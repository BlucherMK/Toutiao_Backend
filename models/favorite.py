

from sqlalchemy import Index, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass

class Favorite(Base):
    __tablename__ = 'favorite'

    __table_args__ = (
        UniqueConstraint('user_id', 'news_id', name='user_news_unique'),
        Index('fk_favorite_idx', 'user_id'),
        Index('fk_favorite_idx', 'news_id'),
    )

    id: Mapped[int] = mapped_column(Integer)