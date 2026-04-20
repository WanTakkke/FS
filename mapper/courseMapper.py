from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.courseInfo import CourseInfo
from schema.courseSchema import CourseQueryRequest
from utils.logger import AppLogger

logger = AppLogger.get_logger(__name__)


async def get_course(db: AsyncSession, skip: int, limit: int):
    logger.info("Mapper课程分页查询: skip=%s, limit=%s", skip, limit)
    stmt = (
        select(
            CourseInfo.course_code,
            CourseInfo.course_name,
            CourseInfo.description
        )
        .where(CourseInfo.is_deleted == 0)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    data = result.mappings().all()
    logger.info("Mapper课程分页查询完成: count=%s", len(data))
    return data


async def get_course_by_conditions(db: AsyncSession, query_params: CourseQueryRequest, skip: int, limit: int):
    logger.info("Mapper课程多条件查询: skip=%s, limit=%s", skip, limit)
    stmt = select(CourseInfo).where(CourseInfo.is_deleted == 0)

    if query_params.course_code:
        stmt = stmt.where(CourseInfo.course_code == query_params.course_code)
    if query_params.course_name:
        stmt = stmt.where(CourseInfo.course_name.like(f"%{query_params.course_name}%"))

    result = await db.execute(stmt.offset(skip).limit(limit))
    data = result.scalars().all()
    logger.info("Mapper课程多条件查询完成: count=%s", len(data))
    return data


async def get_course_by_code(db: AsyncSession, course_code: str):
    logger.info("Mapper按编号查询课程: course_code=%s", course_code)
    result = await db.execute(
        select(CourseInfo).where(CourseInfo.course_code == course_code).where(CourseInfo.is_deleted == 0)
    )
    data = result.scalar_one_or_none()
    logger.info("Mapper按编号查询课程完成: exists=%s", data is not None)
    return data


async def create_course(db: AsyncSession, course_info: CourseInfo):
    logger.info("Mapper新增课程: course_code=%s", course_info.course_code)
    try:
        db.add(course_info)
        await db.commit()
        await db.refresh(course_info)
        logger.info("Mapper新增课程成功: course_code=%s", course_info.course_code)
        return course_info
    except Exception:
        await db.rollback()
        logger.exception("Mapper新增课程异常: course_code=%s", course_info.course_code)
        raise


async def update_course(db: AsyncSession, course_code: str, update_fields: dict):
    logger.info("Mapper修改课程: course_code=%s", course_code)
    existing = await get_course_by_code(db, course_code)
    if not existing:
        logger.warning("Mapper修改课程失败: 课程不存在 course_code=%s", course_code)
        return None

    for field, value in update_fields.items():
        if hasattr(existing, field):
            setattr(existing, field, value)

    try:
        await db.commit()
        await db.refresh(existing)
        logger.info("Mapper修改课程成功: course_code=%s", course_code)
        return existing
    except Exception:
        await db.rollback()
        logger.exception("Mapper修改课程异常: course_code=%s", course_code)
        raise


async def delete_course(db: AsyncSession, course_code: str):
    logger.info("Mapper删除课程: course_code=%s", course_code)
    existing = await get_course_by_code(db, course_code)
    if not existing:
        logger.warning("Mapper删除课程失败: 课程不存在 course_code=%s", course_code)
        return False

    try:
        existing.is_deleted = 1
        await db.commit()
        logger.info("Mapper删除课程成功: course_code=%s", course_code)
        return True
    except Exception:
        await db.rollback()
        logger.exception("Mapper删除课程异常: course_code=%s", course_code)
        raise

