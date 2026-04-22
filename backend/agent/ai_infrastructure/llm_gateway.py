from agent.ai_infrastructure.settings import get_ai_settings


class OpenAILlmGateway:
    def __init__(self, base_url: str, api_key: str, default_model: str):
        self._base_url = base_url
        self._api_key = api_key
        self.default_model = default_model

    @classmethod
    def from_env(cls) -> "OpenAILlmGateway":
        base_url, api_key, model = get_ai_settings()
        return cls(base_url=base_url, api_key=api_key, default_model=model)

    @staticmethod
    def _build_client(base_url: str, api_key: str):
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ValueError("未安装 openai 依赖，请先执行: pip install openai") from exc
        return OpenAI(base_url=base_url, api_key=api_key)

    def generate(self, messages: list[dict[str, str]], model: str | None, temperature: float) -> tuple[str, str]:
        target_model = model or self.default_model
        client = self._build_client(self._base_url, self._api_key)
        response = client.chat.completions.create(
            model=target_model,
            temperature=temperature,
            messages=messages,
        )
        content = response.choices[0].message.content if response.choices else ""
        return content or "", target_model
