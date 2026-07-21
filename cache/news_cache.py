# 导入类型提示工具，用于规范变量和函数的出入参类型，让代码更严谨、VS Code 提示更智能
# Import type hinting tools to strictly define variable/function types, improving code robustness and VS Code intellisense
from typing import Any, Dict, List, Optional
# 导入我们之前在配置文件（cache_conf）里写好的、负责跟 Redis 打交道的底层存取函数
# Import the base fetch/store functions configured earlier that directly interact with Redis
from config.cache_conf import get_json_cache, set_cache
# 定义新闻分类的固定缓存键名（Key）。在 Redis 中，使用冒号 (:) 可以像文件夹一样清晰地划分层级
# Define the fixed cache key for news categories. In Redis, colons (:) are used to separate namespaces logically like folders
CATEGORIES_KEY = "news:categories"
# 定义新闻列表的缓存键前缀。因为列表数据千变万化，我们需要在代码里动态拼接后面的后缀
# Define the cache key prefix for the news list. Since list data varies, we will dynamically append suffixes in the code
NEWS_LIST_PREFIX = "news_list:"

# 定义异步函数，专门用来从 Redis 读取新闻分类数据
# Define async function dedicated to fetching news category data from Redis
async def get_cache_categories():
    # 直接拿着固定的分类 Key 去底层函数取数据并返回（如果 Redis 里没有，底层会返回 None）
    # Pass the fixed category Key to the base layer to fetch data (returns None if not found in Redis)
    return await get_json_cache(CATEGORIES_KEY)

# 定义写入分类缓存的函数。
# Define the function for writing to the category cache.
async def set_cache_categories(data: List[Dict[str, Any]], expire: int = 7200):
    # 调用底层封装的 set_cache 函数，把分类数据存进 Redis
    # Call the encapsulated base function to save category data into Redis
    return await set_cache(CATEGORIES_KEY, data, expire)

# 定义写入新闻列表缓存的函数。
# Define function to save news list. 
# Optional[int] 表示 category_id 可以是整数，也可以是空值.新闻列表默认半小时(1800秒)过期。
# Optional[int] means category_id can be an int or None Default expiration is 30 mins (1800s).
async def set_cache_news_list(category_id: Optional[int], page: int, size: int, news_list: List[Dict[str, Any]], expire: int = 1800):
    
    # 组装动态 Key 步骤1：如果传了分类 ID 就用该 ID；如果传了 None（代表看首页全部新闻），就用 "all" 代替
    # Dynamic Key Step 1: Use category_id if provided; if None (meaning viewing all news), use "all" instead
    category_part = category_id if category_id is not None else "all"
    
    # 组装动态 Key 步骤2：利用 f-string 把前缀、分类、页码、每页数量无缝拼接。例如拼成: "news_list:1:2:10"
    # Dynamic Key Step 2: Use f-string to concatenate prefix, category, page, and size. E.g., "news_list:1:2:10"
    key = f"{NEWS_LIST_PREFIX}{category_part}:{page}:{size}"
    
    # 把这把独一无二的专属钥匙(key)、新闻数据、以及过期时间一起存进 Redis
    # Save this unique Key, the news data, and the expiration time into Redis
    return await set_cache(key, news_list, expire)


# 定义读取新闻列表缓存的函数。入参必须跟存入时完全一致，这样才能“仿制”出同一把钥匙去开锁
# Define function to fetch news list. Inputs must exactly match the setting function to recreate the exact same key
async def get_cache_news_list(category_id: Optional[int], page: int, size: int):
    
    # 再次执行相同的逻辑，还原当时存数据时的那个 "all" 或者 具体分类ID
    # Re-execute the same logic to reproduce the "all" or specific category ID used during saving
    category_part = category_id if category_id is not None else "all"
    
    # 再次精准地拼接出那把专属钥匙
    # Accurately reconstruct that unique key again
    key = f"{NEWS_LIST_PREFIX}{category_part}:{page}:{size}"
    
    # 拿着这把钥匙，去底层开箱拿数据
    # Take this key to the base layer to open the box and fetch the data
    return await get_json_cache(key)