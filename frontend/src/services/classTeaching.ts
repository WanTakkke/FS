import { http, unwrapResponse } from "../lib/http";
import type { PageParams } from "../types/common";
import type { ClassTeachingItem } from "../types/modules";

export async function queryClassTeaching(params: PageParams) {
  return unwrapResponse<ClassTeachingItem[]>(
    http.get("/api/class-teaching/query", { params: { page: params.page, page_size: params.page_size } }),
  );
}

export async function queryClassTeachingByCondition(payload: Record<string, unknown>) {
  return unwrapResponse<ClassTeachingItem[]>(http.post("/api/class-teaching/query/condition", payload));
}

export async function addClassTeaching(payload: Record<string, unknown>) {
  return unwrapResponse<ClassTeachingItem>(http.post("/api/class-teaching/add", payload));
}

export async function updateClassTeaching(payload: Record<string, unknown>) {
  return unwrapResponse<ClassTeachingItem>(http.post("/api/class-teaching/update", payload));
}

export async function deleteClassTeaching(teachingId: number) {
  return unwrapResponse<boolean>(http.delete(`/api/class-teaching/delete/${teachingId}`));
}
