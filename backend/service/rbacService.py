from sqlalchemy.ext.asyncio import AsyncSession

from mapper import rbacMapper, userMapper
from schema.rbacSchema import (
    PermissionResponse,
    RoleCreateRequest,
    RoleResponse,
    RoleUpdateRequest,
    UserRolePermissionResponse,
)


async def list_roles(db: AsyncSession):
    result = await rbacMapper.list_roles(db)
    return [RoleResponse.model_validate(item) for item in result]


async def create_role(db: AsyncSession, role_data: RoleCreateRequest):
    exists = await rbacMapper.get_role_by_code(db, role_data.code)
    if exists:
        raise ValueError(f"角色编码 {role_data.code} 已存在")
    result = await rbacMapper.create_role(db, role_data.name, role_data.code, role_data.description)
    return RoleResponse.model_validate(result)


async def update_role(db: AsyncSession, role_data: RoleUpdateRequest):
    exists = await rbacMapper.get_role_by_id(db, role_data.role_id)
    if not exists:
        raise ValueError(f"角色ID {role_data.role_id} 不存在")
    result = await rbacMapper.update_role(
        db,
        role_id=role_data.role_id,
        name=role_data.name,
        description=role_data.description,
    )
    return RoleResponse.model_validate(result)


async def delete_role(db: AsyncSession, role_id: int):
    exists = await rbacMapper.get_role_by_id(db, role_id)
    if not exists:
        raise ValueError(f"角色ID {role_id} 不存在")
    return await rbacMapper.soft_delete_role(db, role_id)


async def list_permissions(db: AsyncSession):
    result = await rbacMapper.list_permissions(db)
    return [PermissionResponse.model_validate(item) for item in result]


async def bind_user_roles(db: AsyncSession, user_id: int, role_ids: list[int]):
    user = await userMapper.get_user_by_id(db, user_id)
    if not user:
        raise ValueError(f"用户ID {user_id} 不存在")
    await rbacMapper.replace_user_roles(db, user_id=user_id, role_ids=role_ids)
    return True


async def bind_role_permissions(db: AsyncSession, role_id: int, permission_ids: list[int]):
    role = await rbacMapper.get_role_by_id(db, role_id)
    if not role:
        raise ValueError(f"角色ID {role_id} 不存在")
    await rbacMapper.replace_role_permissions(db, role_id=role_id, permission_ids=permission_ids)
    return True


async def get_user_role_permission(db: AsyncSession, user_id: int):
    user = await userMapper.get_user_by_id(db, user_id)
    if not user:
        raise ValueError(f"用户ID {user_id} 不存在")
    roles = await rbacMapper.get_user_roles(db, user_id)
    permissions = await rbacMapper.get_user_permissions(db, user_id)
    return UserRolePermissionResponse(
        user_id=user.id,
        username=user.username,
        roles=roles,
        permissions=permissions,
    )
