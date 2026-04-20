from datetime import date

from sqlalchemy import BigInteger, Date
from sqlalchemy.orm import Mapped, mapped_column

from models.baseInfo import Base


class ClassTeachingPeriodInfo(Base):
    __tablename__ = "class_teaching_periods"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="自增主键")
    class_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="班级ID (逻辑关联 classes.id)")
    lecturer_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="授课老师ID (逻辑关联 teachers.id)")
    course_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="课程ID (逻辑关联 courses.id)")
    start_date: Mapped[date] = mapped_column(Date, nullable=False, comment="授课开始日期")
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment="授课结束日期")

