from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from schema.employmentSchema import (
    EmploymentRequest,
    EmploymentResponse,
    EmploymentUpdateRequest,
    EmploymentQueryRequest
)
from service import employmentService
from utils.baseResponse import BaseResponse
from utils.logger import AppLogger

employment_router = APIRouter(prefix="/api/employment", tags=["就业模块"])
logger = AppLogger.get_logger(__name__)


@employment_router.get("/query", response_model=BaseResponse[List[EmploymentResponse]], description="查询就业信息")
async def get_employment(page: int = 1, page_size: int = 10, db: AsyncSession = Depends(get_db)):
    logger.info("就业列表查询请求: page=%s, page_size=%s", page, page_size)
    result = await employmentService.get_employment(db, page, page_size)
    logger.info("就业列表查询完成: count=%s", len(result))
    return BaseResponse.success(data=result)


@employment_router.post("/query/condition", response_model=BaseResponse[List[EmploymentResponse]], description="多条件查询就业信息")
async def get_employment_by_conditions(query_params: EmploymentQueryRequest, db: AsyncSession = Depends(get_db)):
    logger.info("就业多条件查询请求: params=%s", query_params.model_dump())
    result = await employmentService.get_employment_by_conditions(db, query_params)
    logger.info("就业多条件查询完成: count=%s", len(result))
    return BaseResponse.success(data=result)


@employment_router.get("/query/{employment_id}", response_model=BaseResponse[EmploymentResponse], description="查询就业详情")
async def get_employment_detail(employment_id: int, db: AsyncSession = Depends(get_db)):
    try:
        logger.info("就业详情查询请求: id=%s", employment_id)
        result = await employmentService.get_employment_detail(db, employment_id)
        logger.info("就业详情查询成功: id=%s", employment_id)
        return BaseResponse.success(data=result)
    except ValueError as e:
        logger.warning("就业详情查询失败: id=%s, reason=%s", employment_id, str(e))
        return BaseResponse.error(code=400, message=str(e))


@employment_router.post("/add", response_model=BaseResponse[EmploymentResponse], description="新增就业信息")
async def add_employment(employment_data: EmploymentRequest, db: AsyncSession = Depends(get_db)):
    try:
        logger.info(
            "新增就业请求: student_code=%s, company_name=%s",
            employment_data.student_code,
            employment_data.company_name
        )
        result = await employmentService.create_employment(db, employment_data)
        logger.info("新增就业成功: student_code=%s, company_name=%s", result.student_code, result.company_name)
        return BaseResponse.success(data=result)
    except ValueError as e:
        logger.warning(
            "新增就业失败: student_code=%s, company_name=%s, reason=%s",
            employment_data.student_code,
            employment_data.company_name,
            str(e)
        )
        return BaseResponse.error(code=400, message=str(e))


@employment_router.post("/update", response_model=BaseResponse[EmploymentResponse], description="修改就业信息")
async def update_employment(employment_data: EmploymentUpdateRequest, db: AsyncSession = Depends(get_db)):
    try:
        logger.info("修改就业请求: id=%s", employment_data.id)
        result = await employmentService.update_employment(db, employment_data)
        logger.info("修改就业成功: id=%s", employment_data.id)
        return BaseResponse.success(data=result)
    except ValueError as e:
        logger.warning("修改就业失败: id=%s, reason=%s", employment_data.id, str(e))
        return BaseResponse.error(code=400, message=str(e))


@employment_router.delete("/delete/{employment_id}", response_model=BaseResponse[bool], description="删除就业信息")
async def delete_employment(employment_id: int, db: AsyncSession = Depends(get_db)):
    try:
        logger.info("删除就业请求: id=%s", employment_id)
        await employmentService.delete_employment(db, employment_id)
        logger.info("删除就业成功: id=%s", employment_id)
        return BaseResponse.success()
    except ValueError as e:
        logger.warning("删除就业失败: id=%s, reason=%s", employment_id, str(e))
        return BaseResponse.error(code=400, message=str(e))
