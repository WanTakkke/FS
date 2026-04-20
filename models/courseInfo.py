from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from models.baseInfo import Base


class CourseInfo(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="自增主键")
    course_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, comment="课程编码(业务唯一)")
    course_name: Mapped[str] = mapped_column(String(100), nullable=False, comment="课程名称")
    description: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="课程描述")

