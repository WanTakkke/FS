from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.studentInfo import StudentInfo


async def get_student(db: AsyncSession, skip: int = 0, limit: int=10):
    result = await db.execute(select(StudentInfo).offset(skip).limit(limit))
    return result.scalars().all()