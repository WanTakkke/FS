from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ClassTeachingRequest(BaseModel):
    class_code: str
    lecturer_code: str
    course_code: str
    start_date: date
    end_date: date | None = None

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.end_date is not None and self.start_date > self.end_date:
            raise ValueError("start_date 不能大于 end_date")
        return self


class ClassTeachingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    class_code: str | None = None
    lecturer_code: str | None = None
    lecturer_name: str | None = None
    course_code: str | None = None
    course_name: str | None = None
    start_date: str
    end_date: str | None = None
    is_current_teaching: bool

    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def convert_date_fields(cls, value):
        if value is None:
            return None
        if isinstance(value, date):
            return value.isoformat()
        return value

    @field_validator("is_current_teaching", mode="before")
    @classmethod
    def convert_is_current(cls, value):
        if value in (0, 1):
            return bool(value)
        return value


class ClassTeachingUpdateRequest(BaseModel):
    id: int
    class_code: str | None = None
    lecturer_code: str | None = None
    course_code: str | None = None
    start_date: date | None = None
    end_date: date | None = None

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.start_date is not None and self.end_date is not None and self.start_date > self.end_date:
            raise ValueError("start_date 不能大于 end_date")
        return self


class ClassTeachingQueryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    class_code: str | None = None
    lecturer_code: str | None = None
    lecturer_name: str | None = None
    course_code: str | None = None
    course_name: str | None = None
    start_date_start: date | None = None
    start_date_end: date | None = None
    end_date_start: date | None = None
    end_date_end: date | None = None
    is_current_teaching: bool | None = None

    @model_validator(mode="after")
    def validate_ranges(self):
        if self.start_date_start and self.start_date_end and self.start_date_start > self.start_date_end:
            raise ValueError("start_date_start 不能大于 start_date_end")
        if self.end_date_start and self.end_date_end and self.end_date_start > self.end_date_end:
            raise ValueError("end_date_start 不能大于 end_date_end")
        return self
