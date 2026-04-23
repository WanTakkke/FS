from datetime import date

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import  String, Integer, Date
from sqlalchemy.dialects.mysql import TINYINT

from models.baseInfo import Base


class StudentInfo(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="自增主键")
    student_code: Mapped[str] = mapped_column(String(50), nullable=False,unique=True,comment="学生业务编号")
    class_id: Mapped[int] = mapped_column(Integer,nullable=False,comment="所属班级ID (逻辑关联 classes.id)")
    advisor_id: Mapped[int | None] = mapped_column(Integer,nullable=True,comment="顾问老师ID (逻辑关联 teachers.id)")
    name: Mapped[str] = mapped_column(String(100),nullable=False,comment="姓名")
    gender: Mapped[int] = mapped_column(TINYINT,nullable=False,comment="性别: 0-女, 1-男")
    age: Mapped[int | None] = mapped_column(Integer,nullable=True,comment="年龄")
    hometown: Mapped[str | None] = mapped_column(String(100),nullable=True,comment="籍贯")
    graduate_school: Mapped[str | None] = mapped_column(String(100),nullable=True,comment="毕业院校")
    major: Mapped[str | None] = mapped_column(String(100),nullable=True,comment="专业")
    enrollment_date: Mapped[date] = mapped_column(Date,comment="入学时间")
    graduation_date: Mapped[date | None] = mapped_column(Date,nullable=True,comment="毕业时间")
    education_level: Mapped[str | None] = mapped_column(String(50),nullable=True,comment="学历")
