from pydantic import BaseModel, ConfigDict, Field


class RoleCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    code: str = Field(min_length=1, max_length=64)
    description: str | None = Field(default=None, max_length=255)


class RoleUpdateRequest(BaseModel):
    role_id: int
    name: str | None = Field(default=None, min_length=1, max_length=64)
    description: str | None = Field(default=None, max_length=255)


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
    description: str | None = None


class PermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    parent_id: int | None = None
    name: str
    code: str
    type: str


class UserRoleBindRequest(BaseModel):
    user_id: int
    role_ids: list[int] = Field(default_factory=list)


class RolePermissionBindRequest(BaseModel):
    role_id: int
    permission_ids: list[int] = Field(default_factory=list)


class UserRolePermissionResponse(BaseModel):
    user_id: int
    username: str
    roles: list[str]
    permissions: list[str]
