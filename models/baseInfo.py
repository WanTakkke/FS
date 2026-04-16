from datetime import datetime
from sqlalchemy import DateTime, SmallInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """公共基类，包含所有表的公共字段"""
    __abstract__ = True  # 标记为抽象类，不会创建对应的数据库表

    is_deleted: Mapped[int] = mapped_column(SmallInteger, default=0, comment="是否删除：0-未删除，1-已删除")
    create_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")
    update_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="更新时间")
