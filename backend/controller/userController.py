from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from utils.baseResponse import BaseResponse
from config.db_config import get_db
from schema.userSchema import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse,
    RefreshTokenRequest,
    CurrentUserResponse,
    UserUpdateRequest,
    UserStatusUpdateRequest,
    UserPasswordResetRequest,
    UserPageResponse,
)
from service import userService
from mapper import userMapper
from utils.auth import get_current_user, require_permission
from utils.logger import AppLogger

user_router = APIRouter(prefix="/api/user", tags=["用户模块"])
logger = AppLogger.get_logger(__name__)


@user_router.post("/register", response_model=BaseResponse[UserResponse], description="用户注册")
async def register(user_data: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    try:
        result = await userService.register_user(db, user_data)
        return BaseResponse.success(message="注册成功")
    except ValueError as e:
        return BaseResponse.error(code=400, message=str(e))


@user_router.post("/login", response_model=BaseResponse[TokenResponse], description="用户登录")
async def login(login_data: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    result = await userService.login_user(db, login_data)
    if not result:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return BaseResponse.success(data=result)


@user_router.post("/refresh", response_model=BaseResponse[TokenResponse], description="刷新访问令牌")
async def refresh_token(data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    try:
        result = await userService.refresh_access_token(db, data.refresh_token)
        return BaseResponse.success(data=result)
    except ValueError as e:
        return BaseResponse.error(code=400, message=str(e))


@user_router.get("/me", response_model=BaseResponse[CurrentUserResponse], description="获取当前用户信息")
async def get_me(current_user: CurrentUserResponse = Depends(get_current_user)):
    return BaseResponse.success(data=current_user)


@user_router.get("/list", response_model=BaseResponse[UserPageResponse], description="用户列表", dependencies=[Depends(require_permission("user:read"))])
async def list_users(
    page: int = 1,
    page_size: int = 20,
    username: str | None = None,
    email: str | None = None,
    is_active: int | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUserResponse = Depends(get_current_user),
):
    try:
        result = await userService.list_users(
            db,
            page=page,
            page_size=page_size,
            username=username,
            email=email,
            is_active=is_active,
        )
        return BaseResponse.success(data=result)
    except ValueError as e:
        logger.warning("查询用户列表失败: reason=%s", str(e))
        return BaseResponse.error(code=400, message=str(e))


@user_router.get("/{user_id}", response_model=BaseResponse[UserResponse], description="用户详情", dependencies=[Depends(require_permission("user:read"))])
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUserResponse = Depends(get_current_user),
):
    user = await userMapper.get_user_by_id(db, user_id)
    if not user:
        return BaseResponse.error(code=404, message="用户不存在")
    return BaseResponse.success(data=UserResponse.model_validate(user))


@user_router.put("/{user_id}", response_model=BaseResponse[UserResponse], description="更新用户", dependencies=[Depends(require_permission("user:update"))])
async def update_user(
    user_id: int,
    user_data: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUserResponse = Depends(get_current_user),
):
    try:
        result = await userService.update_user(db, user_id, user_data.email)
        return BaseResponse.success(data=result)
    except ValueError as e:
        logger.warning("更新用户失败: user_id=%s reason=%s", user_id, str(e))
        return BaseResponse.error(code=400, message=str(e))


@user_router.put("/{user_id}/status", response_model=BaseResponse[UserResponse], description="更新用户状态", dependencies=[Depends(require_permission("user:status"))])
async def update_user_status(
    user_id: int,
    status_data: UserStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUserResponse = Depends(get_current_user),
):
    try:
        result = await userService.update_user_status(db, user_id, status_data.is_active)
        return BaseResponse.success(data=result)
    except ValueError as e:
        logger.warning("更新用户状态失败: user_id=%s reason=%s", user_id, str(e))
        return BaseResponse.error(code=400, message=str(e))


@user_router.put("/{user_id}/password", response_model=BaseResponse[UserResponse], description="重置用户密码", dependencies=[Depends(require_permission("user:password:reset"))])
async def reset_user_password(
    user_id: int,
    password_data: UserPasswordResetRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUserResponse = Depends(get_current_user),
):
    try:
        result = await userService.reset_user_password(db, user_id, password_data.new_password)
        return BaseResponse.success(data=result)
    except ValueError as e:
        logger.warning("重置用户密码失败: user_id=%s reason=%s", user_id, str(e))
        return BaseResponse.error(code=400, message=str(e))


@user_router.delete("/{user_id}", response_model=BaseResponse[bool], description="删除用户", dependencies=[Depends(require_permission("user:delete"))])
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUserResponse = Depends(get_current_user),
):
    try:
        await userService.delete_user(db, user_id)
        return BaseResponse.success()
    except ValueError as e:
        logger.warning("删除用户失败: user_id=%s reason=%s", user_id, str(e))
        return BaseResponse.error(code=400, message=str(e))
