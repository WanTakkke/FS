from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from models.classInfo import ClassInfo
from schema.classSchema import ClassUpdateRequest, ClassQueryRequest
from utils.logger import AppLogger

logger = AppLogger.get_logger(__name__)


async def get_class(db: AsyncSession, skip: int, limit: int):
    logger.info("Mapper班级分页查询: skip=%s, limit=%s", skip, limit)
    result = await db.execute(
        select(ClassInfo).where(ClassInfo.is_deleted == 0).offset(skip).limit(limit)
    )
    data = result.scalars().all()
    logger.info("Mapper班级分页查询完成: count=%s", len(data))
    return data


async def get_class_by_conditions(db: AsyncSession, query_params: ClassQueryRequest, skip: int, limit: int):
    logger.info("Mapper班级多条件查询: skip=%s, limit=%s", skip, limit)
    stmt = select(ClassInfo).where(ClassInfo.is_deleted == 0)

    if query_params.class_code:
        stmt = stmt.where(ClassInfo.class_code == query_params.class_code)
    if query_params.head_teacher_id is not None:
        stmt = stmt.where(ClassInfo.head_teacher_id == query_params.head_teacher_id)
    if query_params.start_date_start:
        stmt = stmt.where(ClassInfo.start_date >= query_params.start_date_start)
    if query_params.start_date_end:
        stmt = stmt.where(ClassInfo.start_date <= query_params.start_date_end)
    if query_params.keyword:
        stmt = stmt.where(or_(ClassInfo.class_code.like(f"%{query_params.keyword}%")))

    result = await db.execute(stmt.offset(skip).limit(limit))
    data = result.scalars().all()
    logger.info("Mapper班级多条件查询完成: count=%s", len(data))
    return data


async def get_class_by_code(db: AsyncSession, class_code: str):
    logger.info("Mapper按编号查询班级: class_code=%s", class_code)
    result = await db.execute(
        select(ClassInfo).where(ClassInfo.class_code == class_code).where(ClassInfo.is_deleted == 0)
    )
    data = result.scalar_one_or_none()
    logger.info("Mapper按编号查询班级完成: exists=%s", data is not None)
    return data


async def create_class(db: AsyncSession, class_info: ClassInfo):
    logger.info("Mapper新增班级: class_code=%s", class_info.class_code)
    try:
        db.add(class_info)
        await db.commit()
        await db.refresh(class_info)
        logger.info("Mapper新增班级成功: class_code=%s", class_info.class_code)
        return class_info
    except Exception:
        await db.rollback()
        logger.exception("Mapper新增班级异常: class_code=%s", class_info.class_code)
        raise


async def update_class(db: AsyncSession, class_data: ClassUpdateRequest):
    logger.info("Mapper修改班级: class_code=%s", class_data.class_code)
    existing_class = await get_class_by_code(db, class_data.class_code)
    if not existing_class:
        logger.warning("Mapper修改班级失败: 班级不存在 class_code=%s", class_data.class_code)
        return None

    update_fields = class_data.model_dump(exclude_unset=True, exclude={"class_code"})
    for field, value in update_fields.items():
        if hasattr(existing_class, field):
            setattr(existing_class, field, value)

    try:
        await db.commit()
        await db.refresh(existing_class)
        logger.info("Mapper修改班级成功: class_code=%s", class_data.class_code)
        return existing_class
    except Exception:
        await db.rollback()
        logger.exception("Mapper修改班级异常: class_code=%s", class_data.class_code)
        raise


async def delete_class(db: AsyncSession, class_code: str):
    logger.info("Mapper删除班级: class_code=%s", class_code)
    existing_class = await get_class_by_code(db, class_code)
    if not existing_class:
        logger.warning("Mapper删除班级失败: 班级不存在 class_code=%s", class_code)
        return False

    try:
        existing_class.is_deleted = 1
        await db.commit()
        logger.info("Mapper删除班级成功: class_code=%s", class_code)
        return True
    except Exception:
        await db.rollback()
        logger.exception("Mapper删除班级异常: class_code=%s", class_code)
        raise

