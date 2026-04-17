from pydantic import BaseModel, ConfigDict


class UserRegisterRequest(BaseModel):
    username: str
    password: str
    email: str | None = None


class UserLoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str | None = None
    is_active: int
    created_at: str | None = None

    @property
    def password(self):
        return None
