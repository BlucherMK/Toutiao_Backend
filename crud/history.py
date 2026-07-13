from datetime import datetime

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

# 导入浏览记录的数据模型 / Import the data model for History
from models.history import History
from models.news import News

async def add_history(db: AsyncSession, user_id: int, news_id: int):
    query = select(History).where(History.user_id == user_id, History.news_id == news_id)
    result = await db.execute(query)
    existing_history = result.scalar_one_or_none()
    if existing_history:
        existing_history.view_time = datetime.now()
        await db.commit()
        await db.refresh(existing_history)
        return existing_history
    else:
        history = History(user_id=user_id, news_id=news_id)
        db.add(history)
        await db.commit()
        await db.refresh(history)
        return history 


async def get_history_list(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 10
):
    #总量+收藏的新闻列表
    count_query = select(func.count()).where(History.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    #获取收藏列表 - 联表查询 join（）+ 收藏时间排序 +分页limit（）
    #select(查询主题模型类).join(联合查询的模型类, 联合查询的条件)。where().order_by().offset(),limit()
    #别名： Favorite.created_at.label("favorite_time")
    offset = (page - 1)*page_size
    #[
    #   (新闻对象，收藏时间，收藏id)
    #]
    query = (select(News, History.view_time.label("view_time"),History.id.label("history_id"))
             .join(History, History.news_id == News.id)
             .where(History.user_id == user_id)
             .order_by(History.view_time.desc())
             .offset(offset).limit(page_size)
             )
    result = await db.execute(query)
    rows = result.all()
    return rows, total

async def delete_history(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    stmt = delete(History).where(History.user_id == user_id, History.news_id == news_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0 