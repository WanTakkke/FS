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
)
from service import userService
from utils.auth import get_current_user

user_router = APIRouter(prefix="/api/user", tags=["用户模块"])


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
