from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from models.baseInfo import Base


class TeacherInfo(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="自增主键")
    teacher_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, comment="老师业务编号")
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="姓名")

