from fastapi import APIRouter

#创建 APIRouter 实例
#prefix 路由前缀
#tags 分组，标签
router = APIRouter(prefix="/api/users",tags=["users"])

@router.get("/setting")
async def get_categories():
    return{"msg":"获取设置成功"}