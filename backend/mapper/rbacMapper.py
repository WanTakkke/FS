from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def list_roles(db: AsyncSession):
    result = await db.execute(
        text(
            """
            SELECT id, name, code, description
            FROM sys_role
            WHERE deleted_at IS NULL
            ORDER BY id DESC
            """
        )
    )
    return result.mappings().all()


async def get_role_by_id(db: AsyncSession, role_id: int):
    result = await db.execute(
        text(
            """
            SELECT id, name, code, description
            FROM sys_role
            WHERE id = :role_id AND deleted_at IS NULL
            """
        ),
        {"role_id": role_id},
    )
    return result.mappings().first()


async def get_role_by_code(db: AsyncSession, code: str):
    result = await db.execute(
        text(
            """
            SELECT id, name, code, description
            FROM sys_role
            WHERE code = :code AND deleted_at IS NULL
            """
        ),
        {"code": code},
    )
    return result.mappings().first()


async def create_role(db: AsyncSession, name: str, code: str, description: str | None):
    await db.execute(
        text(
            """
            INSERT INTO sys_role(name, code, description, created_at, updated_at, deleted_at)
            VALUES(:name, :code, :description, NOW(), NOW(), NULL)
            """
        ),
        {"name": name, "code": code, "description": description},
    )
    await db.commit()
    return await get_role_by_code(db, code)


async def update_role(db: AsyncSession, role_id: int, name: str | None, description: str | None):
    updates: list[str] = []
    params: dict[str, object] = {"role_id": role_id}
    if name is not None:
        updates.append("name = :name")
        params["name"] = name
    if description is not None:
        updates.append("description = :description")
        params["description"] = description
    if not updates:
        return await get_role_by_id(db, role_id)
    updates.append("updated_at = NOW()")
    sql = f"UPDATE sys_role SET {', '.join(updates)} WHERE id = :role_id AND deleted_at IS NULL"
    await db.execute(text(sql), params)
    await db.commit()
    return await get_role_by_id(db, role_id)


async def soft_delete_role(db: AsyncSession, role_id: int):
    await db.execute(
        text(
            """
            UPDATE sys_role
            SET deleted_at = NOW(), updated_at = NOW()
            WHERE id = :role_id AND deleted_at IS NULL
            """
        ),
        {"role_id": role_id},
    )
    await db.execute(text("DELETE FROM sys_user_role WHERE role_id = :role_id"), {"role_id": role_id})
    await db.execute(text("DELETE FROM sys_role_permission WHERE role_id = :role_id"), {"role_id": role_id})
    await db.commit()
    return True


async def list_permissions(db: AsyncSession):
    result = await db.execute(
        text(
            """
            SELECT id, parent_id, name, code, type
            FROM sys_permission
            WHERE deleted_at IS NULL
            ORDER BY id ASC
            """
        )
    )
    return result.mappings().all()


async def get_user_roles(db: AsyncSession, user_id: int):
    result = await db.execute(
        text(
            """
            SELECT r.code
            FROM sys_role r
            JOIN sys_user_role ur ON ur.role_id = r.id
            WHERE ur.user_id = :user_id
              AND r.deleted_at IS NULL
            ORDER BY r.id ASC
            """
        ),
        {"user_id": user_id},
    )
    return [row[0] for row in result.all()]


async def get_user_permissions(db: AsyncSession, user_id: int):
    result = await db.execute(
        text(
            """
            SELECT DISTINCT p.code
            FROM sys_permission p
            JOIN sys_role_permission rp ON rp.permission_id = p.id
            JOIN sys_user_role ur ON ur.role_id = rp.role_id
            JOIN sys_role r ON r.id = ur.role_id
            WHERE ur.user_id = :user_id
              AND p.deleted_at IS NULL
              AND r.deleted_at IS NULL
            ORDER BY p.code ASC
            """
        ),
        {"user_id": user_id},
    )
    return [row[0] for row in result.all()]


async def replace_user_roles(db: AsyncSession, user_id: int, role_ids: list[int]):
    await db.execute(text("DELETE FROM sys_user_role WHERE user_id = :user_id"), {"user_id": user_id})
    for role_id in role_ids:
        await db.execute(
            text(
                """
                INSERT INTO sys_user_role(user_id, role_id, created_at)
                VALUES(:user_id, :role_id, NOW())
                """
            ),
            {"user_id": user_id, "role_id": role_id},
        )
    await db.commit()


async def replace_role_permissions(db: AsyncSession, role_id: int, permission_ids: list[int]):
    await db.execute(text("DELETE FROM sys_role_permission WHERE role_id = :role_id"), {"role_id": role_id})
    for permission_id in permission_ids:
        await db.execute(
            text(
                """
                INSERT INTO sys_role_permission(role_id, permission_id, created_at)
                VALUES(:role_id, :permission_id, NOW())
                """
            ),
            {"role_id": role_id, "permission_id": permission_id},
        )
    await db.commit()


async def list_user_ids_by_role(db: AsyncSession, role_id: int) -> list[int]:
    result = await db.execute(
        text(
            """
            SELECT DISTINCT ur.user_id
            FROM sys_user_role ur
            JOIN sys_user u ON u.id = ur.user_id
            WHERE ur.role_id = :role_id AND u.deleted_at IS NULL
            """
        ),
        {"role_id": role_id},
    )
    return [int(row[0]) for row in result.all()]


async def count_active_users_by_role(db: AsyncSession, role_id: int) -> int:
    result = await db.execute(
        text(
            """
            SELECT COUNT(DISTINCT ur.user_id)
            FROM sys_user_role ur
            JOIN sys_user u ON u.id = ur.user_id
            WHERE ur.role_id = :role_id
              AND u.deleted_at IS NULL
              AND u.is_active = 1
            """
        ),
        {"role_id": role_id},
    )
    return int(result.scalar_one() or 0)


async def user_has_role(db: AsyncSession, user_id: int, role_id: int) -> bool:
    result = await db.execute(
        text(
            """
            SELECT 1
            FROM sys_user_role
            WHERE user_id = :user_id AND role_id = :role_id
            LIMIT 1
            """
        ),
        {"user_id": user_id, "role_id": role_id},
    )
    return result.scalar_one_or_none() is not None


async def create_audit_log(
    db: AsyncSession,
    module: str,
    action: str,
    operator_id: int | None,
    operator_username: str,
    target_type: str,
    target_id: str,
    detail_json: str | None = None,
) -> None:
    await db.execute(
        text(
            """
            INSERT INTO sys_audit_log(
                module, action, operator_id, operator_username, target_type, target_id, detail_json, created_at
            )
            VALUES(:module, :action, :operator_id, :operator_username, :target_type, :target_id, :detail_json, NOW())
            """
        ),
        {
            "module": module,
            "action": action,
            "operator_id": operator_id,
            "operator_username": operator_username,
            "target_type": target_type,
            "target_id": target_id,
            "detail_json": detail_json,
        },
    )
    await db.commit()
