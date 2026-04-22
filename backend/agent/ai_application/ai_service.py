from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from agent.ai_domain.models import ChatResult, Text2SqlResult
from agent.ai_domain.prompt_builder import build_text2sql_prompt
from agent.ai_domain.sql_guard import (
    extract_sql,
    force_row_limit,
    normalize_rows,
    validate_readonly_sql,
)
from agent.ai_infrastructure.llm_gateway import OpenAILlmGateway


class AIApplicationService:
    def __init__(self, llm_gateway: OpenAILlmGateway):
        self._llm_gateway = llm_gateway

    @classmethod
    def from_env(cls) -> "AIApplicationService":
        gateway = OpenAILlmGateway.from_env()
        return cls(llm_gateway=gateway)

    def chat(self, message: str, model: str | None, temperature: float) -> ChatResult:
        content, target_model = self._llm_gateway.generate(
            messages=[{"role": "user", "content": message}],
            model=model,
            temperature=temperature,
        )
        return ChatResult(answer=content, model=target_model)

    async def text2sql(
        self,
        question: str,
        model: str | None,
        temperature: float,
        max_rows: int,
        db: AsyncSession,
    ) -> Text2SqlResult:
        system_prompt = build_text2sql_prompt()
        raw_sql, _ = self._llm_gateway.generate(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ],
            model=model,
            temperature=temperature,
        )
        parsed_sql = extract_sql(raw_sql)
        if not parsed_sql:
            raise ValueError("模型未生成有效 SQL")
        validate_readonly_sql(parsed_sql)
        safe_sql = force_row_limit(parsed_sql, max_rows)

        result = await db.execute(text(safe_sql))
        columns = list(result.keys())
        mappings = result.mappings().all()
        raw_rows: list[dict[str, Any]] = [dict(row) for row in mappings]
        rows = normalize_rows(raw_rows)

        return Text2SqlResult(
            sql=parsed_sql,
            columns=columns,
            rows=rows,
            row_count=len(rows),
            warning="仅支持只读查询，结果已强制限制最大返回行数",
        )
