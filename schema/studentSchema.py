from datetime import date
from pydantic import BaseModel, field_serializer


class StudentRequest(BaseModel):
    student_code: str
    class_id: int
    advisor_id: int | None = None
    name: str
    gender: int
    age: int | None = None
    hometown: str | None = None
    graduate_school: str | None = None
    major: str | None = None
    enrollment_date: date
    graduation_date: date | None = None
    education_level: str | None = None


class StudentResponse(BaseModel):
    student_code: str
    class_id: int
    advisor_id: int
    name: str
    gender: int
    age: int
    hometown: str
    graduate_school: str
    major: str
    enrollment_date: str
    graduation_date: str | None = None
    education_level: str | None = None

    #数据库返回的date类型，需要转换成字符串
    @field_serializer('enrollment_date', 'graduation_date')
    def serialize_dates(self, value: date | None) -> str | None:
        if value is None:
            return None
        return value.isoformat()

class StudentUpdateRequest(BaseModel):
    student_code: str  # 学生编号用于定位记录，必填
    class_id: int | None = None
    advisor_id: int | None = None
    name: str | None = None
    gender: int | None = None
    age: int | None = None
    hometown: str | None = None
    graduate_school: str | None = None
    major: str | None = None
    enrollment_date: date | None = None
    graduation_date: date | None = None
    education_level: str | None = None



