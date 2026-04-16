from fastapi import APIRouter

stu_router = APIRouter(prefix="/api/student", tags=["学生模块"])

@stu_router.get("/test")
async def test():
    return {"message": "Hello World"}