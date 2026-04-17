from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.studentInfo import StudentInfo


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