import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from mapper import userMapper
from models.userInfo import SysUser
from schema.userSchema import UserRegisterRequest, UserLoginRequest, UserResponse, TokenResponse

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # 限制密码长度
    password_bytes = plain_password.encode('utf-8')[:72]
    # 验证密码
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def get_password_hash(password: str) -> str:
    # 限制密码长度
    password_bytes = password.encode('utf-8')[:72]
    # 生成盐
    salt = bcrypt.gensalt()
    # 生成哈希
    hashed = bcrypt.hashpw(password_bytes, salt)
    # 返回哈希
    return hashed.decode('utf-8')


def create_access_token(user_id: int) -> TokenResponse:
    # 创建令牌
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # 生成令牌
    to_encode = {"sub": str(user_id), "exp": expire}
    # 编码令牌
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    # 返回令牌
    return TokenResponse(access_token=encoded_jwt, token_type="bearer")


async def login_user(db: AsyncSession, login_data: UserLoginRequest) -> Optional[TokenResponse]:
    user = await userMapper.get_user_by_username(db, login_data.username)
    if not user:
        return None
    if not verify_password(login_data.password, user.hashed_password):
        return None
    if user.is_active != 1:
        return None
    return create_access_token(user.id)


async def register_user(db: AsyncSession, user_data: UserRegisterRequest) -> UserResponse:
    existing_user = await userMapper.get_user_by_username(db, user_data.username)
    if existing_user:
        raise ValueError(f"用户名 {user_data.username} 已存在")

    hashed_password = get_password_hash(user_data.password)
    user = SysUser(
        username=user_data.username,
        hashed_password=hashed_password,
        email=user_data.email,
        is_active=1
    )
    result = await userMapper.create_user(db, user)
    return UserResponse.model_validate(result)
