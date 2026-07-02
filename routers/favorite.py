from fastapi import APIRouter, Depends, Query

from config.db_conf import get_db
from crud import favorite
from models.users import User
from utils.auth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession

from utils.response import success_response


router = APIRouter(prefix="/api/favorite",tags=["favorite"])

@router.get("/check")
async def check_favorite(
    news_id: int = Query(..., alias="newsId"),
    user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    is_favorited = await favorite.is_news_favorite(db, user.id, news_id)
    return success_response(message="检查收藏状态成功")