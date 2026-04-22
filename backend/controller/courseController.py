from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from schema.courseSchema import CourseRequest, CourseResponse, CourseUpdateRequest, CourseQueryRequest
from service import courseService
from utils.auth import require_permission
from utils.baseResponse import BaseResponse
from utils.logger import AppLogger

course_router = APIRouter(prefix="/api/course", tags=["课程模块"])
logger = AppLogger.get_logger(__name__)


@course_router.get("/query", response_model=BaseResponse[List[CourseResponse]], description="查询课程信息")
async def get_course(
    page: int = 1,
    page_size: int = 10,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_permission("course:read")),
):
    logger.info("课程列表查询请求: page=%s, page_size=%s", page, page_size)
    result = await courseService.get_course(db, page, page_size)
    logger.info("课程列表查询完成: count=%s", len(result))
    return BaseResponse.success(data=result)


@course_router.post("/query/condition", response_model=BaseResponse[List[CourseResponse]], description="多条件查询课程信息")
async def get_course_by_conditions(
    query_params: CourseQueryRequest,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_permission("course:read")),
):
    logger.info("课程多条件查询请求: params=%s", query_params.model_dump())
    result = await courseService.get_course_by_conditions(db, query_params)
    logger.info("课程多条件查询完成: count=%s", len(result))
    return BaseResponse.success(data=result)


@course_router.get("/query/{course_code}", response_model=BaseResponse[CourseResponse], description="查询课程详情")
async def get_course_detail(
    course_code: str,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_permission("course:read")),
):
    try:
        logger.info("课程详情查询请求: course_code=%s", course_code)
        result = await courseService.get_course_detail(db, course_code)
        logger.info("课程详情查询成功: course_code=%s", course_code)
        return BaseResponse.success(data=result)
    except ValueError as e:
        logger.warning("课程详情查询失败: course_code=%s, reason=%s", course_code, str(e))
        return BaseResponse.error(code=400, message=str(e))


@course_router.post("/add", response_model=BaseResponse[CourseResponse], description="新增课程信息")
async def add_course(
    course_data: CourseRequest,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_permission("course:create")),
):
    try:
        logger.info("新增课程请求: course_code=%s", course_data.course_code)
        result = await courseService.create_course(db, course_data)
        logger.info("新增课程成功: course_code=%s", course_data.course_code)
        return BaseResponse.success(data=result)
    except ValueError as e:
        logger.warning("新增课程失败: course_code=%s, reason=%s", course_data.course_code, str(e))
        return BaseResponse.error(code=400, message=str(e))


@course_router.post("/update", response_model=BaseResponse[CourseResponse], description="修改课程信息")
async def update_course(
    course_data: CourseUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_permission("course:update")),
):
    try:
        logger.info("修改课程请求: course_code=%s", course_data.course_code)
        result = await courseService.update_course(db, course_data)
        logger.info("修改课程成功: course_code=%s", course_data.course_code)
        return BaseResponse.success(data=result)
    except ValueError as e:
        logger.warning("修改课程失败: course_code=%s, reason=%s", course_data.course_code, str(e))
        return BaseResponse.error(code=400, message=str(e))


@course_router.delete("/delete/{course_code}", response_model=BaseResponse[bool], description="删除课程信息")
async def delete_course(
    course_code: str,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_permission("course:delete")),
):
    try:
        logger.info("删除课程请求: course_code=%s", course_code)
        await courseService.delete_course(db, course_code)
        logger.info("删除课程成功: course_code=%s", course_code)
        return BaseResponse.success()
    except ValueError as e:
        logger.warning("删除课程失败: course_code=%s, reason=%s", course_code, str(e))
        return BaseResponse.error(code=400, message=str(e))
