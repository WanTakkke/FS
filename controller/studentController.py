from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from utils.baseResponse import BaseResponse
from utils.logger import AppLogger
from config.db_config import get_db
from schema.studentSchema import StudentRequest, StudentResponse, StudentUpdateRequest, StudentQueryRequest
from service import studentSerive

stu_router = APIRouter(prefix="/api/student", tags=["学生模块"])
logger = AppLogger.get_logger(__name__)

@stu_router.get("/query", response_model=BaseResponse[List[StudentResponse]], description="查询学生信息")
async def get_student(page: int = 1, page_size: int=10, db: AsyncSession = Depends(get_db)):
    logger.info("学生列表查询请求: page=%s, page_size=%s", page, page_size)
    result = await studentSerive.get_student(db, page, page_size)
    logger.info("学生列表查询完成: count=%s", len(result))
    return BaseResponse.success(data=result)


@stu_router.post("/query/condition", response_model=BaseResponse[List[StudentResponse]], description="多条件查询学生信息")
async def get_student_by_conditions(
        query_params: StudentQueryRequest,
        db: AsyncSession = Depends(get_db)
):
    logger.info("学生多条件查询请求: params=%s", query_params.model_dump())
    result = await studentSerive.get_student_by_conditions(db, query_params)
    logger.info("学生多条件查询完成: count=%s", len(result))
    return BaseResponse.success(data=result)


@stu_router.post("/add", response_model=BaseResponse[StudentResponse], description="新增学生信息")
async def add_student(student_data: StudentRequest, db: AsyncSession = Depends(get_db)):
    try:
        logger.info("新增学生请求: student_code=%s", student_data.student_code)
        result = await studentSerive.create_student(db, student_data)
        logger.info("新增学生成功: student_code=%s", student_data.student_code)
        return BaseResponse.success(data=result)
    except ValueError as e:
        logger.warning("新增学生失败: student_code=%s, reason=%s", student_data.student_code, str(e))
        return BaseResponse.error(code=400, message=str(e))


@stu_router.post("/update", response_model=BaseResponse[StudentResponse], description="修改学生信息")
async def update_student(student_data: StudentUpdateRequest, db: AsyncSession = Depends(get_db)):
    try:
        logger.info("修改学生请求: student_code=%s", student_data.student_code)
        result = await studentSerive.update_student(db, student_data)
        logger.info("修改学生成功: student_code=%s", student_data.student_code)
        return BaseResponse.success(data=result)
    except ValueError as e:
        logger.warning("修改学生失败: student_code=%s, reason=%s", student_data.student_code, str(e))
        return BaseResponse.error(code=400, message=str(e))


@stu_router.delete("/delete/{student_code}", response_model=BaseResponse[bool], description="删除学生信息")
async def delete_student(student_code: str, db: AsyncSession = Depends(get_db)):
    try:
        logger.info("删除学生请求: student_code=%s", student_code)
        await studentSerive.delete_student(db, student_code)
        logger.info("删除学生成功: student_code=%s", student_code)
        return BaseResponse.success()
    except ValueError as e:
        logger.warning("删除学生失败: student_code=%s, reason=%s", student_code, str(e))
        return BaseResponse.error(code=400, message=str(e))

