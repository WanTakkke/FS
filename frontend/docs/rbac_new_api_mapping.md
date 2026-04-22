# 前端对接清单：新增认证 / RBAC / AI 接口

## 用户认证

| Method | URL | 请求参数 | 响应 data |
|---|---|---|---|
| POST | `/api/user/register` | `username`, `password`, `email?` | `UserResponse`（当前后端返回成功消息） |
| POST | `/api/user/login` | `username`, `password` | `access_token`, `refresh_token`, `expires_in` |
| POST | `/api/user/refresh` | `refresh_token` | 新的 `access_token` + 轮换后的 `refresh_token` |
| GET | `/api/user/me` | Header: `Authorization: Bearer xxx` | `id`, `username`, `roles`, `permissions` |

## RBAC 管理

| Method | URL | 请求参数 | 响应 data |
|---|---|---|---|
| GET | `/api/rbac/roles` | 无 | `Role[]` |
| POST | `/api/rbac/roles` | `name`, `code`, `description` | `Role` |
| POST | `/api/rbac/roles/update` | `role_id`, `name?`, `description?` | `Role` |
| DELETE | `/api/rbac/roles/{role_id}` | Path: `role_id` | `boolean` |
| GET | `/api/rbac/permissions` | 无 | `Permission[]` |
| POST | `/api/rbac/users/roles` | `user_id`, `role_ids[]` | `boolean` |
| POST | `/api/rbac/roles/permissions` | `role_id`, `permission_ids[]` | `boolean` |
| GET | `/api/rbac/users/{user_id}/permissions` | Path: `user_id` | `user_id`, `username`, `roles[]`, `permissions[]` |

## AI 模块

| Method | URL | 请求参数 | 响应 data |
|---|---|---|---|
| POST | `/api/ai/chat` | `message`, `model?`, `temperature?` | `answer`, `model` |
| POST | `/api/ai/text2sql` | `question`, `model?`, `temperature?`, `max_rows?` | `sql`, `columns[]`, `rows[]`, `row_count`, `warning?` |

## 前端实现映射

- 类型定义：`src/types/rbac.ts`
- Service 封装：`src/services/auth.ts`、`src/services/rbac.ts`、`src/services/ai.ts`
- 状态管理：`src/store/authStore.ts`、`src/store/uiStore.ts`
- 路由守卫：`src/router/index.tsx`
- 页面：
  - 登录页：`src/pages/LoginPage.tsx`
  - RBAC 管理页：`src/pages/RbacPage.tsx`
  - AI 页：`src/pages/AiPage.tsx`
- 统一请求拦截：
  - 自动带 token：`src/lib/http.ts`
  - 401 自动刷新 token：`src/lib/http.ts`
  - 业务错误提示：`src/lib/http.ts`
- 参数校验：
  - 通用校验器：`src/lib/validators.ts`
  - Service 入参校验：`src/services/*.ts`
- 缓存机制：
  - TanStack Query：`src/lib/queryClient.ts` + 页面级 `useQuery`
