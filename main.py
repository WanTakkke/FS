from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from controller import studentController, userController

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有HTTP地址访问
    allow_credentials=True,  # 允许发送凭据（cookies、认证头部等）
    allow_methods=["*"],  # 允许所有HTTP方法
    # 或指定方法：allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers=["*"],  # 允许所有HTTP头部
    # 或指定头部：allow_headers=["Authorization", "Content-Type"]
)

#导入子路由
app.include_router(studentController.stu_router)
app.include_router(userController.user_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8001)