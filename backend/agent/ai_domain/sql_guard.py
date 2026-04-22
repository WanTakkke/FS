import re
from datetime import date, datetime
from decimal import Decimal
from typing import Any


def extract_sql(raw_output: str) -> str:
    content = raw_output.strip()
    code_block_match = re.search(r"```(?:sql)?\s*([\s\S]*?)```", content, flags=re.IGNORECASE)
    sql = code_block_match.group(1).strip() if code_block_match else content
    return sql.rstrip(";").strip()


def validate_readonly_sql(sql: str) -> None:
    lowered = sql.lower().strip()
    if not lowered.startswith("select") and not lowered.startswith("with"):
        raise ValueError("仅允许 SELECT 查询")
    if ";" in sql:
        raise ValueError("不允许多语句执行")
    forbidden = re.compile(
        r"\b(insert|update|delete|drop|alter|truncate|create|replace|grant|revoke)\b",
        re.IGNORECASE,
    )
    if forbidden.search(sql):
        raise ValueError("SQL 包含危险关键字，仅允许只读查询")


def force_row_limit(sql: str, max_rows: int) -> str:
    return f"SELECT * FROM ({sql}) AS _safe_query LIMIT {int(max_rows)}"


def to_jsonable(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat(sep=" ") if isinstance(value, datetime) else value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def normalize_rows(raw_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{k: to_jsonable(v) for k, v in row.items()} for row in raw_rows]
