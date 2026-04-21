import { http, unwrapResponse } from "../lib/http";
import type { PageParams } from "../types/common";
import type { EmploymentItem } from "../types/modules";

export async function queryEmployments(params: PageParams) {
  return unwrapResponse<EmploymentItem[]>(
    http.get("/api/employment/query", { params: { page: params.page, page_size: params.page_size } }),
  );
}

export async function queryEmploymentsByCondition(payload: Record<string, unknown>) {
  return unwrapResponse<EmploymentItem[]>(http.post("/api/employment/query/condition", payload));
}

export async function addEmployment(payload: Record<string, unknown>) {
  return unwrapResponse<EmploymentItem>(http.post("/api/employment/add", payload));
}

export async function updateEmployment(payload: Record<string, unknown>) {
  return unwrapResponse<EmploymentItem>(http.post("/api/employment/update", payload));
}

export async function deleteEmployment(employmentId: number) {
  return unwrapResponse<boolean>(http.delete(`/api/employment/delete/${employmentId}`));
}
