from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
#数据库连接字符串 / Database Connection URL
# 告诉 Python 数据库的具体寻址参数 / Specifies the precise addressing parameters for the database:
# mysql: 目标数据库方言 / Target database dialect
# aiomysql: 异步 DBAPI 驱动 / Asynchronous DBAPI driver
# @localhost: 本机地址坐标 / Localhost coordinates
ASYNC_DATABASE_URL = "mysql+aiomysql://root:123456@localhost:3306/news_app?charset=utf8mb4"
#创建异步数据库引擎 / Create Async Database Engine
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo = True,        # 启用 SQL 日志回显监控 / Enable SQL query logging (Echo)
    pool_size = 10,     # 核心连接池容量 / Core connection pool size
    max_overflow = 20   # 最大连接溢出阈值 / Maximum connection overflow threshold
)
# 创建异步会话工厂 / Create Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,      # 绑定至底层引擎 / Bind to the underlying execution engine
    class_=AsyncSession,    # 声明为异步会话上下文 / Declare as an async session context
    expire_on_commit=False  # 禁用提交后隐式过期机制 / Disable implicit expiration on commit
)
# 依赖注入：获取数据库会话 / Dependency Injection: Get DB Session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session               # 挂起并将当前会话注入路由 / Yield session context to the router
            await session.commit()      # 正常执行完毕，提交事务 / Commit transaction on success
        except Exception:
            await session.rollback()    # 捕获异常，执行事务回滚 / Rollback transaction on exception
            raise                       # 抛出异常供全局捕获 / Re-raise the exception for global handling
        finally:
            await session.close()       # 周期结束，释放连接回连接池 / Release connection back to the pool