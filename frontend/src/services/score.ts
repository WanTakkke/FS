import { http, unwrapResponse } from "../lib/http";
import type { PageParams } from "../types/common";
import type { ScoreItem } from "../types/modules";

export async function queryScores(params: PageParams) {
  return unwrapResponse<ScoreItem[]>(
    http.get("/api/score/query", { params: { page: params.page, page_size: params.page_size } }),
  );
}

export async function queryScoresByCondition(payload: Record<string, unknown>) {
  return unwrapResponse<ScoreItem[]>(http.post("/api/score/query/condition", payload));
}

export async function addScore(payload: Record<string, unknown>) {
  return unwrapResponse<ScoreItem>(http.post("/api/score/add", payload));
}

export async function updateScore(payload: Record<string, unknown>) {
  return unwrapResponse<ScoreItem>(http.post("/api/score/update", payload));
}

export async function deleteScore(studentCode: string, examSequence: string) {
  return unwrapResponse<boolean>(
    http.delete(`/api/score/delete/${encodeURIComponent(studentCode)}/${encodeURIComponent(examSequence)}`),
  );
}
