from dataclasses import dataclass
from typing import Any


@dataclass
class ChatResult:
    answer: str
    model: str


@dataclass
class Text2SqlResult:
    sql: str
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int
    warning: str | None = None
