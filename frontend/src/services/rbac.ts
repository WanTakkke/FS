import { http, unwrapResponse } from "../lib/http";
import {
  assertNonEmptyString,
  assertPositiveInt,
  assertPositiveIntArray,
} from "../lib/validators";
import type {
  AuditLogPageResponse,
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

export async function listAuditLogs(params?: {
  page?: number;
  page_size?: number;
  module?: string;
  action?: string;
  operator_id?: number;
  target_type?: string;
  target_id?: string;
  start_time?: string;
  end_time?: string;
}) {
  const queryParams = new URLSearchParams();
  if (params?.page) queryParams.append("page", params.page.toString());
  if (params?.page_size) queryParams.append("page_size", params.page_size.toString());
  if (params?.module) queryParams.append("module", params.module);
  if (params?.action) queryParams.append("action", params.action);
  if (params?.operator_id) queryParams.append("operator_id", params.operator_id.toString());
  if (params?.target_type) queryParams.append("target_type", params.target_type);
  if (params?.target_id) queryParams.append("target_id", params.target_id);
  if (params?.start_time) queryParams.append("start_time", params.start_time);
  if (params?.end_time) queryParams.append("end_time", params.end_time);
  
  const queryString = queryParams.toString();
  const url = queryString ? `/api/rbac/audit-logs?${queryString}` : "/api/rbac/audit-logs";
  return unwrapResponse<AuditLogPageResponse>(http.get(url));
}
