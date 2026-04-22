import { http, unwrapResponse } from "../lib/http";
import {
  assertNonEmptyString,
  assertPositiveInt,
  assertPositiveIntArray,
} from "../lib/validators";
import type {
  Permission,
  Role,
  RoleCreatePayload,
  RolePermissionBindPayload,
  RoleUpdatePayload,
  UserRoleBindPayload,
  UserRolePermission,
} from "../types/rbac";

export async function listRoles() {
  return unwrapResponse<Role[]>(http.get("/api/rbac/roles"));
}

export async function createRole(payload: RoleCreatePayload) {
  assertNonEmptyString(payload.name, "角色名称");
  assertNonEmptyString(payload.code, "角色编码");
  return unwrapResponse<Role>(http.post("/api/rbac/roles", payload));
}

export async function updateRole(payload: RoleUpdatePayload) {
  assertPositiveInt(payload.role_id, "角色ID");
  if (!payload.name && !payload.description) {
    throw new Error("至少填写一个更新字段");
  }
  return unwrapResponse<Role>(http.post("/api/rbac/roles/update", payload));
}

export async function deleteRole(roleId: number) {
  assertPositiveInt(roleId, "角色ID");
  return unwrapResponse<boolean>(http.delete(`/api/rbac/roles/${roleId}`));
}

export async function listPermissions() {
  return unwrapResponse<Permission[]>(http.get("/api/rbac/permissions"));
}

export async function bindUserRoles(payload: UserRoleBindPayload) {
  assertPositiveInt(payload.user_id, "用户ID");
  assertPositiveIntArray(payload.role_ids, "角色ID列表");
  return unwrapResponse<boolean>(http.post("/api/rbac/users/roles", payload));
}

export async function bindRolePermissions(payload: RolePermissionBindPayload) {
  assertPositiveInt(payload.role_id, "角色ID");
  assertPositiveIntArray(payload.permission_ids, "权限ID列表");
  return unwrapResponse<boolean>(http.post("/api/rbac/roles/permissions", payload));
}

export async function queryUserRolePermission(userId: number) {
  assertPositiveInt(userId, "用户ID");
  return unwrapResponse<UserRolePermission>(http.get(`/api/rbac/users/${userId}/permissions`));
}
