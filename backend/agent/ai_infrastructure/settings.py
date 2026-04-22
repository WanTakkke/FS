import os

from dotenv import load_dotenv

load_dotenv()


def get_ai_settings() -> tuple[str, str, str]:
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
