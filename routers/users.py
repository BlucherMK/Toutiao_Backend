from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.users import UserRequest

from config.db_conf import get_db
from crud import users
#创建 APIRouter 实例
#prefix 路由前缀
#tags 分组，标签
router = APIRouter(prefix="/api/users",tags=["users"])

@router.post("/register")
async def get_categories(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    # 注册逻辑： 验证用户是否存在——创建用户——生成token——响应结果
    existing_user = await users.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "用户已经存在")
    user = await users.create_user(db,user_data)
    token = await users.create_token(db, user.id)
    return{
        "code": 200,
        "message": "注册成功",
        "data":{
            "token": token,
            "userInfo": {
                "id": user.id,
                "username": user_data.username,
                "bio": user.bio,
                "avatar": user.avatar
            }
        }
    } 