from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class EmploymentRequest(BaseModel):
    student_code: str
    company_name: str
    job_open_date: datetime
    offer_date: datetime | None = None
    salary: Decimal | None = Field(default=None, ge=0)
    is_latest_employment: bool = False


class EmploymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_code: str | None = None
    student_name: str | None = None
    class_code: str | None = None
    company_name: str
    job_open_date: str
    offer_date: str | None = None
    salary: float | None = None
    is_latest_employment: bool

    @field_validator("job_open_date", "offer_date", mode="before")
    @classmethod
    def convert_datetime_fields(cls, value):
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat(sep=" ")
        return value

    @field_validator("salary", mode="before")
    @classmethod
    def convert_salary(cls, value):
        if isinstance(value, Decimal):
            return float(value)
        return value

    @field_validator("is_latest_employment", mode="before")
    @classmethod
    def convert_is_latest(cls, value):
        if value in (0, 1):
            return bool(value)
        return value


class EmploymentUpdateRequest(BaseModel):
    id: int
    student_code: str | None = None
    company_name: str | None = None
    job_open_date: datetime | None = None
    offer_date: datetime | None = None
    salary: Decimal | None = Field(default=None, ge=0)
    is_latest_employment: bool | None = None


class EmploymentQueryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    student_code: str | None = None
    student_name: str | None = None
    company_name: str | None = None
    is_latest_employment: bool | None = None
    salary_min: Decimal | None = Field(default=None, ge=0)
    salary_max: Decimal | None = Field(default=None, ge=0)
    job_open_start: datetime | None = None
    job_open_end: datetime | None = None
    offer_start: datetime | None = None
    offer_end: datetime | None = None

    @model_validator(mode="after")
    def validate_ranges(self):
        if self.salary_min is not None and self.salary_max is not None and self.salary_min > self.salary_max:
            raise ValueError("salary_min 不能大于 salary_max")
        if self.job_open_start and self.job_open_end and self.job_open_start > self.job_open_end:
            raise ValueError("job_open_start 不能大于 job_open_end")
        if self.offer_start and self.offer_end and self.offer_start > self.offer_end:
            raise ValueError("offer_start 不能大于 offer_end")
        return self
