import os
import re
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from dotenv import load_dotenv
from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from utils.baseResponse import BaseResponse
from utils.logger import AppLogger

load_dotenv()
logger = AppLogger.get_logger(__name__)
ai_router = APIRouter(prefix="/api/ai", tags=["AI模块"])


class AiChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = Field(min_length=1, max_length=4000)
    model: str | None = None
    temperature: float = Field(default=0.7, ge=0, le=2)


class AiChatResponse(BaseModel):
    answer: str
    model: str


class Text2SQLRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1, max_length=2000)
    model: str | None = None
    temperature: float = Field(default=0.0, ge=0, le=1)
    max_rows: int = Field(default=100, ge=1, le=200)


class Text2SQLResponse(BaseModel):
    sql: str
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int
    warning: str | None = None


SCHEMA_PROMPT = """
你是一个 MySQL SQL 生成器，只返回 SQL，不要解释。
数据库核心表结构（仅列出常用字段）：
- students(id, student_code, class_id, advisor_id, name, gender, age, hometown, graduate_school, major, enrollment_date, graduation_date, education_level, is_deleted)
- classes(id, class_code, start_date, head_teacher_id, is_deleted)
- teachers(id, teacher_code, name, is_deleted)
- scores(id, student_id, exam_sequence, score, is_deleted)
- employments(id, student_id, company_name, job_open_date, offer_date, salary, is_current, is_deleted)
- courses(id, course_code, course_name, description, is_deleted)
- class_teaching_periods(id, class_id, lecturer_id, course_id, start_date, end_date, is_deleted)
关系：
- students.class_id -> classes.id
- scores.student_id / employments.student_id -> students.id
- class_teaching_periods.class_id -> classes.id
- class_teaching_periods.lecturer_id -> teachers.id
- class_teaching_periods.course_id -> courses.id
业务约束：
- 对外常用编码字段：student_code/class_code/course_code/teacher_code
- 查询时优先附加 is_deleted = 0 条件
输出要求：
- 只输出一条可执行 SQL（MySQL）
- 只能 SELECT 查询
"""


def _get_ai_settings() -> tuple[str, str, str]:
    base_url = os.getenv("AI_BASE_URL", "").strip()
    api_key = os.getenv("AI_API_KEY", "").strip()
    model = os.getenv("AI_MODEL", "").strip()

    if not base_url:
        raise ValueError("AI_BASE_URL 未配置")
    if not api_key:
        raise ValueError("AI_API_KEY 未配置")
    if not model:
        raise ValueError("AI_MODEL 未配置")

    return base_url, api_key, model


def _extract_sql(raw_output: str) -> str:
    content = raw_output.strip()
    code_block_match = re.search(r"```(?:sql)?\s*([\s\S]*?)```", content, flags=re.IGNORECASE)
    sql = code_block_match.group(1).strip() if code_block_match else content
    return sql.rstrip(";").strip()


def _validate_readonly_sql(sql: str) -> None:
    lowered = sql.lower().strip()
    if not lowered.startswith("select") and not lowered.startswith("with"):
        raise ValueError("仅允许 SELECT 查询")
    if ";" in sql:
        raise ValueError("不允许多语句执行")
    forbidden = re.compile(r"\b(insert|update|delete|drop|alter|truncate|create|replace|grant|revoke)\b", re.IGNORECASE)
    if forbidden.search(sql):
        raise ValueError("SQL 包含危险关键字，仅允许只读查询")


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat(sep=" ") if isinstance(value, datetime) else value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


@ai_router.post("/chat", response_model=BaseResponse[AiChatResponse], description="AI 对话")
async def ai_chat(chat_data: AiChatRequest):
    base_url: str = ""
    target_model: str = chat_data.model or ""
    try:
        base_url, api_key, default_model = _get_ai_settings()
        target_model = chat_data.model or default_model
        logger.info("AI对话请求: model=%s, message_length=%s", target_model, len(chat_data.message))

        try:
            from openai import OpenAI
        except ImportError as exc:
            logger.error("openai SDK 未安装")
            raise ValueError("未安装 openai 依赖，请先执行: pip install openai") from exc

        client = OpenAI(base_url=base_url, api_key=api_key)
        response = client.chat.completions.create(
            model=target_model,
            messages=[{"role": "user", "content": chat_data.message}],
            temperature=chat_data.temperature,
        )
        answer = response.choices[0].message.content if response.choices else ""
        final_answer = answer or ""
        logger.info("AI对话成功: model=%s, answer_length=%s", target_model, len(final_answer))
        return BaseResponse.success(data=AiChatResponse(answer=final_answer, model=target_model))
    except ValueError as e:
        logger.warning("AI对话失败: model=%s, reason=%s", target_model or "unknown", str(e))
        return BaseResponse.error(code=400, message=str(e))
    except Exception as e:
        logger.exception("AI调用异常: model=%s, base_url=%s", target_model or "unknown", base_url or "unknown")
        return BaseResponse.error(code=500, message=f"AI 调用失败: {str(e)}")


@ai_router.post("/text2sql", response_model=BaseResponse[Text2SQLResponse], description="自然语言转SQL并执行只读查询")
async def text2sql(query_data: Text2SQLRequest, db: AsyncSession = Depends(get_db)):
    base_url: str = ""
    target_model: str = query_data.model or ""
    try:
        base_url, api_key, default_model = _get_ai_settings()
        target_model = query_data.model or default_model

        try:
            from openai import OpenAI
        except ImportError as exc:
            logger.error("openai SDK 未安装")
            raise ValueError("未安装 openai 依赖，请先执行: pip install openai") from exc

        client = OpenAI(base_url=base_url, api_key=api_key)
        response = client.chat.completions.create(
            model=target_model,
            temperature=query_data.temperature,
            messages=[
                {"role": "system", "content": SCHEMA_PROMPT},
                {"role": "user", "content": query_data.question},
            ],
        )

        raw_sql = response.choices[0].message.content if response.choices else ""
        parsed_sql = _extract_sql(raw_sql or "")
        if not parsed_sql:
            raise ValueError("模型未生成有效 SQL")
        _validate_readonly_sql(parsed_sql)

        safe_sql = f"SELECT * FROM ({parsed_sql}) AS _safe_query LIMIT {query_data.max_rows}"
        logger.info("Text2SQL执行: model=%s, max_rows=%s, sql=%s", target_model, query_data.max_rows, parsed_sql)

        result = await db.execute(text(safe_sql))
        columns = list(result.keys())
        raw_rows = result.mappings().all()
        rows: list[dict[str, Any]] = []
        for row in raw_rows:
            normalized = {k: _to_jsonable(v) for k, v in dict(row).items()}
            rows.append(normalized)

        return BaseResponse.success(
            data=Text2SQLResponse(
                sql=parsed_sql,
                columns=columns,
                rows=rows,
                row_count=len(rows),
                warning="仅支持只读查询，结果已强制限制最大返回行数",
            )
        )
    except ValueError as e:
        logger.warning("Text2SQL失败: model=%s, reason=%s", target_model or "unknown", str(e))
        return BaseResponse.error(code=400, message=str(e))
    except Exception as e:
        logger.exception("Text2SQL异常: model=%s, base_url=%s", target_model or "unknown", base_url or "unknown")
        return BaseResponse.error(code=500, message=f"Text2SQL 调用失败: {str(e)}")
