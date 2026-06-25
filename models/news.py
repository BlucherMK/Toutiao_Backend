from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
# 所有数据库模型的基类 / Base class for all database models
class Base(DeclarativeBase):
    
    # 创建时间，默认值为当前时间 / Creation time, defaults to current time
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.now, 
        comment="创建时间 / Creation time"
    )
    
    # 更新时间，每次更新记录时自动修改为当前时间
    # Update time, automatically updated to current time whenever the record is updated
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.now, 
        onupdate=datetime.now, 
        comment="更新时间 / Update time"
    )
    
class Category(Base):
    # 指定数据库中的表名 / Specify the physical table name in the database
    __tablename__ = "news_category"

    # 分类ID，主键且自动递增 / Category ID, Primary Key and Auto-incremented
    # 分类名称，字符串长度50，唯一且不能为空 / Category name, String length 50, Unique and Not Null
    # 排序权重，默认值为0 / Sort order weight, defaults to 0
    # 注意：已将 Mapped[str] 修正为 Mapped[int] / Note: Fixed Mapped[str] to Mapped[int]
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="分类ID / Category ID")
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="分类名称 / Category Name")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="排序 / Sort Order")

    def __repr__(self):
        # 用于在控制台打印对象时显示友好信息 / User-friendly string representation for console debugging
        return f"<Category(id={self.id}, name={self.name}, sort_order={self.sort_order})>"
    
class News(Base):
    __tablename__ = "news"

    # 创建索引：提升查询速度 → 相当于添加目录 
    # Create indexes: Improve query speed → Like adding a table of contents for the database
    __table_args__ = (
        # 针对分类ID建立索引，优化高频查询场景 / Create index on category_id, optimizing high-frequency queries
        Index('fk_news_category_idx', 'category_id'),  
        # 针对发布时间建立索引，优化按发布时间排序的查询 / Create index on publish_time, optimizing chronological sorting
        Index('idx_publish_time', 'publish_time')  
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="新闻ID / News ID")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="新闻标题 / News Title")
    
    # 新闻简介，Optional 表示允许为空 (NULL) / News description, Optional means it can be NULL
    # 新闻正文内容，Text 类型适合存储超长文本 / News main content, Text type is suitable for massive string payloads
    # 封面图片URL，允许为空 / Cover image URL, nullable
    # 外键约束，关联到 news_category 表的 id 字段 / Foreign Key constraint, linked to the 'id' field of 'news_category' table
    # 浏览量，默认值为0 / View count, defaults to 0
    # 发布时间，默认值为当前时间 / Publish time, defaults to current time
    description: Mapped[Optional[str]] = mapped_column(String(500), comment="新闻简介 / News Description")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="新闻内容 / News Content")
    image: Mapped[Optional[str]] = mapped_column(String(255), comment="封面图片URL / Cover Image URL")
    author: Mapped[Optional[str]] = mapped_column(String(50), comment="作者 / Author")
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('news_category.id'), nullable=False, comment="分类ID / Category ID")
    views: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="浏览量 / Views")
    publish_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="发布时间 / Publish Time")

    def __repr__(self):
        return f"<News(id={self.id}, title='{self.title}', views={self.views})>"