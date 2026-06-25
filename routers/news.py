from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from crud import news

# 创建 APIRouter 实例 / Create APIRouter instance
# prefix: 路由统一前缀 / Unified route prefix
# tags: 接口分组标签（用于 Swagger UI 归类） / Group tags (used for categorization in Swagger UI)
router = APIRouter(prefix="/api/news", tags=["news"])

"""
接口实现标准流程 / Standard process for API implementation:
1. 模块化路由 / Modularize routing
2. 定义模型类 -> 映射数据库表 / Define Model classes -> Map to database tables
3. 在 crud 文件夹封装数据库操作方法 / Encapsulate database operations in the 'crud' directory
4. 在路由处理函数中调用 crud 方法并返回响应结果 / Call crud methods in route handlers and return responses
"""

@router.get("/categories")
async def get_categories(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    # 调用 CRUD 方法获取分类数据 / Call CRUD method to fetch category data
    # 获取新闻分类列表 / Get the list of news categories
    # - skip: 跳过的记录数（用于基础分页） / Number of records to skip (for basic pagination)
    # - limit: 最大返回数量 / Maximum number of records to return
    categories = await news.get_categories(db, skip, limit)
    
    # 构造并返回标准 JSON 响应 / Construct and return standard JSON response
    return {
        "code": 200,
        "message": "success",
        "data": categories
    }

@router.get("/list")
async def get_news_list(
    category_id: int = Query(..., alias="categoryId"), page: int = 1, page_size: int = Query(default=10, ge=1, le=100), db: AsyncSession = Depends(get_db)
    # 使用 alias 适配前端的驼峰命名 (categoryId)，后端仍使用下划线命名 (category_id) / Use alias to adapt to frontend's camelCase (categoryId), while backend uses snake_case (category_id)
    # 当前页码，默认第一页 / Current page number, defaults to page 1
    # 每页数据量，设置默认值并限制范围（大于等于1，小于等于100）/ Page size, with default value and constraints (greater than/equal to 1, less than/equal to 100)
    # 依赖注入获取数据库连接 / Dependency injection to get database session
):
    # 计算数据库查询的偏移量 / Calculate the offset for database query
    offset = (page - 1) * page_size
    
    # 查询当前页的新闻数据 / Query news data for the current page
    news_list = await news.get_news_list(db, category_id, offset, page_size)
    
    # 返回带有分页信息的复杂响应对象 / Return complex response object with pagination info
    return {
        "code": 200,
        "message": "success",
        "data": {
            "list": news_list,
            
            "total": "total_count", 
            
            "hasMore": "has_more" 
        }
    }