import { http, unwrapResponse } from "../lib/http";
import type { PageParams } from "../types/common";
import type { ClassItem } from "../types/modules";

export async function queryClasses(params: PageParams) {
  return unwrapResponse<ClassItem[]>(
    http.get("/api/class/query", { params: { page: params.page, page_size: params.page_size } }),
  );
}

export async function queryClassesByCondition(payload: Record<string, unknown>) {
  return unwrapResponse<ClassItem[]>(http.post("/api/class/query/condition", payload));
}

export async function addClass(payload: Record<string, unknown>) {
  return unwrapResponse<ClassItem>(http.post("/api/class/add", payload));
}

export async function updateClass(payload: Record<string, unknown>) {
  return unwrapResponse<ClassItem>(http.post("/api/class/update", payload));
}

export async function deleteClass(classCode: string) {
  return unwrapResponse<boolean>(http.delete(`/api/class/delete/${classCode}`));
}
