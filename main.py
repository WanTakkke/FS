import os

from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from controller import studentController, userController, classController, scoreController, employmentController, classTeachingController, courseController
from utils.exception_handlers import register_exception_handlers
from utils.logger import AppLogger

load_dotenv()

app = FastAPI()

# 初始化日志
log_level = os.getenv("LOG_LEVEL", "INFO")
log_dir = os.getenv("LOG_DIR")
log_filename = os.getenv("LOG_FILENAME", "app.log")
AppLogger.setup(level=log_level, log_dir=log_dir, log_filename=log_filename)
logger = AppLogger.get_logger(__name__)

# 注册全局异常处理
register_exception_handlers(app)


def _parse_cors_allow_origins() -> list[str]:
    raw_value = os.getenv("CORS_ALLOW_ORIGINS", "*")
    if not raw_value.strip():
        return ["*"]
    origins = [item.strip() for item in raw_value.split(",") if item.strip()]
    return origins or ["*"]


cors_allow_origins = _parse_cors_allow_origins()
logger.info("CORS配置加载完成: allow_origins=%s", cors_allow_origins)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_allow_origins,
    allow_credentials=True,  # 允许发送凭据（cookies、认证头部等）
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有HTTP头部
)

#导入子路由
app.include_router(studentController.stu_router)
app.include_router(userController.user_router)
app.include_router(classController.class_router)
app.include_router(scoreController.score_router)
app.include_router(employmentController.employment_router)
app.include_router(classTeachingController.class_teaching_router)
app.include_router(courseController.course_router)

@app.get("/")
async def root():
    logger.info("访问根路径")
    return {"message": "Hello World"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8001)
