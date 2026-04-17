from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from common.baseResponse import BaseResponse
from config.db_config import get_db
from schema.userSchema import UserRegisterRequest, UserLoginRequest, UserResponse, TokenResponse
from service import userService

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
