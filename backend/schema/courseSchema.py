from pydantic import BaseModel, ConfigDict, Field


class CourseRequest(BaseModel):
    course_code: str
    course_name: str
    description: str | None = None


class CourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    course_code: str
    course_name: str
    description: str | None = None


class CourseUpdateRequest(BaseModel):
    course_code: str
    course_name: str | None = None
    description: str | None = None


class CourseQueryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    course_code: str | None = None
    course_name: str | None = None

