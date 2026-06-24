from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_config import get_db
from crud import news
#创建 APIRouter 实例
#prefix 路由前缀
#tags 分组，标签
router = APIRouter(prefix="/api/news",tags=["news"])

#接口实现流程
#1.模块化路由
#2.定义模型类→数据库表（数据库设计文档）
#3.在crud文件夹里面创建文件，封装操作数据库的方法
#4.在路由处理函数里面调用crud封装好的方法，响应结果
@router.get("/catagories")
async def get_catagories(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    categories = await news.get_catagories(db, skip, limit)
    return{
        "code": 200,
        "message": "success",
        "data": categories
    }
