from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.history import History
from models.news import News


async def add_news_history(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
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