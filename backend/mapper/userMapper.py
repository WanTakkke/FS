from datetime import datetime, timezone

from sqlalchemy import select, text
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


async def create_refresh_token_record(
    db: AsyncSession,
    token_jti: str,
    user_id: int,
    expires_at: datetime,
) -> None:
    await db.execute(
        text(
            """
            INSERT INTO sys_refresh_token(token_jti, user_id, expires_at, created_at)
            VALUES(:token_jti, :user_id, :expires_at, NOW())
            """
        ),
        {
            "token_jti": token_jti,
            "user_id": user_id,
            "expires_at": expires_at.replace(tzinfo=None),
        },
    )
    await db.commit()


async def get_refresh_token_record(db: AsyncSession, token_jti: str):
    result = await db.execute(
        text(
            """
            SELECT token_jti, user_id, expires_at, revoked_at
            FROM sys_refresh_token
            WHERE token_jti = :token_jti
            LIMIT 1
            """
        ),
        {"token_jti": token_jti},
    )
    return result.mappings().first()


async def revoke_refresh_token(
    db: AsyncSession,
    token_jti: str,
    replaced_by_jti: str | None = None,
) -> None:
    await db.execute(
        text(
            """
            UPDATE sys_refresh_token
            SET revoked_at = NOW(), replaced_by_jti = :replaced_by_jti
            WHERE token_jti = :token_jti AND revoked_at IS NULL
            """
        ),
        {"token_jti": token_jti, "replaced_by_jti": replaced_by_jti},
    )
    await db.commit()


def is_refresh_record_active(record: dict) -> bool:
    if record.get("revoked_at") is not None:
        return False
    expires_at = record.get("expires_at")
    if expires_at is None:
        return False
    return expires_at.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc)
