from fastapi import APIRouter

#创建 APIRouter 实例
router = APIRouter(prefix="/api/news",tags=["news"])

@router.get("/catagories")
async def get_catagories():
    return{"msg":"获取分类成功"}