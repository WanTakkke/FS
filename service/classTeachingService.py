from sqlalchemy.ext.asyncio import AsyncSession

from mapper import classTeachingMapper
from models.classTeachingPeriodInfo import ClassTeachingPeriodInfo
from schema.classTeachingSchema import (
    ClassTeachingResponse,
    ClassTeachingRequest,
    ClassTeachingUpdateRequest,
    ClassTeachingQueryRequest,
)
from utils.logger import AppLogger

logger = AppLogger.get_logger(__name__)


async def get_class_teaching(db: AsyncSession, page: int, page_size: int):
    logger.info("Service班级授课分页查询: page=%s, page_size=%s", page, page_size)
    skip = (page - 1) * page_size
    result = await classTeachingMapper.get_class_teaching(db, skip, page_size)
    logger.info("Service班级授课分页查询完成: count=%s", len(result))
    return [ClassTeachingResponse.model_validate(item) for item in result]


async def get_class_teaching_by_conditions(db: AsyncSession, query_params: ClassTeachingQueryRequest):
    logger.info("Service班级授课多条件查询: page=%s, page_size=%s", query_params.page, query_params.page_size)
    skip = (query_params.page - 1) * query_params.page_size
    result = await classTeachingMapper.get_class_teaching_by_conditions(db, query_params, skip, query_params.page_size)
    logger.info("Service班级授课多条件查询完成: count=%s", len(result))
    return [ClassTeachingResponse.model_validate(item) for item in result]


async def get_class_teaching_detail(db: AsyncSession, teaching_id: int):
    logger.info("Service班级授课详情查询: id=%s", teaching_id)
    result = await classTeachingMapper.get_class_teaching_detail(db, teaching_id)
    if not result:
        logger.warning("Service班级授课详情查询失败: 记录不存在 id=%s", teaching_id)
        raise ValueError(f"班级授课记录ID {teaching_id} 不存在")
    logger.info("Service班级授课详情查询成功: id=%s", teaching_id)
    return ClassTeachingResponse.model_validate(result)


async def create_class_teaching(db: AsyncSession, teaching_data: ClassTeachingRequest):
    logger.info(
        "Service新增班级授课: class_code=%s, lecturer_code=%s, course_code=%s",
        teaching_data.class_code, teaching_data.lecturer_code, teaching_data.course_code
    )

    class_info = await classTeachingMapper.get_class_by_code(db, teaching_data.class_code)
    if not class_info:
        logger.warning("Service新增班级授课失败: 班级不存在 class_code=%s", teaching_data.class_code)
        raise ValueError(f"班级编号 {teaching_data.class_code} 不存在")

    teacher_info = await classTeachingMapper.get_teacher_by_code(db, teaching_data.lecturer_code)
    if not teacher_info:
        logger.warning("Service新增班级授课失败: 老师不存在 lecturer_code=%s", teaching_data.lecturer_code)
        raise ValueError(f"老师编号 {teaching_data.lecturer_code} 不存在")

    course_info = await classTeachingMapper.get_course_by_code(db, teaching_data.course_code)
    if not course_info:
        logger.warning("Service新增班级授课失败: 课程不存在 course_code=%s", teaching_data.course_code)
        raise ValueError(f"课程编号 {teaching_data.course_code} 不存在")

    duplicate = await classTeachingMapper.get_teaching_by_unique_key(
        db, class_info.id, teacher_info.id, course_info.id, teaching_data.start_date
    )
    if duplicate:
        logger.warning("Service新增班级授课失败: 记录已存在")
        raise ValueError("相同班级、老师、课程、开始日期的授课记录已存在")

    teaching_info = ClassTeachingPeriodInfo(
        class_id=class_info.id,
        lecturer_id=teacher_info.id,
        course_id=course_info.id,
        start_date=teaching_data.start_date,
        end_date=teaching_data.end_date
    )
    created = await classTeachingMapper.create_class_teaching(db, teaching_info)
    result = await classTeachingMapper.get_class_teaching_detail(db, created.id)
    logger.info("Service新增班级授课成功: id=%s", created.id)
    return ClassTeachingResponse.model_validate(result)


async def update_class_teaching(db: AsyncSession, teaching_data: ClassTeachingUpdateRequest):
    logger.info("Service修改班级授课: id=%s", teaching_data.id)
    existing = await classTeachingMapper.get_class_teaching_by_id(db, teaching_data.id)
    if not existing:
        logger.warning("Service修改班级授课失败: 记录不存在 id=%s", teaching_data.id)
        raise ValueError(f"班级授课记录ID {teaching_data.id} 不存在")

    update_fields = teaching_data.model_dump(exclude_unset=True, exclude={"id"})

    target_class_id = existing.class_id
    target_lecturer_id = existing.lecturer_id
    target_course_id = existing.course_id
    target_start_date = update_fields.get("start_date", existing.start_date)

    if "class_code" in update_fields:
        class_info = await classTeachingMapper.get_class_by_code(db, update_fields["class_code"])
        if not class_info:
            logger.warning("Service修改班级授课失败: 班级不存在 class_code=%s", update_fields["class_code"])
            raise ValueError(f"班级编号 {update_fields['class_code']} 不存在")
        target_class_id = class_info.id
        update_fields["class_id"] = class_info.id
        del update_fields["class_code"]

    if "lecturer_code" in update_fields:
        teacher_info = await classTeachingMapper.get_teacher_by_code(db, update_fields["lecturer_code"])
        if not teacher_info:
            logger.warning("Service修改班级授课失败: 老师不存在 lecturer_code=%s", update_fields["lecturer_code"])
            raise ValueError(f"老师编号 {update_fields['lecturer_code']} 不存在")
        target_lecturer_id = teacher_info.id
        update_fields["lecturer_id"] = teacher_info.id
        del update_fields["lecturer_code"]

    if "course_code" in update_fields:
        course_info = await classTeachingMapper.get_course_by_code(db, update_fields["course_code"])
        if not course_info:
            logger.warning("Service修改班级授课失败: 课程不存在 course_code=%s", update_fields["course_code"])
            raise ValueError(f"课程编号 {update_fields['course_code']} 不存在")
        target_course_id = course_info.id
        update_fields["course_id"] = course_info.id
        del update_fields["course_code"]

    if "start_date" in update_fields and "end_date" in update_fields:
        if update_fields["end_date"] is not None and update_fields["start_date"] > update_fields["end_date"]:
            raise ValueError("start_date 不能大于 end_date")
    elif "start_date" in update_fields:
        target_end = update_fields.get("end_date", existing.end_date)
        if target_end is not None and update_fields["start_date"] > target_end:
            raise ValueError("start_date 不能大于 end_date")
    elif "end_date" in update_fields:
        if update_fields["end_date"] is not None and existing.start_date > update_fields["end_date"]:
            raise ValueError("start_date 不能大于 end_date")

    duplicate = await classTeachingMapper.get_teaching_by_unique_key(
        db, target_class_id, target_lecturer_id, target_course_id, target_start_date
    )
    if duplicate and duplicate.id != teaching_data.id:
        logger.warning("Service修改班级授课失败: 记录冲突 id=%s", teaching_data.id)
        raise ValueError("修改后的授课记录与已有记录冲突")

    await classTeachingMapper.update_class_teaching(db, teaching_data.id, update_fields)
    result = await classTeachingMapper.get_class_teaching_detail(db, teaching_data.id)
    logger.info("Service修改班级授课成功: id=%s", teaching_data.id)
    return ClassTeachingResponse.model_validate(result)


async def delete_class_teaching(db: AsyncSession, teaching_id: int):
    logger.info("Service删除班级授课: id=%s", teaching_id)
    existing = await classTeachingMapper.get_class_teaching_by_id(db, teaching_id)
    if not existing:
        logger.warning("Service删除班级授课失败: 记录不存在 id=%s", teaching_id)
        raise ValueError(f"班级授课记录ID {teaching_id} 不存在")

    result = await classTeachingMapper.delete_class_teaching(db, teaching_id)
    logger.info("Service删除班级授课成功: id=%s", teaching_id)
    return result

