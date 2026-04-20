from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.studentInfo import StudentInfo


async def get_student(db: AsyncSession, skip: int, limit):
    result = await db.execute(select(StudentInfo).where(StudentInfo.is_deleted == 0).offset(skip).limit(limit))
    return result.scalars().all()


async def get_student_by_conditions(db: AsyncSession, query_params, skip: int, limit: int):
    stmt = select(StudentInfo).where(StudentInfo.is_deleted == 0)

    if query_params.student_code:
        stmt = stmt.where(StudentInfo.student_code == query_params.student_code)
    if query_params.name:
        stmt = stmt.where(StudentInfo.name.like(f"%{query_params.name}%"))
    if query_params.class_id is not None:
        stmt = stmt.where(StudentInfo.class_id == query_params.class_id)
    if query_params.advisor_id is not None:
        stmt = stmt.where(StudentInfo.advisor_id == query_params.advisor_id)
    if query_params.gender is not None:
        stmt = stmt.where(StudentInfo.gender == query_params.gender)
    if query_params.age_min is not None:
        stmt = stmt.where(StudentInfo.age >= query_params.age_min)
    if query_params.age_max is not None:
        stmt = stmt.where(StudentInfo.age <= query_params.age_max)
    if query_params.hometown:
        stmt = stmt.where(StudentInfo.hometown.like(f"%{query_params.hometown}%"))
    if query_params.graduate_school:
        stmt = stmt.where(StudentInfo.graduate_school.like(f"%{query_params.graduate_school}%"))
    if query_params.major:
        stmt = stmt.where(StudentInfo.major.like(f"%{query_params.major}%"))
    if query_params.education_level:
        stmt = stmt.where(StudentInfo.education_level == query_params.education_level)
    if query_params.enrollment_start_date:
        stmt = stmt.where(StudentInfo.enrollment_date >= query_params.enrollment_start_date)
    if query_params.enrollment_end_date:
        stmt = stmt.where(StudentInfo.enrollment_date <= query_params.enrollment_end_date)
    if query_params.graduation_start_date:
        stmt = stmt.where(StudentInfo.graduation_date >= query_params.graduation_start_date)
    if query_params.graduation_end_date:
        stmt = stmt.where(StudentInfo.graduation_date <= query_params.graduation_end_date)

    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_student_by_code(db: AsyncSession, student_code: str):
    result = await db.execute(select(StudentInfo).where(StudentInfo.student_code == student_code).where(StudentInfo.is_deleted == 0))
    return result.scalar_one_or_none()


async def create_student(db: AsyncSession, student: StudentInfo):
    db.add(student)
    await db.commit()
    await db.refresh(student)
    #返回StudentInfo 模型对象,orm模型对象
    return student


async def update_student(db: AsyncSession, student_data):
    # 根据 student_code 查询现有学生
    existing_student = await get_student_by_code(db, student_data.student_code)
    if not existing_student:
        return None

    # 只更新传入的非空字段
    update_fields = student_data.model_dump(exclude_unset=True, exclude={'student_code'})

    for field, value in update_fields.items():
        if hasattr(existing_student, field):
            setattr(existing_student, field, value)

    # 3. 提交并刷新
    await db.commit()
    await db.refresh(existing_student)

    # 4. 返回更新后的对象
    return existing_student


async def delete_student(db: AsyncSession, student_code: str):
    # 查询学生是否存在
    existing_student = await get_student_by_code(db, student_code)
    if not existing_student:
        return False

    # 删除记录
    existing_student.is_deleted = 1
    await db.commit()

    return True
