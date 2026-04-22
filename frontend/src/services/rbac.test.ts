import { describe, expect, it } from "vitest";

import {
  bindRolePermissions,
  bindUserRoles,
  createRole,
  deleteRole,
  queryUserRolePermission,
  updateRole,
} from "./rbac";

describe("rbac service payload validation", () => {
  it("createRole validates required fields", async () => {
    await expect(createRole({ name: "", code: "" })).rejects.toThrow("角色名称不能为空");
  });

  it("updateRole validates update fields", async () => {
    await expect(updateRole({ role_id: 1 })).rejects.toThrow("至少填写一个更新字段");
  });

  it("deleteRole validates role id", async () => {
    await expect(deleteRole(0)).rejects.toThrow("角色ID必须是正整数");
  });

  it("bindUserRoles validates role_ids", async () => {
    await expect(bindUserRoles({ user_id: 1, role_ids: [] })).rejects.toThrow("角色ID列表不能为空");
  });

  it("bindRolePermissions validates permission_ids", async () => {
    await expect(bindRolePermissions({ role_id: 1, permission_ids: [1, -2] })).rejects.toThrow(
      "权限ID列表必须全部为正整数",
    );
  });

  it("queryUserRolePermission validates user id", async () => {
    await expect(queryUserRolePermission(0)).rejects.toThrow("用户ID必须是正整数");
  });
});
