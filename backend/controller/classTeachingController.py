from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from schema.classTeachingSchema import (
    ClassTeachingRequest,
    ClassTeachingResponse,
    ClassTeachingUpdateRequest,
    ClassTeachingQueryRequest,
)
from service import classTeachingService
from utils.baseResponse import BaseResponse
from utils.logger import AppLogger

class_teaching_router = APIRouter(prefix="/api/class-teaching", tags=["班级授课模块"])
logger = AppLogger.get_logger(__name__)


@class_teaching_router.get("/query", response_model=BaseResponse[List[ClassTeachingResponse]], description="查询班级授课信息")
async def get_class_teaching(page: int = 1, page_size: int = 10, db: AsyncSession = Depends(get_db)):
    logger.info("班级授课列表查询请求: page=%s, page_size=%s", page, page_size)
    result = await classTeachingService.get_class_teaching(db, page, page_size)
    logger.info("班级授课列表查询完成: count=%s", len(result))
    return BaseResponse.success(data=result)


@class_teaching_router.post("/query/condition", response_model=BaseResponse[List[ClassTeachingResponse]], description="多条件查询班级授课信息")
async def get_class_teaching_by_conditions(query_params: ClassTeachingQueryRequest, db: AsyncSession = Depends(get_db)):
    logger.info("班级授课多条件查询请求: params=%s", query_params.model_dump())
    result = await classTeachingService.get_class_teaching_by_conditions(db, query_params)
    logger.info("班级授课多条件查询完成: count=%s", len(result))
    return BaseResponse.success(data=result)


@class_teaching_router.get("/query/{teaching_id}", response_model=BaseResponse[ClassTeachingResponse], description="查询班级授课详情（按授课老师id）")
async def get_class_teaching_detail(teaching_id: int, db: AsyncSession = Depends(get_db)):
    try:
        logger.info("班级授课详情查询请求: id=%s", teaching_id)
        result = await classTeachingService.get_class_teaching_detail(db, teaching_id)
        logger.info("班级授课详情查询成功: id=%s", teaching_id)
        return BaseResponse.success(data=result)
    except ValueError as e:
        logger.warning("班级授课详情查询失败: id=%s, reason=%s", teaching_id, str(e))
        return BaseResponse.error(code=400, message=str(e))


@class_teaching_router.post("/add", response_model=BaseResponse[ClassTeachingResponse], description="新增班级授课信息")
async def add_class_teaching(teaching_data: ClassTeachingRequest, db: AsyncSession = Depends(get_db)):
    try:
        logger.info(
            "新增班级授课请求: class_code=%s, lecturer_code=%s, course_code=%s",
            teaching_data.class_code,
            teaching_data.lecturer_code,
            teaching_data.course_code
        )
        result = await classTeachingService.create_class_teaching(db, teaching_data)
        logger.info(
            "新增班级授课成功: class_code=%s, lecturer_code=%s, course_code=%s",
            result.class_code,
            result.lecturer_code,
            result.course_code
        )
        return BaseResponse.success(data=result)
    except ValueError as e:
        logger.warning(
            "新增班级授课失败: class_code=%s, lecturer_code=%s, course_code=%s, reason=%s",
            teaching_data.class_code,
            teaching_data.lecturer_code,
            teaching_data.course_code,
            str(e)
        )
        return BaseResponse.error(code=400, message=str(e))


@class_teaching_router.post("/update", response_model=BaseResponse[ClassTeachingResponse], description="修改班级授课信息")
async def update_class_teaching(teaching_data: ClassTeachingUpdateRequest, db: AsyncSession = Depends(get_db)):
    try:
        logger.info("修改班级授课请求: id=%s", teaching_data.id)
        result = await classTeachingService.update_class_teaching(db, teaching_data)
        logger.info("修改班级授课成功: id=%s", teaching_data.id)
        return BaseResponse.success(data=result)
    except ValueError as e:
        logger.warning("修改班级授课失败: id=%s, reason=%s", teaching_data.id, str(e))
        return BaseResponse.error(code=400, message=str(e))


@class_teaching_router.delete("/delete/{teaching_id}", response_model=BaseResponse[bool], description="删除班级授课信息")
async def delete_class_teaching(teaching_id: int, db: AsyncSession = Depends(get_db)):
    try:
        logger.info("删除班级授课请求: id=%s", teaching_id)
        await classTeachingService.delete_class_teaching(db, teaching_id)
        logger.info("删除班级授课成功: id=%s", teaching_id)
        return BaseResponse.success()
    except ValueError as e:
        logger.warning("删除班级授课失败: id=%s, reason=%s", teaching_id, str(e))
        return BaseResponse.error(code=400, message=str(e))
