from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

# 定义泛型类型变量
T = TypeVar("T")

class BaseResponse(BaseModel, Generic[T]):
    """
    统一响应模型
    """
    code: int = None
    message: str = None
    data: Optional[T] = None

    @classmethod
    def success(cls, message: str = "success", data: Optional[T] = None) -> "BaseResponse[T]":
        """
        成功响应
        """
        return cls(code=200, message=message, data=data)

    @classmethod
    def error(cls, code: int = 400, message: str = "error", data: Optional[T] = None) -> "BaseResponse[T]":
        """
        错误响应
        """
        return cls(code=code, message=message, data=data)
