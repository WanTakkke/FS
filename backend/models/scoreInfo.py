from decimal import Decimal

from sqlalchemy import BigInteger, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from models.baseInfo import Base


class ScoreInfo(Base):
    __tablename__ = "scores"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="自增主键")
    student_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="学生ID (逻辑关联 students.id)")
    exam_sequence: Mapped[str] = mapped_column(String(20), nullable=False, comment="考核序次")
    score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, comment="成绩 (0.00-100.00)")

