import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from mapper import userMapper, rbacMapper
from models.userInfo import SysUser
from schema.userSchema import UserRegisterRequest, UserLoginRequest, UserResponse, TokenResponse

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


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
    # 返回哈希（字符串）
    return hashed.decode('utf-8')

"""
解码token
"""
def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        raise ValueError("token无效或已过期") from e


def _create_access_token(user_id: int, username: str, roles: list[str], perm_version: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "username": username,
        "roles": roles,
        "perm_version": perm_version,
        "token_type": "access",
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def _create_refresh_token(user_id: int, token_jti: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "jti": token_jti,
        "token_type": "refresh",
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def _extract_expire_at(payload: dict) -> datetime:
    raw_exp = payload.get("exp")
    if raw_exp is None:
        raise ValueError("token缺少过期时间")
    if isinstance(raw_exp, (int, float)):
        return datetime.fromtimestamp(raw_exp, tz=timezone.utc)
    if isinstance(raw_exp, datetime):
        return raw_exp.astimezone(timezone.utc)
    raise ValueError("token过期时间格式不合法")


async def login_user(db: AsyncSession, login_data: UserLoginRequest) -> Optional[TokenResponse]:
    user = await userMapper.get_user_by_username(db, login_data.username)
    if not user:
        return None
    if not verify_password(login_data.password, user.hashed_password):
        return None
    if user.is_active != 1:
        return None
    roles = await rbacMapper.get_user_roles(db, user.id)
    perm_version = await userMapper.get_user_perm_version(db, user.id)
    access_token = _create_access_token(user.id, user.username, roles, perm_version)
    refresh_jti = str(uuid4())
    refresh_token = _create_refresh_token(user.id, refresh_jti)
    refresh_payload = decode_token(refresh_token)
    await userMapper.create_refresh_token_record(
        db,
        token_jti=refresh_jti,
        user_id=user.id,
        expires_at=_extract_expire_at(refresh_payload),
    )
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


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


async def refresh_access_token(db: AsyncSession, refresh_token: str) -> TokenResponse:
    payload = decode_token(refresh_token)
    if payload.get("token_type") != "refresh":
        raise ValueError("refresh_token类型错误")
    user_id = int(payload.get("sub", "0"))
    token_jti = str(payload.get("jti", "")).strip()
    if not token_jti:
        raise ValueError("refresh_token缺少jti")
    if user_id <= 0:
        raise ValueError("refresh_token缺少用户信息")
    refresh_record = await userMapper.get_refresh_token_record(db, token_jti)
    if not refresh_record:
        raise ValueError("refresh_token不存在或已失效")
    if int(refresh_record["user_id"]) != user_id:
        raise ValueError("refresh_token用户不匹配")
    if not userMapper.is_refresh_record_active(refresh_record):
        raise ValueError("refresh_token不存在或已失效")
    user = await userMapper.get_user_by_id(db, user_id)
    if not user or user.is_active != 1:
        raise ValueError("用户不存在或已禁用")
    roles = await rbacMapper.get_user_roles(db, user.id)
    perm_version = await userMapper.get_user_perm_version(db, user.id)
    access_token = _create_access_token(user.id, user.username, roles, perm_version)
    new_refresh_jti = str(uuid4())
    new_refresh_token = _create_refresh_token(user.id, new_refresh_jti)
    new_refresh_payload = decode_token(new_refresh_token)
    await userMapper.revoke_refresh_token(db, token_jti=token_jti, replaced_by_jti=new_refresh_jti)
    await userMapper.create_refresh_token_record(
        db,
        token_jti=new_refresh_jti,
        user_id=user.id,
        expires_at=_extract_expire_at(new_refresh_payload),
    )
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
