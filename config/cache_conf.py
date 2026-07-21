# ==========================================
# Redis 底层连接与通用操作封装
# Redis Base Connection and Generic Operations
# ==========================================

# 导入内置的 json 库，用于处理字典/列表与字符串之间的互相转换 (序列化与反序列化)
# Import built-in json library for converting between dicts/lists and strings (serialization/deserialization)
import json

# 导入 Any 类型提示，表示变量可以是任何数据类型
# Import Any for type hinting, indicating a variable can be of any data type
from typing import Any

# 导入 Redis 的异步驱动包，保证在 FastAPI 中进行数据库操作时不会阻塞主线程
# Import the async Redis driver to ensure DB operations don't block the main thread in FastAPI
import redis.asyncio as redis

# ==========================================
# Redis 连接配置常量 (Redis Connection Config)
# ==========================================

# 定义 Redis 服务端所在的主机地址（本地运行即为 localhost 或 127.0.0.1）
# Define the host address where the Redis server is running
REDIS_HOST="localhost"

# 定义 Redis 服务的监听端口（默认是 6379）
# Define the port Redis is listening on (default is 6379)
REDIS_PORT= 6379

# 定义使用的 Redis 数据库编号（Redis 默认提供 0-15 号共 16 个数据库，这里选第一个）
# Define the Redis database number to use (Redis defaults to 16 DBs from 0-15, selecting the first one)
REDIS_DB = 0


# ==========================================
# 实例化 Redis 连接客户端 (Instantiate Redis Client)
# ==========================================

# 创建一个全局的 Redis 连接对象，FastAPI 的所有路由都可以复用这个管道
# Create a global Redis connection object that all FastAPI routes can reuse
redis_client = redis.Redis(
    host=REDIS_HOST,         # 主机地址 (Host address)
    port=REDIS_PORT,         # 端口号 (Port number)
    db=REDIS_DB,             # 数据库编号 (Database index)
    
    # 极其重要：将 Redis 底层的字节流 (b'xxx') 自动解码为 Python 标准的字符串 (str)
    # Crucial: Automatically decodes raw Redis byte streams (b'xxx') into standard Python strings (str)
    decode_responses=True    
)


# ==========================================
# 读取纯文本缓存 (Read String Cache)
# ==========================================

# 异步函数：获取普通字符串缓存
# Async function: Get basic string cache
async def get_cache(key: str):
    try:
        # 使用传入的 key 去 Redis 中取值并直接返回
        # Fetch the value from Redis using the provided key and return it directly
        return await redis_client.get(key)
    
    except Exception as e:
        # 如果 Redis 服务宕机或网络异常，捕获错误并打印，防止整个后台崩溃
        # Catch and print errors if Redis is down or network fails, preventing backend crash
        print(f"获取缓存失败{e}")
        
        # 异常情况下返回 None，让业务代码继续去查 MySQL 兜底
        # Return None on exception, allowing business logic to fallback to querying MySQL
        return None
    

# ==========================================
# 读取复杂数据结构缓存 (Read JSON Cache)
# ==========================================

# 异步函数：获取并解析列表或字典格式的缓存
# Async function: Get and parse cache stored as list or dict format
async def get_json_cache(key: str):
    try:
        # 第一步：先像拿普通文本一样，把 JSON 格式的字符串拿出来
        # Step 1: Fetch the JSON-formatted string just like basic text
        data = await redis_client.get(key)
        
        # 如果确实拿到了数据（且不是 None）
        # If data was successfully retrieved (and is not None)
        if data:
            # 使用 json.loads 将字符串“反序列化”成 Python 的字典或列表并返回
            # Deserialize the string back into a Python dict or list using json.loads and return it
            return json.loads(data)
            
        # 如果键不存在或已过期，返回 None
        # Return None if the key doesn't exist or has expired
        return None
        
    except Exception as e:
        # 捕获读取异常（包括 JSON 解析失败的异常）
        # Catch fetch exceptions (including JSON parsing failures)
        print(f"获取JSON缓存失败{e}")
        return None


# ==========================================
# 写入缓存数据 (Write Cache Data)
# ==========================================

# 异步函数：设置缓存。带有超时机制，默认为 3600 秒（1小时）
# Async function: Set cache with an expiration mechanism, default is 3600 seconds (1 hour)
async def set_cache(key: str, value: Any, expire: int = 3600):
    try:
        # 检查警察：判断准备存入的数据是不是字典 (dict) 或列表 (list)
        # Type checker: Determine if the incoming data is a dictionary or list
        if isinstance(value, (dict, list)):
            
            # 如果是，就必须用 json.dumps 将其“序列化”成字符串，并且确保中文不乱码
            # If so, serialize it into a string using json.dumps, ensuring Chinese characters stay intact
            value = json.dumps(value, ensure_ascii=False)
            
        # 调用 Redis 的 setex 命令：一步到位设置 Key、过期时间(expire) 和 值(value)
        # Call Redis setex command: Set Key, expiration time, and value all in one step
        await redis_client.setex(key, expire, value)
        
        # 存入成功，返回 True
        # Save successful, return True
        return True
        
    except Exception as e:
        # 如果存入过程发生错误（比如 Redis 内存满了），打印错误并返回 False
        # If an error occurs during saving (e.g., Redis OOM), print error and return False
        print(f"设置缓存失败:{e}")
        return False