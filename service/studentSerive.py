from sqlalchemy.ext.asyncio import AsyncSession

from mapper import studentMapper
from models.studentInfo import StudentInfo
from schema.studentSchema import StudentResponse


async def get_student(db: AsyncSession, page: int, page_size):
    skip = (page - 1) * page_size
    result = await studentMapper.get_student(db, skip, page_size)
    return [StudentResponse.model_validate(item) for item in result]


async def create_student(db: AsyncSession, student_data):
    # 先检查学生编号是否已存在
    existing_student = await studentMapper.get_student_by_code(db, student_data.student_code)
    if existing_student:
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
    return StudentResponse.model_validate(result)


async def update_student(db: AsyncSession, student_data):
    # 先检查学生编号是否已存在
    existing_student = await studentMapper.get_student_by_code(db, student_data.student_code)
    if not existing_student:
        raise ValueError(f"学生编号 {student_data.student_code} 不存在")

    result = await studentMapper.update_student(db, student_data)
    return StudentResponse.model_validate(result)