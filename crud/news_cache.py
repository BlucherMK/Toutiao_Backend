# 导入 FastAPI 工具，用于将 SQLAlchemy 对象转换为可以变成 JSON 的安全字典格式
# Import FastAPI tool to convert SQLAlchemy objects into JSON-serializable dictionaries
from fastapi.encoders import jsonable_encoder

# 导入 SQLAlchemy 的聚合函数 (如 count)、查询 (select) 和更新 (update) 操作
# Import SQLAlchemy aggregation function (like count), select, and update operations
from sqlalchemy import func, select, update

# 导入异步数据库会话类型，用于类型提示
# Import AsyncSession type for database type hinting
from sqlalchemy.ext.asyncio import AsyncSession

# 导入我们自己写的缓存操作函数（获取和设置新闻列表、分类）
# Import custom cache operation functions (get and set news list, categories)
from cache.news_cache import get_cache_news_list, get_cache_categories, set_cache_categories, set_cache_news_list

# 导入数据库对应的实体模型：新闻分类 (Category) 和 新闻本身 (News)
# Import corresponding database entity models: Category and News
from models.news import Category, News

# 导入 Pydantic 模型，用于数据验证和格式化输出
# Import Pydantic model for data validation and formatting output
from schemas.base import NewsItemBase


# ==========================================
# 获取新闻分类列表 (Get Category List)
# ==========================================

# 定义异步函数获取分类，db是数据库连接，skip是跳过多少条，limit是最多拿多少条
# Define async function to get categories, db is connection, skip is offset, limit is max records
async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    
    # 尝试调用缓存函数，去 Redis 里面找有没有分类数据
    # Try to call the cache function to find category data in Redis
    cached_categories = await get_cache_categories()
    
    # 如果在缓存里找到了数据（不是 None）
    # If data is found in cache (not None)
    if cached_categories:
        # 直接把缓存里的数据丢给前端，后面的数据库操作全都不执行了
        # Directly return cached data to frontend, skipping all subsequent DB operations
        return cached_categories
    
    # 如果缓存里没有，就组装一条 SQL 查询语句：去 Category 表查，跳过 skip 条，拿 limit 条
    # If not in cache, build a SQL query: select from Category table, offset by skip, limit by limit
    stmt = select(Category).offset(skip).limit(limit)
    
    # 让数据库去真正执行这条 SQL 语句
    # Let the database actually execute this SQL statement
    result = await db.execute(stmt)
    
    # 把查出来的结果全部提取出来，变成一个 Python 列表
    # Extract all queried results and convert them into a Python list
    categories =  result.scalars().all()

    # 如果从数据库里查到了分类数据（列表不为空）
    # If category data was found in the database (list is not empty)
    if categories:
        # 把复杂的 SQLAlchemy 对象列表，转换成基础的字典列表，防止存 JSON 时报错
        # Convert complex SQLAlchemy object list into basic dict list to prevent JSON serialization errors
        categories = jsonable_encoder(categories)
        
        # 把转换好的数据存进 Redis 缓存里，方便下次直接用
        # Save the converted data into Redis cache for direct use next time
        await set_cache_categories(categories)

    # 最后把分类数据返回给上一层（Router）
    # Finally, return the category data to the upper layer (Router)
    return categories


# ==========================================
# 获取分类下的新闻列表 (Get News List by Category)
# ==========================================

# 定义异步函数获取新闻列表，需要指定分类 category_id
# Define async function to get news list, requiring category_id
async def get_news_list(db:AsyncSession, category_id: int, skip: int = 0, limit: int = 10):
    
    # 根据前端传来的 skip(偏移量) 和 limit(每页数量)，计算出当前是第几页 (page)
    # Calculate current page number based on skip (offset) and limit (items per page)
    page = skip // limit + 1
    
    # 拿着 分类ID、页码、每页数量 去 Redis 里拿对应的缓存
    # Fetch corresponding cache from Redis using category_id, page, and limit
    cached_list = await get_cache_news_list(category_id, page, limit)
    
    # 如果缓存里有数据
    # If there is data in the cache
    if cached_list:
        # 因为缓存里拿出来的是字典，这里用 News(**item) 把字典重新拼装成 SQLAlchemy 的 News 对象格式并返回
        # Since cache returns dicts, use News(**item) to reconstruct them into SQLAlchemy News objects and return
        return [News(**item) for item in cached_list]
    
    # 如果没缓存，准备 SQL：查 News 表，条件是 category_id 相等，然后分页
    # If no cache, prepare SQL: select from News where category_id matches, with pagination
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    
    # 执行查询
    # Execute the query
    result = await db.execute(stmt)
    
    # 取出所有新闻对象，变成列表
    # Extract all news objects into a list
    news_list =  result.scalars().all()

    # 如果查到了新闻数据
    # If news data was found
    if news_list: 
        # 遍历新闻列表，用 Pydantic 模型 (NewsItemBase) 过滤掉不需要的字段，然后转成字典格式 (.model_dump)
        # Iterate news list, use Pydantic model to filter fields, and convert to dict format (.model_dump)
        news_data = [NewsItemBase.model_validate(item).model_dump(mode="json", by_alias=False) for item in news_list]
        
        # 把处理好的字典数据存进 Redis，钥匙由 分类ID、页码和条数共同决定
        # Save the processed dict data to Redis, key is determined by category_id, page, and limit
        await set_cache_news_list(category_id, page, limit, news_data)
        
    # 返回原始的新闻对象列表给上一层
    # Return the original news object list to the upper layer
    return news_list


# ==========================================
# 获取某个分类下有多少条新闻总数 (Get Total News Count)
# ==========================================

# 定义异步函数获取新闻总数
# Define async function to get total news count
async def get_news_count(db: AsyncSession, category_id: int):
    
    # 准备 SQL：使用 func.count 统计 News.id 的数量，条件是该分类
    # Prepare SQL: use func.count to count News.id where category matches
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    
    # 执行查询
    # Execute the query
    result = await db.execute(stmt)
    
    # 提取唯一的标量结果（因为 count() 只会返回一个数字），然后返回它
    # Extract the single scalar result (since count() returns one number) and return it
    return result.scalar_one()


# ==========================================
# 获取单条新闻详情 (Get News Detail)
# ==========================================

# 定义异步函数获取单篇新闻的详细内容
# Define async function to get the detail of a single news article
async def get_news_detail(db: AsyncSession, news_id: int):
    
    # 准备 SQL：查 News 表，找 id 匹配的那一条
    # Prepare SQL: select from News where id matches
    stmt = select(News).where(News.id == news_id)
    
    # 执行查询
    # Execute the query
    result = await db.execute(stmt)
    
    # 获取这唯一的一条数据，如果找不到不会报错，而是返回 None
    # Get this exact one record, return None instead of throwing error if not found
    return result.scalar_one_or_none()


# ==========================================
# 增加新闻阅读量 (Increase News Views)
# ==========================================

# 定义异步函数增加阅读量
# Define async function to increase view count
async def increase_news_views(db: AsyncSession, news_id: int):
    
    # 准备 SQL：更新 News 表匹配 id 的记录，把 views 字段设置为 原来的views + 1
    # Prepare SQL: update News table matching id, set views field to original views + 1
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    
    # 执行这条更新语句
    # Execute this update statement
    result = await db.execute(stmt)
    
    # await db.commit()  # 🚨 注意：这里被注释掉了。如果要真正保存到 MySQL，必须执行 commit。
    # await db.commit()  # 🚨 Note: This is commented out. To save to MySQL, commit must be executed.

    # 如果受影响的行数大于 0 (更新成功)，返回 True，否则返回 False
    # If affected rows > 0 (update successful), return True, else return False
    return result.rowcount > 0


# ==========================================
# 获取相关推荐新闻 (Get Related News)
# ==========================================

# 定义异步函数获取相关新闻，默认拿 5 条
# Define async function to get related news, default limit is 5
async def get_related_news(db:AsyncSession, news_id:int, category_id: int, limit: int = 5):
    
    # 准备 SQL：查询 News 表
    # Prepare SQL: query News table
    stmt = select(News).where(
        News.category_id == category_id,  # 条件1：必须是同一个分类 (Condition 1: same category)
        News.id != news_id                # 条件2：不能是当前这篇新闻自己 (Condition 2: exclude current news)
    ).order_by(
        News.views.desc(),                # 排序1：按阅读量从高到低排 (Sort 1: highest views first)
        News.publish_time.desc()          # 排序2：如果阅读量一样，按发布时间最新排 (Sort 2: newest publish time first)
    ).limit(limit)                        # 限制只拿 limit 条 (Limit to specific count)
    
    # 执行查询
    # Execute the query
    result = await db.execute(stmt)
    
    # 把查出的新闻对象提取成列表
    # Extract the queried news objects into a list
    related_news = result.scalars().all()
    
    # 遍历查出的新闻对象，手动组装成包含特定字段的字典列表并返回（注意这里把 views 映射成了 view）
    # Iterate news objects, manually build and return a dict list with specific fields (Note: 'views' is mapped to 'view')
    return [{
        "id": news_detail.id,
        "title": news_detail.title,
        "content":  news_detail.content,
        "image": news_detail.image,
        "author":news_detail.author,
        "publishTime": news_detail.publish_time,
        "categoryId": news_detail.category_id,
        "view": news_detail.views,
    } for news_detail in related_news]