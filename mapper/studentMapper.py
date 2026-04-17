from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.studentInfo import StudentInfo
from schema.studentSchema import StudentRequest


async def get_student(db: AsyncSession, skip: int, limit):
    result = await db.execute(select(StudentInfo).offset(skip).limit(limit))
    return result.scalars().all()


async def get_student_by_code(db: AsyncSession, student_code: str):
    result = await db.execute(select(StudentInfo).where(StudentInfo.student_code == student_code))
    return result.scalar_one_or_none()


async def create_student(db: AsyncSession, student: StudentInfo):
    db.add(student)
    await db.commit()
    await db.refresh(student)
    #返回StudentInfo 模型对象,orm模型对象
    return student


async def update_student(db: AsyncSession, student_data: StudentRequest):
    # 1. 根据 student_code 查询现有学生
    existing_student = await get_student_by_code(db, student_data.student_code)

    # 2. 逐个更新字段（除了 id 和 student_code）
    existing_student.class_id = student_data.class_id
    existing_student.advisor_id = student_data.advisor_id
    existing_student.name = student_data.name
    existing_student.gender = student_data.gender
    existing_student.age = student_data.age
    existing_student.hometown = student_data.hometown
    existing_student.graduate_school = student_data.graduate_school
    existing_student.major = student_data.major
    existing_student.enrollment_date = student_data.enrollment_date
    existing_student.graduation_date = student_data.graduation_date
    existing_student.education_level = student_data.education_level

    # 3. 提交并刷新
    await db.commit()
    await db.refresh(existing_student)

    # 4. 返回更新后的对象
    return existing_student