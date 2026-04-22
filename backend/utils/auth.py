from typing import Callable

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from mapper import rbacMapper, userMapper
from schema.userSchema import CurrentUserResponse
from service import userService

bearer_scheme = HTTPBearer(auto_error=False)

"""
获取当前用户
"""
async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> CurrentUserResponse:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="缺少或无效的认证信息")
    token = credentials.credentials
    try:
        payload = userService.decode_token(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    if payload.get("token_type") != "access":
        raise HTTPException(status_code=401, detail="token类型错误")
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="token缺少用户标识")
    user_id = int(sub)
    user = await userMapper.get_user_by_id(db, user_id)
    if not user or user.is_active != 1:
        raise HTTPException(status_code=401, detail="用户不存在或已禁用")
    token_perm_version = payload.get("perm_version")
    if token_perm_version is None:
        raise HTTPException(status_code=401, detail="token权限版本无效，请重新登录")
    current_perm_version = await userMapper.get_user_perm_version(db, user_id)
    if int(token_perm_version) != current_perm_version:
        raise HTTPException(status_code=401, detail="登录状态已变更，请重新登录")
    roles = await rbacMapper.get_user_roles(db, user.id)
    permissions = await rbacMapper.get_user_permissions(db, user.id)
    return CurrentUserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        roles=roles,
        permissions=permissions,
    )


"""
权限检查
"""
def require_permission(permission_code: str) -> Callable:
    async def _check(current_user: CurrentUserResponse = Depends(get_current_user)) -> CurrentUserResponse:
        if "admin" in current_user.roles:
            return current_user
        if permission_code not in current_user.permissions:
            raise HTTPException(status_code=403, detail=f"缺少权限: {permission_code}")
        return current_user

    return _check
