import os

from dotenv import load_dotenv
from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field

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
