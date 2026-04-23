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


async def get_user_perm_version(db: AsyncSession, user_id: int) -> int:
    result = await db.execute(
        text(
            """
            SELECT COALESCE(perm_version, 1) AS perm_version
            FROM sys_user
            WHERE id = :user_id AND deleted_at IS NULL
            LIMIT 1
            """
        ),
        {"user_id": user_id},
    )
    row = result.mappings().first()
    if not row:
        raise ValueError("用户不存在")
    return int(row["perm_version"])


async def bump_user_perm_version(db: AsyncSession, user_id: int) -> None:
    await db.execute(
        text(
            """
            UPDATE sys_user
            SET perm_version = COALESCE(perm_version, 1) + 1,
                updated_at = NOW()
            WHERE id = :user_id AND deleted_at IS NULL
            """
        ),
        {"user_id": user_id},
    )
    await db.commit()


async def bump_users_perm_version_by_role(db: AsyncSession, role_id: int) -> None:
    await db.execute(
        text(
            """
            UPDATE sys_user u
            JOIN sys_user_role ur ON ur.user_id = u.id
            SET u.perm_version = COALESCE(u.perm_version, 1) + 1,
                u.updated_at = NOW()
            WHERE ur.role_id = :role_id AND u.deleted_at IS NULL
            """
        ),
        {"role_id": role_id},
    )
    await db.commit()


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


async def list_users(
    db: AsyncSession,
    page: int,
    page_size: int,
    username: str | None = None,
    email: str | None = None,
    is_active: int | None = None,
):
    where_sql = ["deleted_at IS NULL"]
    params: dict[str, object] = {
        "offset": (page - 1) * page_size,
        "page_size": page_size,
    }
    
    if username:
        where_sql.append("username LIKE :username")
        params["username"] = f"%{username}%"
    if email:
        where_sql.append("email LIKE :email")
        params["email"] = f"%{email}%"
    if is_active is not None:
        where_sql.append("is_active = :is_active")
        params["is_active"] = is_active
    
    where_clause = " AND ".join(where_sql)
    count_sql = f"SELECT COUNT(1) FROM sys_user WHERE {where_clause}"
    list_sql = f"""
        SELECT id, username, email, is_active, created_at, updated_at
        FROM sys_user
        WHERE {where_clause}
        ORDER BY id DESC
        LIMIT :offset, :page_size
    """
    
    total_result = await db.execute(text(count_sql), params)
    total = int(total_result.scalar_one() or 0)
    records_result = await db.execute(text(list_sql), params)
    records = records_result.mappings().all()
    return total, records


async def update_user(db: AsyncSession, user_id: int, email: str | None):
    updates: list[str] = []
    params: dict[str, object] = {"user_id": user_id}
    
    if email is not None:
        updates.append("email = :email")
        params["email"] = email
    
    if not updates:
        return await get_user_by_id(db, user_id)
    
    updates.append("updated_at = NOW()")
    sql = f"UPDATE sys_user SET {', '.join(updates)} WHERE id = :user_id AND deleted_at IS NULL"
    await db.execute(text(sql), params)
    await db.commit()
    return await get_user_by_id(db, user_id)


async def update_user_status(db: AsyncSession, user_id: int, is_active: int):
    await db.execute(
        text(
            """
            UPDATE sys_user
            SET is_active = :is_active, updated_at = NOW()
            WHERE id = :user_id AND deleted_at IS NULL
            """
        ),
        {"user_id": user_id, "is_active": is_active},
    )
    await db.commit()
    return await get_user_by_id(db, user_id)


async def update_user_password(db: AsyncSession, user_id: int, hashed_password: str):
    await db.execute(
        text(
            """
            UPDATE sys_user
            SET hashed_password = :hashed_password, updated_at = NOW()
            WHERE id = :user_id AND deleted_at IS NULL
            """
        ),
        {"user_id": user_id, "hashed_password": hashed_password},
    )
    await db.commit()
    return await get_user_by_id(db, user_id)


async def soft_delete_user(db: AsyncSession, user_id: int):
    await db.execute(
        text(
            """
            UPDATE sys_user
            SET deleted_at = NOW(), updated_at = NOW()
            WHERE id = :user_id AND deleted_at IS NULL
            """
        ),
        {"user_id": user_id},
    )
    await db.execute(
        text("DELETE FROM sys_user_role WHERE user_id = :user_id"),
        {"user_id": user_id},
    )
    await db.commit()
    return True
