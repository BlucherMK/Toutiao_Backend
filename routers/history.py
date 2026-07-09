from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from crud import history
from models.users import User
from schemas.history import HistoryAddRequest
from utils.auth import get_current_user
from utils.response import success_response


router = APIRouter(prefix="/api/history",tags=["history"])

@router.post("/add")
async def add_history(
    data: HistoryAddRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await history.add_news_history(db, user.id, data.news_id)
    return success_response(message="浏览记录添加成功", data=result)

@router.get("list")
async def get_history_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=100, alias="pageSize"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return success_response(message="获取浏览列表成功")