from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from schema.classSchema import ClassRequest, ClassResponse, ClassUpdateRequest, ClassQueryRequest
from service import classService
from utils.baseResponse import BaseResponse
from utils.logger import AppLogger

class_router = APIRouter(prefix="/api/class", tags=["班级模块"])
logger = AppLogger.get_logger(__name__)


@class_router.get("/query", response_model=BaseResponse[List[ClassResponse]], description="查询班级信息")
async def get_class(page: int = 1, page_size: int = 10, db: AsyncSession = Depends(get_db)):
    logger.info("班级列表查询请求: page=%s, page_size=%s", page, page_size)
    result = await classService.get_class(db, page, page_size)
    logger.info("班级列表查询完成: count=%s", len(result))
    return BaseResponse.success(data=result)


@class_router.post("/query/condition", response_model=BaseResponse[List[ClassResponse]], description="多条件查询班级信息")
async def get_class_by_conditions(query_params: ClassQueryRequest, db: AsyncSession = Depends(get_db)):
    logger.info("班级多条件查询请求: params=%s", query_params.model_dump())
    result = await classService.get_class_by_conditions(db, query_params)
    logger.info("班级多条件查询完成: count=%s", len(result))
    return BaseResponse.success(data=result)


@class_router.get("/query/{class_code}", response_model=BaseResponse[ClassResponse], description="查询班级详情")
async def get_class_detail(class_code: str, db: AsyncSession = Depends(get_db)):
    try:
        logger.info("班级详情查询请求: class_code=%s", class_code)
        result = await classService.get_class_detail(db, class_code)
        logger.info("班级详情查询成功: class_code=%s", class_code)
        return BaseResponse.success(data=result)
    except ValueError as e:
        logger.warning("班级详情查询失败: class_code=%s, reason=%s", class_code, str(e))
        return BaseResponse.error(code=400, message=str(e))


@class_router.post("/add", response_model=BaseResponse[ClassResponse], description="新增班级信息")
async def add_class(class_data: ClassRequest, db: AsyncSession = Depends(get_db)):
    try:
        logger.info("新增班级请求: class_code=%s", class_data.class_code)
        result = await classService.create_class(db, class_data)
        logger.info("新增班级成功: class_code=%s", class_data.class_code)
        return BaseResponse.success(data=result)
    except ValueError as e:
        logger.warning("新增班级失败: class_code=%s, reason=%s", class_data.class_code, str(e))
        return BaseResponse.error(code=400, message=str(e))


@class_router.post("/update", response_model=BaseResponse[ClassResponse], description="修改班级信息")
async def update_class(class_data: ClassUpdateRequest, db: AsyncSession = Depends(get_db)):
    try:
        logger.info("修改班级请求: class_code=%s", class_data.class_code)
        result = await classService.update_class(db, class_data)
        logger.info("修改班级成功: class_code=%s", class_data.class_code)
        return BaseResponse.success(data=result)
    except ValueError as e:
        logger.warning("修改班级失败: class_code=%s, reason=%s", class_data.class_code, str(e))
        return BaseResponse.error(code=400, message=str(e))


@class_router.delete("/delete/{class_code}", response_model=BaseResponse[bool], description="删除班级信息")
async def delete_class(class_code: str, db: AsyncSession = Depends(get_db)):
    try:
        logger.info("删除班级请求: class_code=%s", class_code)
        await classService.delete_class(db, class_code)
        logger.info("删除班级成功: class_code=%s", class_code)
        return BaseResponse.success()
    except ValueError as e:
        logger.warning("删除班级失败: class_code=%s, reason=%s", class_code, str(e))
        return BaseResponse.error(code=400, message=str(e))

