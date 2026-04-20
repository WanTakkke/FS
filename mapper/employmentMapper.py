from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.classInfo import ClassInfo
from models.employmentInfo import EmploymentInfo
from models.studentInfo import StudentInfo
from utils.logger import AppLogger

logger = AppLogger.get_logger(__name__)


def _employment_query_stmt():
    return (
        select(
            StudentInfo.student_code,
            StudentInfo.name.label("student_name"),
            ClassInfo.class_code,
            EmploymentInfo.company_name,
            EmploymentInfo.job_open_date,
            EmploymentInfo.offer_date,
            EmploymentInfo.salary,
            EmploymentInfo.is_current.label("is_latest_employment")
        )
        .select_from(EmploymentInfo)
        .outerjoin(
            StudentInfo,
            (EmploymentInfo.student_id == StudentInfo.id) & (StudentInfo.is_deleted == 0)
        )
        .outerjoin(
            ClassInfo,
            (StudentInfo.class_id == ClassInfo.id) & (ClassInfo.is_deleted == 0)
        )
        .where(EmploymentInfo.is_deleted == 0)
    )


async def get_employment(db: AsyncSession, skip: int, limit: int):
    logger.info("Mapper就业分页查询: skip=%s, limit=%s", skip, limit)
    result = await db.execute(_employment_query_stmt().offset(skip).limit(limit))
    data = result.mappings().all()
    logger.info("Mapper就业分页查询完成: count=%s", len(data))
    return data


async def get_employment_by_conditions(db: AsyncSession, query_params, skip: int, limit: int):
    logger.info("Mapper就业多条件查询: skip=%s, limit=%s", skip, limit)
    stmt = _employment_query_stmt()

    if query_params.student_code:
        stmt = stmt.where(StudentInfo.student_code == query_params.student_code)
    if query_params.student_name:
        stmt = stmt.where(StudentInfo.name.like(f"%{query_params.student_name}%"))
    if query_params.company_name:
        stmt = stmt.where(EmploymentInfo.company_name.like(f"%{query_params.company_name}%"))
    if query_params.is_latest_employment is not None:
        stmt = stmt.where(EmploymentInfo.is_current == int(query_params.is_latest_employment))
    if query_params.salary_min is not None:
        stmt = stmt.where(EmploymentInfo.salary >= query_params.salary_min)
    if query_params.salary_max is not None:
        stmt = stmt.where(EmploymentInfo.salary <= query_params.salary_max)
    if query_params.job_open_start:
        stmt = stmt.where(EmploymentInfo.job_open_date >= query_params.job_open_start)
    if query_params.job_open_end:
        stmt = stmt.where(EmploymentInfo.job_open_date <= query_params.job_open_end)
    if query_params.offer_start:
        stmt = stmt.where(EmploymentInfo.offer_date >= query_params.offer_start)
    if query_params.offer_end:
        stmt = stmt.where(EmploymentInfo.offer_date <= query_params.offer_end)

    result = await db.execute(stmt.offset(skip).limit(limit))
    data = result.mappings().all()
    logger.info("Mapper就业多条件查询完成: count=%s", len(data))
    return data


async def get_employment_by_id(db: AsyncSession, employment_id: int):
    logger.info("Mapper按ID查询就业记录: id=%s", employment_id)
    result = await db.execute(
        select(EmploymentInfo).where(EmploymentInfo.id == employment_id).where(EmploymentInfo.is_deleted == 0)
    )
    data = result.scalar_one_or_none()
    logger.info("Mapper按ID查询就业记录完成: exists=%s", data is not None)
    return data


async def get_employment_detail(db: AsyncSession, employment_id: int):
    logger.info("Mapper按ID查询就业详情: id=%s", employment_id)
    result = await db.execute(_employment_query_stmt().where(EmploymentInfo.id == employment_id))
    data = result.mappings().first()
    logger.info("Mapper按ID查询就业详情完成: exists=%s", data is not None)
    return data


async def get_student_by_code(db: AsyncSession, student_code: str):
    logger.info("Mapper按编号查询学生: student_code=%s", student_code)
    result = await db.execute(
        select(StudentInfo).where(StudentInfo.student_code == student_code).where(StudentInfo.is_deleted == 0)
    )
    data = result.scalar_one_or_none()
    logger.info("Mapper按编号查询学生完成: exists=%s", data is not None)
    return data


async def get_employment_by_unique_key(db: AsyncSession, student_id: int, company_name: str, job_open_date):
    logger.info("Mapper按业务键查询就业记录: student_id=%s, company_name=%s", student_id, company_name)
    result = await db.execute(
        select(EmploymentInfo).where(
            EmploymentInfo.student_id == student_id,
            EmploymentInfo.company_name == company_name,
            EmploymentInfo.job_open_date == job_open_date,
            EmploymentInfo.is_deleted == 0
        )
    )
    data = result.scalar_one_or_none()
    logger.info("Mapper按业务键查询就业记录完成: exists=%s", data is not None)
    return data


async def clear_current_employment(db: AsyncSession, student_id: int, exclude_id: int | None = None):
    logger.info("Mapper清理当前就业标记: student_id=%s, exclude_id=%s", student_id, exclude_id)
    stmt = (
        update(EmploymentInfo)
        .where(EmploymentInfo.student_id == student_id, EmploymentInfo.is_deleted == 0)
        .values(is_current=0)
    )
    if exclude_id is not None:
        stmt = stmt.where(EmploymentInfo.id != exclude_id)
    await db.execute(stmt)


async def create_employment(db: AsyncSession, employment_info: EmploymentInfo):
    logger.info("Mapper新增就业记录: student_id=%s, company_name=%s", employment_info.student_id, employment_info.company_name)
    try:
        db.add(employment_info)
        await db.commit()
        await db.refresh(employment_info)
        logger.info("Mapper新增就业记录成功: id=%s", employment_info.id)
        return employment_info
    except Exception:
        await db.rollback()
        logger.exception("Mapper新增就业记录异常: student_id=%s", employment_info.student_id)
        raise


async def update_employment(db: AsyncSession, employment_id: int, update_fields: dict):
    logger.info("Mapper修改就业记录: id=%s", employment_id)
    existing = await get_employment_by_id(db, employment_id)
    if not existing:
        logger.warning("Mapper修改就业记录失败: 记录不存在 id=%s", employment_id)
        return None

    for field, value in update_fields.items():
        if hasattr(existing, field):
            setattr(existing, field, value)

    try:
        await db.commit()
        await db.refresh(existing)
        logger.info("Mapper修改就业记录成功: id=%s", employment_id)
        return existing
    except Exception:
        await db.rollback()
        logger.exception("Mapper修改就业记录异常: id=%s", employment_id)
        raise


async def delete_employment(db: AsyncSession, employment_id: int):
    logger.info("Mapper删除就业记录: id=%s", employment_id)
    existing = await get_employment_by_id(db, employment_id)
    if not existing:
        logger.warning("Mapper删除就业记录失败: 记录不存在 id=%s", employment_id)
        return False

    try:
        existing.is_deleted = 1
        await db.commit()
        logger.info("Mapper删除就业记录成功: id=%s", employment_id)
        return True
    except Exception:
        await db.rollback()
        logger.exception("Mapper删除就业记录异常: id=%s", employment_id)
        raise
