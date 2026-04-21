import { http, unwrapResponse } from "../lib/http";
import type { PageParams } from "../types/common";
import type { Student } from "../types/modules";

export async function queryStudents(params: PageParams) {
  return unwrapResponse<Student[]>(
    http.get("/api/student/query", { params: { page: params.page, page_size: params.page_size } }),
  );
}

export async function queryStudentsByCondition(payload: Record<string, unknown>) {
  return unwrapResponse<Student[]>(http.post("/api/student/query/condition", payload));
}

export async function addStudent(payload: Record<string, unknown>) {
  return unwrapResponse<Student>(http.post("/api/student/add", payload));
}

export async function updateStudent(payload: Record<string, unknown>) {
  return unwrapResponse<Student>(http.post("/api/student/update", payload));
}

export async function deleteStudent(studentCode: string) {
  return unwrapResponse<boolean>(http.delete(`/api/student/delete/${studentCode}`));
}
