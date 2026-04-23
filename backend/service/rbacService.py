import json

from sqlalchemy.ext.asyncio import AsyncSession

from mapper import rbacMapper, userMapper
from schema.userSchema import CurrentUserResponse
from schema.rbacSchema import (
    AuditLogItemResponse,
    AuditLogPageResponse,
    PermissionCreateRequest,
    PermissionResponse,
    PermissionUpdateRequest,
    RoleCreateRequest,
    RoleResponse,
    RoleUpdateRequest,
    UserRolePermissionResponse,
)


def _operator_fields(operator: CurrentUserResponse | None) -> tuple[int | None, str]:
    if operator is None:
        return None, "system"
    return operator.id, operator.username


async def list_roles(db: AsyncSession):
    result = await rbacMapper.list_roles(db)
    return [RoleResponse.model_validate(item) for item in result]


async def create_role(db: AsyncSession, role_data: RoleCreateRequest, operator: CurrentUserResponse | None = None):
    exists = await rbacMapper.get_role_by_code(db, role_data.code)
    if exists:
        raise ValueError(f"角色编码 {role_data.code} 已存在")
    result = await rbacMapper.create_role(db, role_data.name, role_data.code, role_data.description)
    operator_id, operator_name = _operator_fields(operator)
    await rbacMapper.create_audit_log(
        db,
        module="rbac",
        action="role.create",
        operator_id=operator_id,
        operator_username=operator_name,
        target_type="role",
        target_id=str(result["id"]),
        detail_json=json.dumps(
            {
                "name": role_data.name,
                "code": role_data.code,
                "description": role_data.description,
            },
            ensure_ascii=False,
        ),
    )
    return RoleResponse.model_validate(result)


async def update_role(db: AsyncSession, role_data: RoleUpdateRequest, operator: CurrentUserResponse | None = None):
    exists = await rbacMapper.get_role_by_id(db, role_data.role_id)
    if not exists:
        raise ValueError(f"角色ID {role_data.role_id} 不存在")
    result = await rbacMapper.update_role(
        db,
        role_id=role_data.role_id,
        name=role_data.name,
        description=role_data.description,
    )
    operator_id, operator_name = _operator_fields(operator)
    await rbacMapper.create_audit_log(
        db,
        module="rbac",
        action="role.update",
        operator_id=operator_id,
        operator_username=operator_name,
        target_type="role",
        target_id=str(role_data.role_id),
        detail_json=json.dumps(
            {
                "name": role_data.name,
                "description": role_data.description,
            },
            ensure_ascii=False,
        ),
    )
    return RoleResponse.model_validate(result)


async def delete_role(db: AsyncSession, role_id: int, operator: CurrentUserResponse | None = None):
    exists = await rbacMapper.get_role_by_id(db, role_id)
    if not exists:
        raise ValueError(f"角色ID {role_id} 不存在")
    if exists["code"] == "admin":
        admin_user_count = await rbacMapper.count_active_users_by_role(db, role_id)
        if admin_user_count > 0:
            raise ValueError("超级管理员角色仍有关联用户，禁止删除")
    affected_user_ids = await rbacMapper.list_user_ids_by_role(db, role_id)
    result = await rbacMapper.soft_delete_role(db, role_id)
    for user_id in affected_user_ids:
        await userMapper.bump_user_perm_version(db, user_id)
    operator_id, operator_name = _operator_fields(operator)
    await rbacMapper.create_audit_log(
        db,
        module="rbac",
        action="role.delete",
        operator_id=operator_id,
        operator_username=operator_name,
        target_type="role",
        target_id=str(role_id),
        detail_json=json.dumps({"deleted": True}, ensure_ascii=False),
    )
    return result


async def list_permissions(db: AsyncSession):
    result = await rbacMapper.list_permissions(db)
    return [PermissionResponse.model_validate(item) for item in result]


async def create_permission(
    db: AsyncSession,
    perm_data: PermissionCreateRequest,
    operator: CurrentUserResponse | None = None,
):
    exists = await rbacMapper.get_permission_by_code(db, perm_data.code)
    if exists:
        raise ValueError(f"权限编码 {perm_data.code} 已存在")
    if perm_data.parent_id is not None:
        parent = await rbacMapper.get_permission_by_id(db, perm_data.parent_id)
        if not parent:
            raise ValueError(f"父权限ID {perm_data.parent_id} 不存在")
    result = await rbacMapper.create_permission(
        db,
        parent_id=perm_data.parent_id,
        name=perm_data.name,
        code=perm_data.code,
        perm_type=perm_data.type,
    )
    operator_id, operator_name = _operator_fields(operator)
    await rbacMapper.create_audit_log(
        db,
        module="rbac",
        action="permission.create",
        operator_id=operator_id,
        operator_username=operator_name,
        target_type="permission",
        target_id=str(result["id"]),
        detail_json=json.dumps(
            {
                "parent_id": perm_data.parent_id,
                "name": perm_data.name,
                "code": perm_data.code,
                "type": perm_data.type,
            },
            ensure_ascii=False,
        ),
    )
    return PermissionResponse.model_validate(result)


async def update_permission(
    db: AsyncSession,
    perm_data: PermissionUpdateRequest,
    operator: CurrentUserResponse | None = None,
):
    exists = await rbacMapper.get_permission_by_id(db, perm_data.permission_id)
    if not exists:
        raise ValueError(f"权限ID {perm_data.permission_id} 不存在")
    if perm_data.parent_id is not None:
        if perm_data.parent_id == perm_data.permission_id:
            raise ValueError("父权限不能是自己")
        parent = await rbacMapper.get_permission_by_id(db, perm_data.parent_id)
        if not parent:
            raise ValueError(f"父权限ID {perm_data.parent_id} 不存在")
    result = await rbacMapper.update_permission(
        db,
        permission_id=perm_data.permission_id,
        parent_id=perm_data.parent_id,
        name=perm_data.name,
        perm_type=perm_data.type,
    )
    operator_id, operator_name = _operator_fields(operator)
    await rbacMapper.create_audit_log(
        db,
        module="rbac",
        action="permission.update",
        operator_id=operator_id,
        operator_username=operator_name,
        target_type="permission",
        target_id=str(perm_data.permission_id),
        detail_json=json.dumps(
            {
                "parent_id": perm_data.parent_id,
                "name": perm_data.name,
                "type": perm_data.type,
            },
            ensure_ascii=False,
        ),
    )
    return PermissionResponse.model_validate(result)


async def delete_permission(db: AsyncSession, permission_id: int, operator: CurrentUserResponse | None = None):
    exists = await rbacMapper.get_permission_by_id(db, permission_id)
    if not exists:
        raise ValueError(f"权限ID {permission_id} 不存在")
    role_count = await rbacMapper.count_roles_by_permission(db, permission_id)
    if role_count > 0:
        raise ValueError(f"该权限已关联 {role_count} 个角色，禁止删除")
    result = await rbacMapper.soft_delete_permission(db, permission_id)
    operator_id, operator_name = _operator_fields(operator)
    await rbacMapper.create_audit_log(
        db,
        module="rbac",
        action="permission.delete",
        operator_id=operator_id,
        operator_username=operator_name,
        target_type="permission",
        target_id=str(permission_id),
        detail_json=json.dumps({"deleted": True}, ensure_ascii=False),
    )
    return result


async def bind_user_roles(
    db: AsyncSession,
    user_id: int,
    role_ids: list[int],
    operator: CurrentUserResponse | None = None,
):
    user = await userMapper.get_user_by_id(db, user_id)
    if not user:
        raise ValueError(f"用户ID {user_id} 不存在")
    admin_role = await rbacMapper.get_role_by_code(db, "admin")
    if admin_role:
        admin_role_id = int(admin_role["id"])
        had_admin_before = await rbacMapper.user_has_role(db, user_id=user_id, role_id=admin_role_id)
        has_admin_after = admin_role_id in role_ids
        if had_admin_before and not has_admin_after:
            if operator and operator.id == user_id:
                raise ValueError("不能移除自己的超级管理员角色")
            active_admin_count = await rbacMapper.count_active_users_by_role(db, admin_role_id)
            if active_admin_count <= 1:
                raise ValueError("系统至少保留1个超级管理员")
    await rbacMapper.replace_user_roles(db, user_id=user_id, role_ids=role_ids)
    await userMapper.bump_user_perm_version(db, user_id)
    operator_id, operator_name = _operator_fields(operator)
    await rbacMapper.create_audit_log(
        db,
        module="rbac",
        action="user.bind_role",
        operator_id=operator_id,
        operator_username=operator_name,
        target_type="user",
        target_id=str(user_id),
        detail_json=json.dumps({"role_ids": role_ids}, ensure_ascii=False),
    )
    return True


async def bind_role_permissions(
    db: AsyncSession,
    role_id: int,
    permission_ids: list[int],
    operator: CurrentUserResponse | None = None,
):
    role = await rbacMapper.get_role_by_id(db, role_id)
    if not role:
        raise ValueError(f"角色ID {role_id} 不存在")
    await rbacMapper.replace_role_permissions(db, role_id=role_id, permission_ids=permission_ids)
    await userMapper.bump_users_perm_version_by_role(db, role_id)
    operator_id, operator_name = _operator_fields(operator)
    await rbacMapper.create_audit_log(
        db,
        module="rbac",
        action="role.bind_permission",
        operator_id=operator_id,
        operator_username=operator_name,
        target_type="role",
        target_id=str(role_id),
        detail_json=json.dumps({"permission_ids": permission_ids}, ensure_ascii=False),
    )
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


async def list_audit_logs(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    module: str | None = None,
    action: str | None = None,
    operator_username: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
):
    if page < 1:
        raise ValueError("page 必须大于等于 1")
    if page_size < 1 or page_size > 200:
        raise ValueError("page_size 必须在 1~200 之间")
    total, records = await rbacMapper.query_audit_logs(
        db=db,
        page=page,
        page_size=page_size,
        module=module,
        action=action,
        operator_username=operator_username,
        start_time=start_time,
        end_time=end_time,
    )
    return AuditLogPageResponse(
        total=total,
        page=page,
        page_size=page_size,
        records=[AuditLogItemResponse.model_validate(item) for item in records],
    )
