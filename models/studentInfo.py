from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class StudentInfo():
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="自增主键")
    student_code: Mapped[str] = mapped_column(String(50), comment="学号")
    class_id: Mapped[int] = mapped_column(comment="班级ID")
