from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.classInfo import ClassInfo
from models.scoreInfo import ScoreInfo
from models.studentInfo import StudentInfo
from utils.logger import AppLogger

logger = AppLogger.get_logger(__name__)


async def get_score(db: AsyncSession, skip: int, limit: int):
    logger.info("Mapper成绩分页查询: skip=%s, limit=%s", skip, limit)
    stmt = (
        select(
            ScoreInfo.id,
            ClassInfo.class_code,
            StudentInfo.name.label("student_name"),
            ScoreInfo.exam_sequence,
            ScoreInfo.score
        )
        .select_from(ScoreInfo)
        .outerjoin(
            StudentInfo,
            (ScoreInfo.student_id == StudentInfo.id) & (StudentInfo.is_deleted == 0)
        )
        .outerjoin(
            ClassInfo,
            (StudentInfo.class_id == ClassInfo.id) & (ClassInfo.is_deleted == 0)
        )
        .where(ScoreInfo.is_deleted == 0)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    data = result.mappings().all()
    logger.info("Mapper成绩分页查询完成: count=%s", len(data))
    return data


async def get_score_by_conditions(db: AsyncSession, query_params, skip: int, limit: int):
    logger.info("Mapper成绩多条件查询: skip=%s, limit=%s", skip, limit)
    stmt = (
        select(
            ScoreInfo.id,
            ClassInfo.class_code,
            StudentInfo.name.label("student_name"),
            ScoreInfo.exam_sequence,
            ScoreInfo.score
        )
        .select_from(ScoreInfo)
        .outerjoin(
            StudentInfo,
            (ScoreInfo.student_id == StudentInfo.id) & (StudentInfo.is_deleted == 0)
        )
        .outerjoin(
            ClassInfo,
            (StudentInfo.class_id == ClassInfo.id) & (ClassInfo.is_deleted == 0)
        )
        .where(ScoreInfo.is_deleted == 0)
    )

    if query_params.student_name:
        stmt = stmt.where(StudentInfo.name.like(f"%{query_params.student_name}%"))
    if query_params.exam_sequence:
        stmt = stmt.where(ScoreInfo.exam_sequence == query_params.exam_sequence)
    if query_params.score_min is not None:
        stmt = stmt.where(ScoreInfo.score >= query_params.score_min)
    if query_params.score_max is not None:
        stmt = stmt.where(ScoreInfo.score <= query_params.score_max)

    result = await db.execute(stmt.offset(skip).limit(limit))
    data = result.mappings().all()
    logger.info("Mapper成绩多条件查询完成: count=%s", len(data))
    return data


async def get_score_by_id(db: AsyncSession, score_id: int):
    logger.info("Mapper按ID查询成绩: id=%s", score_id)
    result = await db.execute(
        select(ScoreInfo).where(ScoreInfo.id == score_id).where(ScoreInfo.is_deleted == 0)
    )
    data = result.scalar_one_or_none()
    logger.info("Mapper按ID查询成绩完成: exists=%s", data is not None)
    return data


async def get_score_detail_with_student(db: AsyncSession, score_id: int):
    logger.info("Mapper按ID查询成绩详情(含学生姓名): id=%s", score_id)
    stmt = (
        select(
            ScoreInfo.id,
            ClassInfo.class_code,
            StudentInfo.name.label("student_name"),
            ScoreInfo.exam_sequence,
            ScoreInfo.score
        )
        .select_from(ScoreInfo)
        .outerjoin(
            StudentInfo,
            (ScoreInfo.student_id == StudentInfo.id) & (StudentInfo.is_deleted == 0)
        )
        .outerjoin(
            ClassInfo,
            (StudentInfo.class_id == ClassInfo.id) & (ClassInfo.is_deleted == 0)
        )
        .where(ScoreInfo.is_deleted == 0, ScoreInfo.id == score_id)
    )
    result = await db.execute(stmt)
    data = result.mappings().first()
    logger.info("Mapper按ID查询成绩详情完成: exists=%s", data is not None)
    return data


async def get_student_by_id(db: AsyncSession, student_id: int):
    logger.info("Mapper按ID查询学生: student_id=%s", student_id)
    result = await db.execute(
        select(StudentInfo).where(StudentInfo.id == student_id).where(StudentInfo.is_deleted == 0)
    )
    data = result.scalar_one_or_none()
    logger.info("Mapper按ID查询学生完成: exists=%s", data is not None)
    return data


async def get_student_by_code(db: AsyncSession, student_code: str):
    logger.info("Mapper按编号查询学生: student_code=%s", student_code)
    result = await db.execute(
        select(StudentInfo).where(StudentInfo.student_code == student_code).where(StudentInfo.is_deleted == 0)
    )
    data = result.scalar_one_or_none()
    logger.info("Mapper按编号查询学生完成: exists=%s", data is not None)
    return data


async def get_students_by_name(db: AsyncSession, student_name: str):
    logger.info("Mapper按姓名查询学生: student_name=%s", student_name)
    result = await db.execute(
        select(StudentInfo).where(StudentInfo.name == student_name).where(StudentInfo.is_deleted == 0)
    )
    data = result.scalars().all()
    logger.info("Mapper按姓名查询学生完成: count=%s", len(data))
    return data


async def get_score_by_student_and_exam(db: AsyncSession, student_id: int, exam_sequence: str):
    logger.info("Mapper按学生和考核序次查询成绩: student_id=%s, exam_sequence=%s", student_id, exam_sequence)
    result = await db.execute(
        select(ScoreInfo).where(
            ScoreInfo.student_id == student_id,
            ScoreInfo.exam_sequence == exam_sequence,
            ScoreInfo.is_deleted == 0
        )
    )
    data = result.scalar_one_or_none()
    logger.info("Mapper按学生和考核序次查询完成: exists=%s", data is not None)
    return data


async def create_score(db: AsyncSession, score_info: ScoreInfo):
    logger.info("Mapper新增成绩: student_id=%s, exam_sequence=%s", score_info.student_id, score_info.exam_sequence)
    try:
        db.add(score_info)
        await db.commit()
        await db.refresh(score_info)
        logger.info("Mapper新增成绩成功: id=%s", score_info.id)
        return score_info
    except Exception:
        await db.rollback()
        logger.exception("Mapper新增成绩异常: student_id=%s, exam_sequence=%s", score_info.student_id, score_info.exam_sequence)
        raise


async def update_score(db: AsyncSession, score_id: int, update_fields: dict):
    logger.info("Mapper修改成绩: id=%s", score_id)
    existing_score = await get_score_by_id(db, score_id)
    if not existing_score:
        logger.warning("Mapper修改成绩失败: 记录不存在 id=%s", score_id)
        return None

    for field, value in update_fields.items():
        if hasattr(existing_score, field):
            setattr(existing_score, field, value)

    try:
        await db.commit()
        await db.refresh(existing_score)
        logger.info("Mapper修改成绩成功: id=%s", score_id)
        return existing_score
    except Exception:
        await db.rollback()
        logger.exception("Mapper修改成绩异常: id=%s", score_id)
        raise


async def delete_score(db: AsyncSession, score_id: int):
    logger.info("Mapper删除成绩: id=%s", score_id)
    existing_score = await get_score_by_id(db, score_id)
    if not existing_score:
        logger.warning("Mapper删除成绩失败: 记录不存在 id=%s", score_id)
        return False

    try:
        existing_score.is_deleted = 1
        await db.commit()
        logger.info("Mapper删除成绩成功: id=%s", score_id)
        return True
    except Exception:
        await db.rollback()
        logger.exception("Mapper删除成绩异常: id=%s", score_id)
        raise
