# RBAC 权限码治理规范

## 1. 命名规则

- 兼容格式：
  - `module:action`（当前存量）
  - `module:resource:action`（推荐新格式）
- 命名字符：小写字母、数字、下划线
- 示例：
  - `student:read`
  - `rbac:role:read`
  - `student:profile:update`
  - `ai:text2sql:execute`

## 2. 设计原则

- 一个接口只绑定一个最小必要权限码。
- 同一业务语义只能有一个权限码，禁止同义多码。
- 权限码一经上线，不随意改名；新增能力使用新增码。

## 3. SQL 唯一性策略

- 使用 `deleted_flag` 生成列（由 `deleted_at` 派生）参与唯一索引。
- 唯一索引：`uk_code_deleted_flag(code, deleted_flag)`。
- 目标：同一 `code` 最多存在一条活动记录（`deleted_flag=0`）。

## 4. 自动检查

- 检查脚本：`backend/script/rbac_permission_lint.py`
- 检查范围：
  - 代码中的 `require_permission("...")`
  - `backend/sql/rbac_init.sql` 权限初始化列表
- 失败条件：
  - 权限码格式非法
  - 重复定义
  - 代码使用但 SQL 未初始化

## 5. 执行方式

```bash
cd backend
python script/rbac_permission_lint.py
```

## 6. 升级脚本

- 文件：`backend/sql/rbac_permission_governance_upgrade.sql`
- 作用：
  - 增加 `deleted_flag`
  - 替换旧索引 `uk_code_deleted`
  - 创建唯一索引 `uk_code_deleted_flag`
