from sqlalchemy.ext.asyncio import AsyncSession

from mapper import studentMapper
from models.studentInfo import StudentInfo
from schema.studentSchema import StudentResponse
from utils.logger import AppLogger

logger = AppLogger.get_logger(__name__)


async def get_student(db: AsyncSession, page: int, page_size):
    logger.info("Service学生分页查询: page=%s, page_size=%s", page, page_size)
    skip = (page - 1) * page_size
    result = await studentMapper.get_student(db, skip, page_size)
    logger.info("Service学生分页查询完成: count=%s", len(result))
    return [StudentResponse.model_validate(item) for item in result]


async def get_student_by_conditions(db: AsyncSession, query_params):
    logger.info("Service学生多条件查询: page=%s, page_size=%s", query_params.page, query_params.page_size)
    skip = (query_params.page - 1) * query_params.page_size
    result = await studentMapper.get_student_by_conditions(db, query_params, skip, query_params.page_size)
    logger.info("Service学生多条件查询完成: count=%s", len(result))
    return [StudentResponse.model_validate(item) for item in result]


async def create_student(db: AsyncSession, student_data):
    logger.info("Service新增学生: student_code=%s", student_data.student_code)
    # 先检查学生编号是否已存在
    existing_student = await studentMapper.get_student_by_code(db, student_data.student_code)
    if existing_student:
        logger.warning("Service新增学生失败: 学生编号已存在 student_code=%s", student_data.student_code)
        raise ValueError(f"学生编号 {student_data.student_code} 已存在")
    
    # 不存在则创建新学生
    student = StudentInfo(
        student_code=student_data.student_code,
        class_id=student_data.class_id,
        advisor_id=student_data.advisor_id,
        name=student_data.name,
        gender=student_data.gender,
        age=student_data.age,
        hometown=student_data.hometown,
        graduate_school=student_data.graduate_school,
        major=student_data.major,
        enrollment_date=student_data.enrollment_date,
        graduation_date=student_data.graduation_date,
        education_level=student_data.education_level
    )
    result = await studentMapper.create_student(db, student)
    logger.info("Service新增学生成功: student_code=%s", student_data.student_code)
    return StudentResponse.model_validate(result)


async def update_student(db: AsyncSession, student_data):
    logger.info("Service修改学生: student_code=%s", student_data.student_code)
    # 先检查学生编号是否已存在
    existing_student = await studentMapper.get_student_by_code(db, student_data.student_code)
    if not existing_student:
        logger.warning("Service修改学生失败: 学生不存在 student_code=%s", student_data.student_code)
        raise ValueError(f"学生编号 {student_data.student_code} 不存在")

    result = await studentMapper.update_student(db, student_data)
    logger.info("Service修改学生成功: student_code=%s", student_data.student_code)
    return StudentResponse.model_validate(result)


async def delete_student(db: AsyncSession, student_code: str):
    logger.info("Service删除学生: student_code=%s", student_code)
    # 先检查学生是否存在
    existing_student = await studentMapper.get_student_by_code(db, student_code)
    if not existing_student:
        logger.warning("Service删除学生失败: 学生不存在 student_code=%s", student_code)
        raise ValueError(f"学生编号 {student_code} 不存在")

    # 执行删除
    result = await studentMapper.delete_student(db, student_code)
    logger.info("Service删除学生成功: student_code=%s", student_code)
    return result
