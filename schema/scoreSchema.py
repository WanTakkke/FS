from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ScoreRequest(BaseModel):
    student_code: str
    exam_sequence: str
    score: Decimal = Field(ge=0, le=100)


class ScoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    class_code: str | None = None
    student_name: str | None = None
    exam_sequence: str
    score: float

    @field_validator("score", mode="before")
    @classmethod
    def convert_score(cls, value):
        if isinstance(value, Decimal):
            return float(value)
        return value


class ScoreUpdateRequest(BaseModel):
    id: int
    student_id: int | None = None
    exam_sequence: str | None = None
    score: Decimal | None = Field(default=None, ge=0, le=100)


class ScoreQueryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    student_name: str | None = None
    exam_sequence: str | None = None
    score_min: Decimal | None = Field(default=None, ge=0, le=100)
    score_max: Decimal | None = Field(default=None, ge=0, le=100)

    @model_validator(mode="after")
    def validate_score_range(self):
        if self.score_min is not None and self.score_max is not None and self.score_min > self.score_max:
            raise ValueError("score_min 不能大于 score_max")
        return self
