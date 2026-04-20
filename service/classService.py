from sqlalchemy.ext.asyncio import AsyncSession

from mapper import classMapper
from models.classInfo import ClassInfo
from schema.classSchema import ClassResponse, ClassQueryRequest, ClassRequest, ClassUpdateRequest
from utils.logger import AppLogger

logger = AppLogger.get_logger(__name__)


async def get_class(db: AsyncSession, page: int, page_size: int):
    logger.info("Service班级分页查询: page=%s, page_size=%s", page, page_size)
    skip = (page - 1) * page_size
    result = await classMapper.get_class(db, skip, page_size)
    logger.info("Service班级分页查询完成: count=%s", len(result))
    return [ClassResponse.model_validate(item) for item in result]


async def get_class_by_conditions(db: AsyncSession, query_params: ClassQueryRequest):
    logger.info("Service班级多条件查询: page=%s, page_size=%s", query_params.page, query_params.page_size)
    skip = (query_params.page - 1) * query_params.page_size
    result = await classMapper.get_class_by_conditions(db, query_params, skip, query_params.page_size)
    logger.info("Service班级多条件查询完成: count=%s", len(result))
    return [ClassResponse.model_validate(item) for item in result]


async def get_class_detail(db: AsyncSession, class_code: str):
    logger.info("Service班级详情查询: class_code=%s", class_code)
    result = await classMapper.get_class_by_code(db, class_code)
    if not result:
        logger.warning("Service班级详情查询失败: 班级不存在 class_code=%s", class_code)
        raise ValueError(f"班级编号 {class_code} 不存在")
    logger.info("Service班级详情查询成功: class_code=%s", class_code)
    return ClassResponse.model_validate(result)


async def create_class(db: AsyncSession, class_data: ClassRequest):
    logger.info("Service新增班级: class_code=%s", class_data.class_code)
    existing_class = await classMapper.get_class_by_code(db, class_data.class_code)
    if existing_class:
        logger.warning("Service新增班级失败: 班级编号已存在 class_code=%s", class_data.class_code)
        raise ValueError(f"班级编号 {class_data.class_code} 已存在")

    class_info = ClassInfo(
        class_code=class_data.class_code,
        start_date=class_data.start_date,
        head_teacher_id=class_data.head_teacher_id
    )
    result = await classMapper.create_class(db, class_info)
    logger.info("Service新增班级成功: class_code=%s", class_data.class_code)
    return ClassResponse.model_validate(result)


async def update_class(db: AsyncSession, class_data: ClassUpdateRequest):
    logger.info("Service修改班级: class_code=%s", class_data.class_code)
    existing_class = await classMapper.get_class_by_code(db, class_data.class_code)
    if not existing_class:
        logger.warning("Service修改班级失败: 班级不存在 class_code=%s", class_data.class_code)
        raise ValueError(f"班级编号 {class_data.class_code} 不存在")

    result = await classMapper.update_class(db, class_data)
    logger.info("Service修改班级成功: class_code=%s", class_data.class_code)
    return ClassResponse.model_validate(result)


async def delete_class(db: AsyncSession, class_code: str):
    logger.info("Service删除班级: class_code=%s", class_code)
    existing_class = await classMapper.get_class_by_code(db, class_code)
    if not existing_class:
        logger.warning("Service删除班级失败: 班级不存在 class_code=%s", class_code)
        raise ValueError(f"班级编号 {class_code} 不存在")

    result = await classMapper.delete_class(db, class_code)
    logger.info("Service删除班级成功: class_code=%s", class_code)
    return result

