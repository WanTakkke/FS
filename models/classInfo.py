from datetime import date

from sqlalchemy import String, Integer, Date
from sqlalchemy.orm import Mapped, mapped_column

from models.baseInfo import Base


class ClassInfo(Base):
    __tablename__ = "classes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="自增主键")
    class_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, comment="班级业务编号")
    start_date: Mapped[date] = mapped_column(Date, nullable=False, comment="开课时间")
    head_teacher_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="班主任ID (逻辑关联 teachers.id)")

