import { http, unwrapResponse } from "../lib/http";
import {
  assertNonEmptyString,
  assertPositiveInt,
  assertPositiveIntArray,
} from "../lib/validators";
import type {
  Permission,
  PermissionCreatePayload,
  PermissionTreeNode,
  PermissionUpdatePayload,
  Role,
  RoleCreatePayload,
  RolePermissionBindPayload,
  RoleUpdatePayload,
  UserPageResponse,
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

export async function getPermissionTree() {
  return unwrapResponse<PermissionTreeNode[]>(http.get("/api/rbac/permissions/tree"));
}

export async function createPermission(payload: PermissionCreatePayload) {
  assertNonEmptyString(payload.name, "权限名称");
  assertNonEmptyString(payload.code, "权限编码");
  return unwrapResponse<Permission>(http.post("/api/rbac/permissions", payload));
}

export async function updatePermission(payload: PermissionUpdatePayload) {
  assertPositiveInt(payload.permission_id, "权限ID");
  if (!payload.parent_id && !payload.name && !payload.type) {
    throw new Error("至少填写一个更新字段");
  }
  return unwrapResponse<Permission>(http.post("/api/rbac/permissions/update", payload));
}

export async function deletePermission(permissionId: number) {
  assertPositiveInt(permissionId, "权限ID");
  return unwrapResponse<boolean>(http.delete(`/api/rbac/permissions/${permissionId}`));
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
