import { http, unwrapResponse } from "../lib/http";
import { assertNonEmptyString, assertNumberInRange } from "../lib/validators";

export interface AiChatPayload {
  message: string;
  model?: string;
  temperature?: number;
}

export interface AiChatResult {
  answer: string;
  model: string;
}

export interface Text2SqlPayload {
  question: string;
  model?: string;
  temperature?: number;
  max_rows?: number;
}

export interface Text2SqlResult {
  sql: string;
  columns: string[];
  rows: Array<Record<string, unknown>>;
  row_count: number;
  warning?: string | null;
}

export async function chatWithAi(payload: AiChatPayload) {
  assertNonEmptyString(payload.message, "对话内容");
  if (payload.temperature !== undefined) {
    assertNumberInRange(payload.temperature, "temperature", 0, 2);
  }
  return unwrapResponse<AiChatResult>(http.post("/api/ai/chat", payload));
}

export async function text2sql(payload: Text2SqlPayload) {
  assertNonEmptyString(payload.question, "查询问题");
  if (payload.temperature !== undefined) {
    assertNumberInRange(payload.temperature, "temperature", 0, 1);
  }
  if (payload.max_rows !== undefined) {
    assertNumberInRange(payload.max_rows, "max_rows", 1, 200);
  }
  return unwrapResponse<Text2SqlResult>(http.post("/api/ai/text2sql", payload));
}
