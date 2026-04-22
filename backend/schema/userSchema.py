from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator


class UserRegisterRequest(BaseModel):
    username: str
    password: str
    email: str | None = None


class UserLoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int | None = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class CurrentUserResponse(BaseModel):
    id: int
    username: str
    email: str | None = None
    roles: list[str]
    permissions: list[str]


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str | None = None
    is_active: int
    created_at: str | None = None

    @field_validator('created_at', mode='before')
    @classmethod
    def convert_datetime(cls, v):
        if isinstance(v, datetime):
            return v.strftime('%Y-%m-%d %H:%M:%S')
        return v

    @property
    def password(self):
        return None
