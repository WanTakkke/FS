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

export async function chatWithAi(payload: AiChatPayload) {
  return unwrapResponse<AiChatResult>(http.post("/api/ai/chat", payload));
}
