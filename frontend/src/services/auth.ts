import { http, unwrapResponse } from "../lib/http";
import { assertNonEmptyString } from "../lib/validators";
import type {
  CurrentUser,
  LoginPayload,
  RefreshPayload,
  TokenResponse,
  User,
  UserPageResponse,
  UserUpdatePayload,
  UserStatusUpdatePayload,
  UserPasswordResetPayload,
} from "../types/rbac";

export async function login(payload: LoginPayload) {
  assertNonEmptyString(payload.username, "用户名");
  assertNonEmptyString(payload.password, "密码");
  return unwrapResponse<TokenResponse>(http.post("/api/user/login", payload));
}

export async function refreshToken(payload: RefreshPayload) {
  assertNonEmptyString(payload.refresh_token, "refresh_token");
  return unwrapResponse<TokenResponse>(http.post("/api/user/refresh", payload));
}

export async function queryCurrentUser() {
  return unwrapResponse<CurrentUser>(http.get("/api/user/me"));
}

export async function listUsers(params?: {
  page?: number;
  page_size?: number;
  username?: string;
  email?: string;
  is_active?: number;
}) {
  const queryParams = new URLSearchParams();
  if (params?.page) queryParams.append("page", params.page.toString());
  if (params?.page_size) queryParams.append("page_size", params.page_size.toString());
  if (params?.username) queryParams.append("username", params.username);
  if (params?.email) queryParams.append("email", params.email);
  if (params?.is_active !== undefined) queryParams.append("is_active", params.is_active.toString());
  
  const queryString = queryParams.toString();
  const url = queryString ? `/api/user/list?${queryString}` : "/api/user/list";
  return unwrapResponse<UserPageResponse>(http.get(url));
}

export async function getUser(userId: number) {
  return unwrapResponse<User>(http.get(`/api/user/${userId}`));
}

export async function updateUser(userId: number, payload: UserUpdatePayload) {
  return unwrapResponse<User>(http.put(`/api/user/${userId}`, payload));
}

export async function updateUserStatus(userId: number, payload: UserStatusUpdatePayload) {
  return unwrapResponse<User>(http.put(`/api/user/${userId}/status`, payload));
}

export async function resetUserPassword(userId: number, payload: UserPasswordResetPayload) {
  assertNonEmptyString(payload.new_password, "新密码");
  return unwrapResponse<User>(http.put(`/api/user/${userId}/password`, payload));
}

export async function deleteUser(userId: number) {
  return unwrapResponse<boolean>(http.delete(`/api/user/${userId}`));
}
