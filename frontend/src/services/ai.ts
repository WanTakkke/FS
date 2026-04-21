import { http, unwrapResponse } from "../lib/http";

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
  return unwrapResponse<AiChatResult>(http.post("/api/ai/chat", payload));
}

export async function text2sql(payload: Text2SqlPayload) {
  return unwrapResponse<Text2SqlResult>(http.post("/api/ai/text2sql", payload));
}
