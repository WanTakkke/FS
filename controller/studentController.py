from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_config import get_db
from mapper import studentMapper

stu_router = APIRouter(prefix="/api/student", tags=["学生模块"])

@stu_router.get("/query")
async def get_student(skip: int = 0, limit: int=10, db: AsyncSession = Depends(get_db)):
    result = await studentMapper.get_student(db, skip, limit)
    return {
        "code":200,
        "message": "success",
        "data": result
    }
