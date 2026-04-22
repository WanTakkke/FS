import { http, unwrapResponse } from "../lib/http";
import { assertNonEmptyString } from "../lib/validators";
import type {
  CurrentUser,
  LoginPayload,
  RefreshPayload,
  TokenResponse,
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
