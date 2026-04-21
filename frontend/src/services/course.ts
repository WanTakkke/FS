import { http, unwrapResponse } from "../lib/http";
import type { PageParams } from "../types/common";
import type { CourseItem } from "../types/modules";

export async function queryCourses(params: PageParams) {
  return unwrapResponse<CourseItem[]>(
    http.get("/api/course/query", { params: { page: params.page, page_size: params.page_size } }),
  );
}

export async function queryCoursesByCondition(payload: Record<string, unknown>) {
  return unwrapResponse<CourseItem[]>(http.post("/api/course/query/condition", payload));
}

export async function addCourse(payload: Record<string, unknown>) {
  return unwrapResponse<CourseItem>(http.post("/api/course/add", payload));
}

export async function updateCourse(payload: Record<string, unknown>) {
  return unwrapResponse<CourseItem>(http.post("/api/course/update", payload));
}

export async function deleteCourse(courseCode: string) {
  return unwrapResponse<boolean>(http.delete(`/api/course/delete/${courseCode}`));
}
