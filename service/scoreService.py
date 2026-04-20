from sqlalchemy.ext.asyncio import AsyncSession

from mapper import scoreMapper
from models.scoreInfo import ScoreInfo
from schema.scoreSchema import ScoreResponse, ScoreRequest, ScoreUpdateRequest, ScoreQueryRequest
from utils.logger import AppLogger

logger = AppLogger.get_logger(__name__)


async def get_score(db: AsyncSession, page: int, page_size: int):
    logger.info("Service成绩分页查询: page=%s, page_size=%s", page, page_size)
    skip = (page - 1) * page_size
    result = await scoreMapper.get_score(db, skip, page_size)
    logger.info("Service成绩分页查询完成: count=%s", len(result))
    return [ScoreResponse.model_validate(item) for item in result]


async def get_score_by_conditions(db: AsyncSession, query_params: ScoreQueryRequest):
    logger.info("Service成绩多条件查询: page=%s, page_size=%s", query_params.page, query_params.page_size)
    skip = (query_params.page - 1) * query_params.page_size
    result = await scoreMapper.get_score_by_conditions(db, query_params, skip, query_params.page_size)
    logger.info("Service成绩多条件查询完成: count=%s", len(result))
    return [ScoreResponse.model_validate(item) for item in result]


async def create_score(db: AsyncSession, score_data: ScoreRequest):
    logger.info("Service新增成绩: student_code=%s, exam_sequence=%s", score_data.student_code, score_data.exam_sequence)

    student = await scoreMapper.get_student_by_code(db, score_data.student_code)
    if not student:
        logger.warning("Service新增成绩失败: 学生不存在 student_code=%s", score_data.student_code)
        raise ValueError(f"学生编号 {score_data.student_code} 不存在")

    duplicate = await scoreMapper.get_score_by_student_and_exam(db, student.id, score_data.exam_sequence)
    if duplicate:
        logger.warning(
            "Service新增成绩失败: 成绩记录已存在 student_code=%s, exam_sequence=%s",
            score_data.student_code, score_data.exam_sequence
        )
        raise ValueError(f"学生编号 {score_data.student_code} 的 {score_data.exam_sequence} 成绩已存在")

    score_info = ScoreInfo(
        student_id=student.id,
        exam_sequence=score_data.exam_sequence,
        score=score_data.score
    )
    created = await scoreMapper.create_score(db, score_info)
    result = await scoreMapper.get_score_detail_with_student(db, created.id)
    logger.info("Service新增成绩成功: id=%s", created.id)
    return ScoreResponse.model_validate(result)


async def update_score(db: AsyncSession, score_data: ScoreUpdateRequest):
    logger.info("Service修改成绩: id=%s", score_data.id)
    existing_score = await scoreMapper.get_score_by_id(db, score_data.id)
    if not existing_score:
        logger.warning("Service修改成绩失败: 记录不存在 id=%s", score_data.id)
        raise ValueError(f"成绩ID {score_data.id} 不存在")

    update_fields = score_data.model_dump(exclude_unset=True, exclude={"id"})

    target_student_id = existing_score.student_id
    target_exam_sequence = update_fields.get("exam_sequence", existing_score.exam_sequence)

    if "student_code" in update_fields:
        student = await scoreMapper.get_student_by_code(db, update_fields["student_code"])
        if not student:
            logger.warning("Service修改成绩失败: 学生不存在 student_code=%s", update_fields["student_code"])
            raise ValueError(f"学生编号 {update_fields['student_code']} 不存在")
        target_student_id = student.id
        update_fields["student_id"] = student.id
        del update_fields["student_code"]

    duplicate = await scoreMapper.get_score_by_student_and_exam(db, target_student_id, target_exam_sequence)
    if duplicate and duplicate.id != score_data.id:
        logger.warning(
            "Service修改成绩失败: 成绩记录冲突 student_id=%s, exam_sequence=%s",
            target_student_id, target_exam_sequence
        )
        raise ValueError(f"学生ID {target_student_id} 的 {target_exam_sequence} 成绩已存在")

    await scoreMapper.update_score(db, score_data.id, update_fields)
    result = await scoreMapper.get_score_detail_with_student(db, score_data.id)
    logger.info("Service修改成绩成功: id=%s", score_data.id)
    return ScoreResponse.model_validate(result)


async def delete_score(db: AsyncSession, score_id: int):
    logger.info("Service删除成绩: id=%s", score_id)
    existing_score = await scoreMapper.get_score_by_id(db, score_id)
    if not existing_score:
        logger.warning("Service删除成绩失败: 记录不存在 id=%s", score_id)
        raise ValueError(f"成绩ID {score_id} 不存在")

    result = await scoreMapper.delete_score(db, score_id)
    logger.info("Service删除成绩成功: id=%s", score_id)
    return result
