SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 第一步：清理所有权限数据（包括软删除的）
DELETE FROM sys_role_permission;
DELETE FROM sys_permission;

-- 第二步：创建权限组节点（parent_id为NULL，type='group'）
INSERT INTO sys_permission(parent_id, name, code, type, created_at, updated_at, deleted_at)
VALUES
(NULL, 'RBAC管理', 'rbac', 'group', NOW(), NOW(), NULL),
(NULL, '用户管理', 'user', 'group', NOW(), NOW(), NULL),
(NULL, '学生管理', 'student', 'group', NOW(), NOW(), NULL),
(NULL, '成绩管理', 'score', 'group', NOW(), NOW(), NULL),
(NULL, '班级管理', 'class', 'group', NOW(), NOW(), NULL),
(NULL, '课程管理', 'course', 'group', NOW(), NOW(), NULL),
(NULL, '就业管理', 'employment', 'group', NOW(), NOW(), NULL),
(NULL, '班级授课管理', 'class_teaching', 'group', NOW(), NOW(), NULL),
(NULL, 'AI助手', 'ai', 'group', NOW(), NOW(), NULL);

-- 第三步：创建子权限（parent_id指向权限组ID）
-- RBAC管理子权限
SET @rbac_id = (SELECT id FROM sys_permission WHERE code = 'rbac' LIMIT 1);
INSERT INTO sys_permission(parent_id, name, code, type, created_at, updated_at, deleted_at)
VALUES
(@rbac_id, '角色查询', 'rbac:role:read', 'api', NOW(), NOW(), NULL),
(@rbac_id, '角色创建', 'rbac:role:create', 'api', NOW(), NOW(), NULL),
(@rbac_id, '角色更新', 'rbac:role:update', 'api', NOW(), NOW(), NULL),
(@rbac_id, '角色删除', 'rbac:role:delete', 'api', NOW(), NOW(), NULL),
(@rbac_id, '权限查询', 'rbac:permission:read', 'api', NOW(), NOW(), NULL),
(@rbac_id, '权限创建', 'rbac:permission:create', 'api', NOW(), NOW(), NULL),
(@rbac_id, '权限更新', 'rbac:permission:update', 'api', NOW(), NOW(), NULL),
(@rbac_id, '权限删除', 'rbac:permission:delete', 'api', NOW(), NOW(), NULL),
(@rbac_id, '审计日志查询', 'rbac:audit:read', 'api', NOW(), NOW(), NULL),
(@rbac_id, '用户绑定角色', 'rbac:user:bind_role', 'api', NOW(), NOW(), NULL),
(@rbac_id, '角色绑定权限', 'rbac:role:bind_permission', 'api', NOW(), NOW(), NULL);

-- 用户管理子权限
SET @user_id = (SELECT id FROM sys_permission WHERE code = 'user' LIMIT 1);
INSERT INTO sys_permission(parent_id, name, code, type, created_at, updated_at, deleted_at)
VALUES
(@user_id, '用户查询', 'user:read', 'api', NOW(), NOW(), NULL),
(@user_id, '用户更新', 'user:update', 'api', NOW(), NOW(), NULL),
(@user_id, '用户状态管理', 'user:status', 'api', NOW(), NOW(), NULL),
(@user_id, '用户密码重置', 'user:password:reset', 'api', NOW(), NOW(), NULL),
(@user_id, '用户删除', 'user:delete', 'api', NOW(), NOW(), NULL);

-- 学生管理子权限
SET @student_id = (SELECT id FROM sys_permission WHERE code = 'student' LIMIT 1);
INSERT INTO sys_permission(parent_id, name, code, type, created_at, updated_at, deleted_at)
VALUES
(@student_id, '学生查询', 'student:read', 'api', NOW(), NOW(), NULL),
(@student_id, '学生新增', 'student:create', 'api', NOW(), NOW(), NULL),
(@student_id, '学生更新', 'student:update', 'api', NOW(), NOW(), NULL),
(@student_id, '学生删除', 'student:delete', 'api', NOW(), NOW(), NULL);

-- 成绩管理子权限
SET @score_id = (SELECT id FROM sys_permission WHERE code = 'score' LIMIT 1);
INSERT INTO sys_permission(parent_id, name, code, type, created_at, updated_at, deleted_at)
VALUES
(@score_id, '成绩查询', 'score:read', 'api', NOW(), NOW(), NULL),
(@score_id, '成绩新增', 'score:create', 'api', NOW(), NOW(), NULL),
(@score_id, '成绩更新', 'score:update', 'api', NOW(), NOW(), NULL),
(@score_id, '成绩删除', 'score:delete', 'api', NOW(), NOW(), NULL);

-- 班级管理子权限
SET @class_id = (SELECT id FROM sys_permission WHERE code = 'class' LIMIT 1);
INSERT INTO sys_permission(parent_id, name, code, type, created_at, updated_at, deleted_at)
VALUES
(@class_id, '班级查询', 'class:read', 'api', NOW(), NOW(), NULL),
(@class_id, '班级新增', 'class:create', 'api', NOW(), NOW(), NULL),
(@class_id, '班级更新', 'class:update', 'api', NOW(), NOW(), NULL),
(@class_id, '班级删除', 'class:delete', 'api', NOW(), NOW(), NULL);

-- 课程管理子权限
SET @course_id = (SELECT id FROM sys_permission WHERE code = 'course' LIMIT 1);
INSERT INTO sys_permission(parent_id, name, code, type, created_at, updated_at, deleted_at)
VALUES
(@course_id, '课程查询', 'course:read', 'api', NOW(), NOW(), NULL),
(@course_id, '课程新增', 'course:create', 'api', NOW(), NOW(), NULL),
(@course_id, '课程更新', 'course:update', 'api', NOW(), NOW(), NULL),
(@course_id, '课程删除', 'course:delete', 'api', NOW(), NOW(), NULL);

-- 就业管理子权限
SET @employment_id = (SELECT id FROM sys_permission WHERE code = 'employment' LIMIT 1);
INSERT INTO sys_permission(parent_id, name, code, type, created_at, updated_at, deleted_at)
VALUES
(@employment_id, '就业查询', 'employment:read', 'api', NOW(), NOW(), NULL),
(@employment_id, '就业新增', 'employment:create', 'api', NOW(), NOW(), NULL),
(@employment_id, '就业更新', 'employment:update', 'api', NOW(), NOW(), NULL),
(@employment_id, '就业删除', 'employment:delete', 'api', NOW(), NOW(), NULL);

-- 班级授课管理子权限
SET @class_teaching_id = (SELECT id FROM sys_permission WHERE code = 'class_teaching' LIMIT 1);
INSERT INTO sys_permission(parent_id, name, code, type, created_at, updated_at, deleted_at)
VALUES
(@class_teaching_id, '班级授课查询', 'class_teaching:read', 'api', NOW(), NOW(), NULL),
(@class_teaching_id, '班级授课新增', 'class_teaching:create', 'api', NOW(), NOW(), NULL),
(@class_teaching_id, '班级授课更新', 'class_teaching:update', 'api', NOW(), NOW(), NULL),
(@class_teaching_id, '班级授课删除', 'class_teaching:delete', 'api', NOW(), NOW(), NULL);

-- AI助手子权限
SET @ai_id = (SELECT id FROM sys_permission WHERE code = 'ai' LIMIT 1);
INSERT INTO sys_permission(parent_id, name, code, type, created_at, updated_at, deleted_at)
VALUES
(@ai_id, 'AI对话', 'ai:chat', 'api', NOW(), NOW(), NULL),
(@ai_id, 'AI Text2SQL', 'ai:text2sql', 'api', NOW(), NOW(), NULL);

-- 第四步：赋权
-- admin 拥有全部权限
INSERT INTO sys_role_permission(role_id, permission_id, created_at)
SELECT r.id, p.id, NOW()
FROM sys_role r
CROSS JOIN sys_permission p
WHERE r.code = 'admin' AND r.deleted_at IS NULL AND p.deleted_at IS NULL;

-- teacher 拥有主要业务模块权限
INSERT INTO sys_role_permission(role_id, permission_id, created_at)
SELECT r.id, p.id, NOW()
FROM sys_role r
JOIN sys_permission p ON p.code IN (
    'student', 'student:read', 'student:create', 'student:update', 'student:delete',
    'score', 'score:read', 'score:create', 'score:update', 'score:delete',
    'class', 'class:read', 'class:create', 'class:update', 'class:delete',
    'course', 'course:read', 'course:create', 'course:update', 'course:delete',
    'employment', 'employment:read', 'employment:create', 'employment:update', 'employment:delete',
    'class_teaching', 'class_teaching:read', 'class_teaching:create', 'class_teaching:update', 'class_teaching:delete',
    'ai', 'ai:chat', 'ai:text2sql'
) AND p.deleted_at IS NULL
WHERE r.code = 'teacher' AND r.deleted_at IS NULL;

SET FOREIGN_KEY_CHECKS = 1;

-- 验证结果
SELECT 
    p1.id,
    p1.name,
    p1.code,
    p1.type,
    p1.parent_id,
    p2.name as parent_name
FROM sys_permission p1
LEFT JOIN sys_permission p2 ON p1.parent_id = p2.id
WHERE p1.deleted_at IS NULL
ORDER BY COALESCE(p1.parent_id, p1.id), p1.id;



SELECT
    p1.id,
    p1.name,
    p1.code,
    p1.type,
    p1.parent_id,
    p2.name as parent_name
FROM sys_permission p1
LEFT JOIN sys_permission p2 ON p1.parent_id = p2.id
WHERE p1.deleted_at IS NULL
ORDER BY COALESCE(p1.parent_id, p1.id), p1.id;
