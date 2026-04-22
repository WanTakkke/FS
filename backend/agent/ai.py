from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from agent.ai_application.ai_service import AIApplicationService
from config.db_config import get_db
from utils.auth import require_permission
from utils.baseResponse import BaseResponse
from utils.logger import AppLogger

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


_ai_service: AIApplicationService | None = None


def _get_ai_service() -> AIApplicationService:
    global _ai_service
    if _ai_service is None:
        _ai_service = AIApplicationService.from_env()
    return _ai_service


@ai_router.post("/chat", response_model=BaseResponse[AiChatResponse], description="AI 对话")
async def ai_chat(
    chat_data: AiChatRequest,
    _: object = Depends(require_permission("ai:chat")),
):
    try:
        target_model = chat_data.model or "env_default"
        logger.info("AI对话请求: model=%s, message_length=%s", target_model, len(chat_data.message))
        result = _get_ai_service().chat(
            message=chat_data.message,
            model=chat_data.model,
            temperature=chat_data.temperature,
        )
        logger.info("AI对话成功: model=%s, answer_length=%s", result.model, len(result.answer))
        return BaseResponse.success(data=AiChatResponse(answer=result.answer, model=result.model))
    except ValueError as e:
        logger.warning("AI对话失败: model=%s, reason=%s", chat_data.model or "unknown", str(e))
        return BaseResponse.error(code=400, message=str(e))
    except Exception as e:
        logger.exception("AI调用异常: model=%s", chat_data.model or "unknown")
        return BaseResponse.error(code=500, message=f"AI 调用失败: {str(e)}")


@ai_router.post("/text2sql", response_model=BaseResponse[Text2SQLResponse], description="自然语言转SQL并执行只读查询")
async def text2sql(
    query_data: Text2SQLRequest,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_permission("ai:text2sql")),
):
    try:
        target_model = query_data.model or "env_default"
        logger.info("Text2SQL请求: model=%s, max_rows=%s", target_model, query_data.max_rows)
        result = await _get_ai_service().text2sql(
            question=query_data.question,
            model=query_data.model,
            temperature=query_data.temperature,
            max_rows=query_data.max_rows,
            db=db,
        )
        logger.info("Text2SQL执行成功: model=%s, row_count=%s", target_model, result.row_count)

        return BaseResponse.success(
            data=Text2SQLResponse(
                sql=result.sql,
                columns=result.columns,
                rows=result.rows,
                row_count=result.row_count,
                warning=result.warning,
            )
        )
    except ValueError as e:
        logger.warning("Text2SQL失败: model=%s, reason=%s", query_data.model or "unknown", str(e))
        return BaseResponse.error(code=400, message=str(e))
    except Exception as e:
        logger.exception("Text2SQL异常: model=%s", query_data.model or "unknown")
        return BaseResponse.error(code=500, message=f"Text2SQL 调用失败: {str(e)}")
