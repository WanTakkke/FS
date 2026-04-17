from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from common.baseResponse import BaseResponse
from config.db_config import get_db
from schema.studentSchema import StudentRequest, StudentResponse
from service import studentSerive

stu_router = APIRouter(prefix="/api/student", tags=["学生模块"])

@stu_router.get("/query", response_model=BaseResponse[List[StudentResponse]], description="查询学生信息")
async def get_student(page: int = 1, page_size: int=10, db: AsyncSession = Depends(get_db)):
    result = await studentSerive.get_student(db, page, page_size)
    return BaseResponse.success(data=result)


@stu_router.post("/add", response_model=BaseResponse[StudentResponse], description="新增学生信息")
async def add_student(student_data: StudentRequest, db: AsyncSession = Depends(get_db)):
    try:
        result = await studentSerive.create_student(db, student_data)
        return BaseResponse.success(data=result)
    except ValueError as e:
        return BaseResponse.error(code=400, message=str(e))

