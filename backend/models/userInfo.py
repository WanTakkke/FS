from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, BigInteger
from sqlalchemy.dialects.mysql import TINYINT


class UserBase(DeclarativeBase):
    pass


class SysUser(UserBase):
    __tablename__ = "sys_user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    username: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, comment="用户名")
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False, comment="密码哈希")
    email: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="邮箱")
    is_active: Mapped[int] = mapped_column(TINYINT, default=1, nullable=False, comment="是否启用: 1-启用, 0-禁用")
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now, comment="更新时间")
    deleted_at: Mapped[datetime | None] = mapped_column(default=None, comment="删除时间")
