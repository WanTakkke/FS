from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.userInfo import SysUser


async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(
        select(SysUser).where(
            SysUser.username == username,
            SysUser.deleted_at.is_(None)
        )
    )
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user: SysUser):
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(SysUser).where(
            SysUser.id == user_id,
            SysUser.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()
