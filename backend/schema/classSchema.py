from datetime import date

from pydantic import BaseModel, ConfigDict, field_validator, Field, model_validator


class ClassRequest(BaseModel):
    class_code: str
    start_date: date
    homeroom_teacher: str


class ClassResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    class_code: str
    start_date: str
    homeroom_teacher: str | None = None

    @field_validator("start_date", mode="before")
    @classmethod
    def convert_dates(cls, value):
        if value is None:
            return None
        if isinstance(value, date):
            return value.isoformat()
        return value


class ClassUpdateRequest(BaseModel):
    class_code: str
    start_date: date | None = None
    homeroom_teacher: str | None = None


class ClassQueryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid") # 禁止多余字段

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    class_code: str | None = None
    homeroom_teacher: str | None = None
    start_date_start: date | None = None
    start_date_end: date | None = None

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.start_date_start and self.start_date_end and self.start_date_start > self.start_date_end:
            raise ValueError("start_date_start 不能大于 start_date_end")
        return self
