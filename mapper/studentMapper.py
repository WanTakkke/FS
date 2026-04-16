from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.studentInfo import StudentInfo


async def get_student(db: AsyncSession, skip: int = 0, limit: int=10):
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