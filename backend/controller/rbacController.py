from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from schema.rbacSchema import (
    PermissionResponse,
    RoleCreateRequest,
    RolePermissionBindRequest,
    RoleResponse,
    RoleUpdateRequest,
    UserRoleBindRequest,
    UserRolePermissionResponse,
)
from schema.userSchema import CurrentUserResponse
from service import rbacService
from utils.auth import get_current_user, require_permission
from utils.baseResponse import BaseResponse
from utils.logger import AppLogger

rbac_router = APIRouter(prefix="/api/rbac", tags=["RBAC权限管理"])
logger = AppLogger.get_logger(__name__)

@rbac_router.get("/roles", response_model=BaseResponse[List[RoleResponse]], dependencies=[Depends(require_permission("rbac:role:read"))])
async def list_roles(db: AsyncSession = Depends(get_db)):
    """角色列表"""
    result = await rbacService.list_roles(db)
    return BaseResponse.success(data=result)


@rbac_router.post("/roles", response_model=BaseResponse[RoleResponse], dependencies=[Depends(require_permission("rbac:role:create"))])
async def create_role(
    role_data: RoleCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUserResponse = Depends(get_current_user),
):
    """创建角色"""
    try:
        result = await rbacService.create_role(db, role_data, operator=current_user)
        return BaseResponse.success(data=result)
    except ValueError as e:
        logger.warning("创建角色失败: code=%s reason=%s", role_data.code, str(e))
        return BaseResponse.error(code=400, message=str(e))


@rbac_router.post("/roles/update", response_model=BaseResponse[RoleResponse], dependencies=[Depends(require_permission("rbac:role:update"))])
async def update_role(
    role_data: RoleUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUserResponse = Depends(get_current_user),
):
    """更新角色"""
    try:
        result = await rbacService.update_role(db, role_data, operator=current_user)
        return BaseResponse.success(data=result)
    except ValueError as e:
        logger.warning("更新角色失败: role_id=%s reason=%s", role_data.role_id, str(e))
        return BaseResponse.error(code=400, message=str(e))


@rbac_router.delete("/roles/{role_id}", response_model=BaseResponse[bool], dependencies=[Depends(require_permission("rbac:role:delete"))])
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUserResponse = Depends(get_current_user),
):
    """删除角色"""
    try:
        await rbacService.delete_role(db, role_id, operator=current_user)
        return BaseResponse.success()
    except ValueError as e:
        logger.warning("删除角色失败: role_id=%s reason=%s", role_id, str(e))
        return BaseResponse.error(code=400, message=str(e))


@rbac_router.get("/permissions", response_model=BaseResponse[List[PermissionResponse]], dependencies=[Depends(require_permission("rbac:permission:read"))])
async def list_permissions(db: AsyncSession = Depends(get_db)):
    """权限列表"""
    result = await rbacService.list_permissions(db)
    return BaseResponse.success(data=result)


@rbac_router.post("/users/roles", response_model=BaseResponse[bool], dependencies=[Depends(require_permission("rbac:user:bind_role"))])
async def bind_user_roles(
    payload: UserRoleBindRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUserResponse = Depends(get_current_user),
):
    """用户绑定角色"""
    try:
        await rbacService.bind_user_roles(db, payload.user_id, payload.role_ids, operator=current_user)
        return BaseResponse.success()
    except ValueError as e:
        logger.warning("绑定用户角色失败: user_id=%s reason=%s", payload.user_id, str(e))
        return BaseResponse.error(code=400, message=str(e))


@rbac_router.post("/roles/permissions", response_model=BaseResponse[bool], dependencies=[Depends(require_permission("rbac:role:bind_permission"))])
async def bind_role_permissions(
    payload: RolePermissionBindRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUserResponse = Depends(get_current_user),
):
    """角色绑定权限"""
    try:
        await rbacService.bind_role_permissions(db, payload.role_id, payload.permission_ids, operator=current_user)
        return BaseResponse.success()
    except ValueError as e:
        logger.warning("绑定角色权限失败: role_id=%s reason=%s", payload.role_id, str(e))
        return BaseResponse.error(code=400, message=str(e))


@rbac_router.get(
    "/users/{user_id}/permissions",
    response_model=BaseResponse[UserRolePermissionResponse],
    dependencies=[Depends(require_permission("rbac:role:read"))],
)
async def get_user_role_permission(user_id: int, db: AsyncSession = Depends(get_db)):
    """查询用户角色与权限"""
    try:
        result = await rbacService.get_user_role_permission(db, user_id)
        return BaseResponse.success(data=result)
    except ValueError as e:
        logger.warning("查询用户权限失败: user_id=%s reason=%s", user_id, str(e))
        return BaseResponse.error(code=400, message=str(e))
