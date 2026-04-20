from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from utils.baseResponse import BaseResponse
from utils.logger import AppLogger

logger = AppLogger.get_logger(__name__)


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(
            "请求参数校验失败: path=%s errors=%s",
            request.url.path,
            exc.errors()
        )
        # 统一兜底请求参数错误，避免将详细校验信息直接暴露给前端
        response = BaseResponse.error(code=400, message="请求参数错误，请检查后重试")
        return JSONResponse(status_code=400, content=response.model_dump())

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception("系统异常: path=%s", request.url.path)
        response = BaseResponse.error(code=500, message="系统繁忙，请稍后重试")
        return JSONResponse(status_code=500, content=response.model_dump())
