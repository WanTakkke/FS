export interface TokenResponse {
  access_token: string;
  refresh_token?: string | null;
  token_type: string;
  expires_in?: number | null;
}

export interface LoginPayload {
  username: string;
  password: string;
}

export interface RefreshPayload {
  refresh_token: string;
}

export interface CurrentUser {
  id: number;
  username: string;
  email?: string | null;
  roles: string[];
  permissions: string[];
}

export interface Role {
  id: number;
  name: string;
  code: string;
  description?: string | null;
}

export interface Permission {
  id: number;
  parent_id?: number | null;
  name: string;
  code: string;
  type: string;
}

export interface PermissionCreatePayload {
  parent_id?: number | null;
  name: string;
  code: string;
  type?: string;
}

export interface PermissionUpdatePayload {
  permission_id: number;
  parent_id?: number | null;
  name?: string;
  type?: string;
}

export interface RoleCreatePayload {
  name: string;
  code: string;
  description?: string;
}

export interface RoleUpdatePayload {
  role_id: number;
  name?: string;
  description?: string;
}

export interface UserRoleBindPayload {
  user_id: number;
  role_ids: number[];
}

export interface RolePermissionBindPayload {
  role_id: number;
  permission_ids: number[];
}

export interface UserRolePermission {
  user_id: number;
  username: string;
  roles: string[];
  permissions: string[];
}
