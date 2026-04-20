from sqlalchemy.ext.asyncio import AsyncSession

from mapper import courseMapper
from models.courseInfo import CourseInfo
from schema.courseSchema import CourseResponse, CourseRequest, CourseUpdateRequest, CourseQueryRequest
from utils.logger import AppLogger

logger = AppLogger.get_logger(__name__)


async def get_course(db: AsyncSession, page: int, page_size: int):
    logger.info("Service课程分页查询: page=%s, page_size=%s", page, page_size)
    skip = (page - 1) * page_size
    result = await courseMapper.get_course(db, skip, page_size)
    logger.info("Service课程分页查询完成: count=%s", len(result))
    return [CourseResponse.model_validate(item) for item in result]


async def get_course_by_conditions(db: AsyncSession, query_params: CourseQueryRequest):
    logger.info("Service课程多条件查询: page=%s, page_size=%s", query_params.page, query_params.page_size)
    skip = (query_params.page - 1) * query_params.page_size
    result = await courseMapper.get_course_by_conditions(db, query_params, skip, query_params.page_size)
    logger.info("Service课程多条件查询完成: count=%s", len(result))
    return [CourseResponse.model_validate(item) for item in result]


async def get_course_detail(db: AsyncSession, course_code: str):
    logger.info("Service课程详情查询: course_code=%s", course_code)
    result = await courseMapper.get_course_by_code(db, course_code)
    if not result:
        logger.warning("Service课程详情查询失败: 课程不存在 course_code=%s", course_code)
        raise ValueError(f"课程编号 {course_code} 不存在")
    logger.info("Service课程详情查询成功: course_code=%s", course_code)
    return CourseResponse.model_validate(result)


async def create_course(db: AsyncSession, course_data: CourseRequest):
    logger.info("Service新增课程: course_code=%s", course_data.course_code)
    existing = await courseMapper.get_course_by_code(db, course_data.course_code)
    if existing:
        logger.warning("Service新增课程失败: 课程编号已存在 course_code=%s", course_data.course_code)
        raise ValueError(f"课程编号 {course_data.course_code} 已存在")

    course_info = CourseInfo(
        course_code=course_data.course_code,
        course_name=course_data.course_name,
        description=course_data.description
    )
    result = await courseMapper.create_course(db, course_info)
    logger.info("Service新增课程成功: course_code=%s", course_data.course_code)
    return CourseResponse.model_validate(result)


async def update_course(db: AsyncSession, course_data: CourseUpdateRequest):
    logger.info("Service修改课程: course_code=%s", course_data.course_code)
    existing = await courseMapper.get_course_by_code(db, course_data.course_code)
    if not existing:
        logger.warning("Service修改课程失败: 课程不存在 course_code=%s", course_data.course_code)
        raise ValueError(f"课程编号 {course_data.course_code} 不存在")

    update_fields = course_data.model_dump(exclude_unset=True, exclude={"course_code"})
    await courseMapper.update_course(db, course_data.course_code, update_fields)
    result = await courseMapper.get_course_by_code(db, course_data.course_code)
    logger.info("Service修改课程成功: course_code=%s", course_data.course_code)
    return CourseResponse.model_validate(result)


async def delete_course(db: AsyncSession, course_code: str):
    logger.info("Service删除课程: course_code=%s", course_code)
    existing = await courseMapper.get_course_by_code(db, course_code)
    if not existing:
        logger.warning("Service删除课程失败: 课程不存在 course_code=%s", course_code)
        raise ValueError(f"课程编号 {course_code} 不存在")

    result = await courseMapper.delete_course(db, course_code)
    logger.info("Service删除课程成功: course_code=%s", course_code)
    return result

