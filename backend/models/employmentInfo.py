from datetime import datetime
from decimal import Decimal

from sqlalchemy import Integer, String, DateTime, Numeric
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from models.baseInfo import Base


class EmploymentInfo(Base):
    __tablename__ = "employments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="自增主键")
    student_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="学生ID (逻辑关联 students.id)")
    company_name: Mapped[str] = mapped_column(String(200), nullable=False, comment="就业公司名称")
    job_open_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="就业开放时间")
    offer_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="offer下发时间")
    salary: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True, comment="就业薪资 (单位: 元)")
    is_current: Mapped[int] = mapped_column(TINYINT, nullable=False, default=0, comment="是否当前最新就业: 0-否, 1-是")

