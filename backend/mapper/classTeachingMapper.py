from sqlalchemy import select, case
from sqlalchemy.ext.asyncio import AsyncSession

from models.classInfo import ClassInfo
from models.classTeachingPeriodInfo import ClassTeachingPeriodInfo
from models.courseInfo import CourseInfo
from models.teacherInfo import TeacherInfo
from utils.logger import AppLogger

logger = AppLogger.get_logger(__name__)


def _teaching_query_stmt():
    return (
        select(
            ClassTeachingPeriodInfo.id,
            ClassInfo.class_code,
            TeacherInfo.teacher_code.label("lecturer_code"),
            TeacherInfo.name.label("lecturer_name"),
            CourseInfo.course_code,
            CourseInfo.course_name,
            ClassTeachingPeriodInfo.start_date,
            ClassTeachingPeriodInfo.end_date,
            case((ClassTeachingPeriodInfo.end_date.is_(None), 1), else_=0).label("is_current_teaching")
        )
        .select_from(ClassTeachingPeriodInfo)
        .outerjoin(
            ClassInfo,
            (ClassTeachingPeriodInfo.class_id == ClassInfo.id) & (ClassInfo.is_deleted == 0)
        )
        .outerjoin(
            TeacherInfo,
            (ClassTeachingPeriodInfo.lecturer_id == TeacherInfo.id) & (TeacherInfo.is_deleted == 0)
        )
        .outerjoin(
            CourseInfo,
            (ClassTeachingPeriodInfo.course_id == CourseInfo.id) & (CourseInfo.is_deleted == 0)
        )
        .where(ClassTeachingPeriodInfo.is_deleted == 0)
    )


async def get_class_teaching(db: AsyncSession, skip: int, limit: int):
    logger.info("Mapper班级授课分页查询: skip=%s, limit=%s", skip, limit)
    result = await db.execute(_teaching_query_stmt().offset(skip).limit(limit))
    data = result.mappings().all()
    logger.info("Mapper班级授课分页查询完成: count=%s", len(data))
    return data


async def get_class_teaching_by_conditions(db: AsyncSession, query_params, skip: int, limit: int):
    logger.info("Mapper班级授课多条件查询: skip=%s, limit=%s", skip, limit)
    stmt = _teaching_query_stmt()

    if query_params.class_code:
        stmt = stmt.where(ClassInfo.class_code == query_params.class_code)
    if query_params.lecturer_code:
        stmt = stmt.where(TeacherInfo.teacher_code == query_params.lecturer_code)
    if query_params.lecturer_name:
        stmt = stmt.where(TeacherInfo.name.like(f"%{query_params.lecturer_name}%"))
    if query_params.course_code:
        stmt = stmt.where(CourseInfo.course_code == query_params.course_code)
    if query_params.course_name:
        stmt = stmt.where(CourseInfo.course_name.like(f"%{query_params.course_name}%"))
    if query_params.start_date_start:
        stmt = stmt.where(ClassTeachingPeriodInfo.start_date >= query_params.start_date_start)
    if query_params.start_date_end:
        stmt = stmt.where(ClassTeachingPeriodInfo.start_date <= query_params.start_date_end)
    if query_params.end_date_start:
        stmt = stmt.where(ClassTeachingPeriodInfo.end_date >= query_params.end_date_start)
    if query_params.end_date_end:
        stmt = stmt.where(ClassTeachingPeriodInfo.end_date <= query_params.end_date_end)
    if query_params.is_current_teaching is not None:
        if query_params.is_current_teaching:
            stmt = stmt.where(ClassTeachingPeriodInfo.end_date.is_(None))
        else:
            stmt = stmt.where(ClassTeachingPeriodInfo.end_date.is_not(None))

    result = await db.execute(stmt.offset(skip).limit(limit))
    data = result.mappings().all()
    logger.info("Mapper班级授课多条件查询完成: count=%s", len(data))
    return data


async def get_class_teaching_by_id(db: AsyncSession, teaching_id: int):
    logger.info("Mapper按ID查询班级授课: id=%s", teaching_id)
    result = await db.execute(
        select(ClassTeachingPeriodInfo)
        .where(ClassTeachingPeriodInfo.id == teaching_id)
        .where(ClassTeachingPeriodInfo.is_deleted == 0)
    )
    data = result.scalar_one_or_none()
    logger.info("Mapper按ID查询班级授课完成: exists=%s", data is not None)
    return data


async def get_class_teaching_detail(db: AsyncSession, teaching_id: int):
    logger.info("Mapper按ID查询班级授课详情: id=%s", teaching_id)
    result = await db.execute(_teaching_query_stmt().where(ClassTeachingPeriodInfo.id == teaching_id))
    data = result.mappings().first()
    logger.info("Mapper按ID查询班级授课详情完成: exists=%s", data is not None)
    return data


async def get_class_by_code(db: AsyncSession, class_code: str):
    logger.info("Mapper按编号查询班级: class_code=%s", class_code)
    result = await db.execute(
        select(ClassInfo).where(ClassInfo.class_code == class_code).where(ClassInfo.is_deleted == 0)
    )
    data = result.scalar_one_or_none()
    logger.info("Mapper按编号查询班级完成: exists=%s", data is not None)
    return data


async def get_teacher_by_code(db: AsyncSession, lecturer_code: str):
    logger.info("Mapper按编号查询老师: lecturer_code=%s", lecturer_code)
    result = await db.execute(
        select(TeacherInfo).where(TeacherInfo.teacher_code == lecturer_code).where(TeacherInfo.is_deleted == 0)
    )
    data = result.scalar_one_or_none()
    logger.info("Mapper按编号查询老师完成: exists=%s", data is not None)
    return data


async def get_course_by_code(db: AsyncSession, course_code: str):
    logger.info("Mapper按编号查询课程: course_code=%s", course_code)
    result = await db.execute(
        select(CourseInfo).where(CourseInfo.course_code == course_code).where(CourseInfo.is_deleted == 0)
    )
    data = result.scalar_one_or_none()
    logger.info("Mapper按编号查询课程完成: exists=%s", data is not None)
    return data


async def get_teaching_by_unique_key(db: AsyncSession, class_id: int, lecturer_id: int, course_id: int, start_date):
    logger.info(
        "Mapper按业务键查询班级授课: class_id=%s, lecturer_id=%s, course_id=%s",
        class_id, lecturer_id, course_id
    )
    result = await db.execute(
        select(ClassTeachingPeriodInfo).where(
            ClassTeachingPeriodInfo.class_id == class_id,
            ClassTeachingPeriodInfo.lecturer_id == lecturer_id,
            ClassTeachingPeriodInfo.course_id == course_id,
            ClassTeachingPeriodInfo.start_date == start_date,
            ClassTeachingPeriodInfo.is_deleted == 0
        )
    )
    data = result.scalar_one_or_none()
    logger.info("Mapper按业务键查询班级授课完成: exists=%s", data is not None)
    return data


async def create_class_teaching(db: AsyncSession, teaching_info: ClassTeachingPeriodInfo):
    logger.info("Mapper新增班级授课: class_id=%s, lecturer_id=%s", teaching_info.class_id, teaching_info.lecturer_id)
    try:
        db.add(teaching_info)
        await db.commit()
        await db.refresh(teaching_info)
        logger.info("Mapper新增班级授课成功: id=%s", teaching_info.id)
        return teaching_info
    except Exception:
        await db.rollback()
        logger.exception("Mapper新增班级授课异常: class_id=%s", teaching_info.class_id)
        raise


async def update_class_teaching(db: AsyncSession, teaching_id: int, update_fields: dict):
    logger.info("Mapper修改班级授课: id=%s", teaching_id)
    existing = await get_class_teaching_by_id(db, teaching_id)
    if not existing:
        logger.warning("Mapper修改班级授课失败: 记录不存在 id=%s", teaching_id)
        return None

    for field, value in update_fields.items():
        if hasattr(existing, field):
            setattr(existing, field, value)

    try:
        await db.commit()
        await db.refresh(existing)
        logger.info("Mapper修改班级授课成功: id=%s", teaching_id)
        return existing
    except Exception:
        await db.rollback()
        logger.exception("Mapper修改班级授课异常: id=%s", teaching_id)
        raise


async def delete_class_teaching(db: AsyncSession, teaching_id: int):
    logger.info("Mapper删除班级授课: id=%s", teaching_id)
    existing = await get_class_teaching_by_id(db, teaching_id)
    if not existing:
        logger.warning("Mapper删除班级授课失败: 记录不存在 id=%s", teaching_id)
        return False

    try:
        existing.is_deleted = 1
        await db.commit()
        logger.info("Mapper删除班级授课成功: id=%s", teaching_id)
        return True
    except Exception:
        await db.rollback()
        logger.exception("Mapper删除班级授课异常: id=%s", teaching_id)
        raise

