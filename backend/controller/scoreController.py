from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from schema.scoreSchema import ScoreRequest, ScoreResponse, ScoreUpdateRequest, ScoreQueryRequest
from service import scoreService
from utils.baseResponse import BaseResponse
from utils.logger import AppLogger

score_router = APIRouter(prefix="/api/score", tags=["成绩模块"])
logger = AppLogger.get_logger(__name__)


@score_router.get("/query", response_model=BaseResponse[List[ScoreResponse]], description="查询成绩信息")
async def get_score(page: int = 1, page_size: int = 10, db: AsyncSession = Depends(get_db)):
    logger.info("成绩列表查询请求: page=%s, page_size=%s", page, page_size)
    result = await scoreService.get_score(db, page, page_size)
    logger.info("成绩列表查询完成: count=%s", len(result))
    return BaseResponse.success(data=result)


@score_router.post("/query/condition", response_model=BaseResponse[List[ScoreResponse]], description="多条件查询成绩信息")
async def get_score_by_conditions(query_params: ScoreQueryRequest, db: AsyncSession = Depends(get_db)):
    logger.info("成绩多条件查询请求: params=%s", query_params.model_dump())
    result = await scoreService.get_score_by_conditions(db, query_params)
    logger.info("成绩多条件查询完成: count=%s", len(result))
    return BaseResponse.success(data=result)


@score_router.post("/add", response_model=BaseResponse[ScoreResponse], description="新增成绩信息")
async def add_score(score_data: ScoreRequest, db: AsyncSession = Depends(get_db)):
    try:
        logger.info("新增成绩请求: student_code=%s, exam_sequence=%s", score_data.student_code, score_data.exam_sequence)
        result = await scoreService.create_score(db, score_data)
        logger.info("新增成绩成功: student_name=%s, exam_sequence=%s", result.student_name, result.exam_sequence)
        return BaseResponse.success(data=result)
    except ValueError as e:
        logger.warning(
            "新增成绩失败: student_code=%s, exam_sequence=%s, reason=%s",
            score_data.student_code, score_data.exam_sequence, str(e)
        )
        return BaseResponse.error(code=400, message=str(e))


@score_router.post("/update", response_model=BaseResponse[ScoreResponse], description="修改成绩信息")
async def update_score(score_data: ScoreUpdateRequest, db: AsyncSession = Depends(get_db)):
    try:
        logger.info(
            "修改成绩请求: student_code=%s, exam_sequence=%s",
            score_data.student_code,
            score_data.exam_sequence
        )
        result = await scoreService.update_score(db, score_data)
        logger.info(
            "修改成绩成功: student_code=%s, exam_sequence=%s",
            score_data.student_code,
            score_data.exam_sequence
        )
        return BaseResponse.success(data=result)
    except ValueError as e:
        logger.warning(
            "修改成绩失败: student_code=%s, exam_sequence=%s, reason=%s",
            score_data.student_code,
            score_data.exam_sequence,
            str(e)
        )
        return BaseResponse.error(code=400, message=str(e))

"""
旧的删除接口，先保留
"""
# @score_router.delete("/delete/{score_id}", response_model=BaseResponse[bool], description="删除成绩信息")
# async def delete_score(score_id: int, db: AsyncSession = Depends(get_db)):
#     try:
#         logger.info("删除成绩请求: id=%s", score_id)
#         await scoreService.delete_score(db, score_id)
#         logger.info("删除成绩成功: id=%s", score_id)
#         return BaseResponse.success()
#     except ValueError as e:
#         logger.warning("删除成绩失败: id=%s, reason=%s", score_id, str(e))
#         return BaseResponse.error(code=400, message=str(e))


@score_router.delete("/delete/{student_code}/{exam_sequence}", response_model=BaseResponse[bool], description="按学生编号和考核序次删除成绩信息")
async def delete_score_by_student_and_exam(student_code: str, exam_sequence: str, db: AsyncSession = Depends(get_db)):
    try:
        logger.info("删除成绩请求: student_code=%s, exam_sequence=%s", student_code, exam_sequence)
        await scoreService.delete_score_by_student_and_exam(db, student_code, exam_sequence)
        logger.info("删除成绩成功: student_code=%s, exam_sequence=%s", student_code, exam_sequence)
        return BaseResponse.success()
    except ValueError as e:
        logger.warning(
            "删除成绩失败: student_code=%s, exam_sequence=%s, reason=%s",
            student_code,
            exam_sequence,
            str(e)
        )
        return BaseResponse.error(code=400, message=str(e))
