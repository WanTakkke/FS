SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 用户权限版本号（角色/权限变更后递增，用于access token快速失效）
SET @col_exists := (
  SELECT COUNT(*)
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'sys_user'
    AND COLUMN_NAME = 'perm_version'
);

SET @ddl := IF(
  @col_exists = 0,
  'ALTER TABLE sys_user ADD COLUMN perm_version BIGINT NOT NULL DEFAULT 1 COMMENT ''权限版本号''',
  'SELECT 1'
);

PREPARE stmt FROM @ddl;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @perm_nullable := (
  SELECT CASE WHEN IS_NULLABLE = 'YES' THEN 1 ELSE 0 END
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'sys_user'
    AND COLUMN_NAME = 'perm_version'
  LIMIT 1
);

SET @fix_null_sql := IF(
  COALESCE(@perm_nullable, 0) = 1,
  'UPDATE sys_user SET perm_version = 1 WHERE perm_version IS NULL',
  'SELECT 1'
);

PREPARE stmt_fix FROM @fix_null_sql;
EXECUTE stmt_fix;
DEALLOCATE PREPARE stmt_fix;

-- 刷新令牌表（refresh token 轮换与失效）
CREATE TABLE IF NOT EXISTS `sys_refresh_token` (
  `token_jti` VARCHAR(64) NOT NULL COMMENT 'refresh token唯一ID(JTI)',
  `user_id` BIGINT NOT NULL COMMENT '用户ID',
  `expires_at` DATETIME NOT NULL COMMENT 'refresh token过期时间',
  `revoked_at` DATETIME DEFAULT NULL COMMENT '失效时间，NULL表示有效',
  `replaced_by_jti` VARCHAR(64) DEFAULT NULL COMMENT '被轮换的新token_jti',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`token_jti`),
  KEY `idx_srt_user_id` (`user_id`),
  KEY `idx_srt_expires_at` (`expires_at`),
  KEY `idx_srt_revoked_at` (`revoked_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='刷新令牌表';

-- 审计日志表（RBAC关键操作记录）
CREATE TABLE IF NOT EXISTS `sys_audit_log` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `module` VARCHAR(64) NOT NULL COMMENT '模块名称，如rbac',
  `action` VARCHAR(64) NOT NULL COMMENT '动作编码，如role.create',
  `operator_id` BIGINT DEFAULT NULL COMMENT '操作者用户ID',
  `operator_username` VARCHAR(64) NOT NULL COMMENT '操作者用户名',
  `target_type` VARCHAR(64) NOT NULL COMMENT '目标类型，如role/user',
  `target_id` VARCHAR(64) NOT NULL COMMENT '目标标识',
  `detail_json` JSON DEFAULT NULL COMMENT '变更详情JSON',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_sal_module_action` (`module`, `action`),
  KEY `idx_sal_operator_id` (`operator_id`),
  KEY `idx_sal_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统审计日志表';

-- 初始化角色
INSERT INTO sys_role(name, code, description, created_at, updated_at, deleted_at)
SELECT '超级管理员', 'admin', '系统超级管理员', NOW(), NOW(), NULL
WHERE NOT EXISTS (
    SELECT 1 FROM sys_role WHERE code = 'admin' AND deleted_at IS NULL
);

INSERT INTO sys_role(name, code, description, created_at, updated_at, deleted_at)
SELECT '教务老师', 'teacher', '教学业务操作角色', NOW(), NOW(), NULL
WHERE NOT EXISTS (
    SELECT 1 FROM sys_role WHERE code = 'teacher' AND deleted_at IS NULL
);

-- 初始化权限点（接口级）
-- 先创建权限组节点（parent_id为NULL，type='group'）
INSERT INTO sys_permission(parent_id, name, code, type, created_at, updated_at, deleted_at)
SELECT NULL, p.name, p.code, 'group', NOW(), NOW(), NULL
FROM (
    SELECT 'RBAC管理' AS name, 'rbac' AS code
    UNION ALL SELECT '用户管理', 'user'
    UNION ALL SELECT '学生管理', 'student'
    UNION ALL SELECT '成绩管理', 'score'
    UNION ALL SELECT '班级管理', 'class'
    UNION ALL SELECT '课程管理', 'course'
    UNION ALL SELECT '就业管理', 'employment'
    UNION ALL SELECT '班级授课管理', 'class_teaching'
    UNION ALL SELECT 'AI助手', 'ai'
) p
WHERE NOT EXISTS (
    SELECT 1 FROM sys_permission sp WHERE sp.code = p.code AND sp.deleted_at IS NULL
);

-- 创建子权限（parent_id指向权限组，type='api'）
-- RBAC管理子权限
INSERT INTO sys_permission(parent_id, name, code, type, created_at, updated_at, deleted_at)
SELECT pg.id, p.name, p.code, 'api', NOW(), NOW(), NULL
FROM sys_permission pg
JOIN (
    SELECT 'rbac' AS group_code, '角色查询' AS name, 'rbac:role:read' AS code
    UNION ALL SELECT 'rbac', '角色创建', 'rbac:role:create'
    UNION ALL SELECT 'rbac', '角色更新', 'rbac:role:update'
    UNION ALL SELECT 'rbac', '角色删除', 'rbac:role:delete'
    UNION ALL SELECT 'rbac', '权限查询', 'rbac:permission:read'
    UNION ALL SELECT 'rbac', '权限创建', 'rbac:permission:create'
    UNION ALL SELECT 'rbac', '权限更新', 'rbac:permission:update'
    UNION ALL SELECT 'rbac', '权限删除', 'rbac:permission:delete'
    UNION ALL SELECT 'rbac', '审计日志查询', 'rbac:audit:read'
    UNION ALL SELECT 'rbac', '用户绑定角色', 'rbac:user:bind_role'
    UNION ALL SELECT 'rbac', '角色绑定权限', 'rbac:role:bind_permission'
) p ON pg.code = p.group_code
WHERE pg.deleted_at IS NULL
  AND NOT EXISTS (
    SELECT 1 FROM sys_permission sp WHERE sp.code = p.code AND sp.deleted_at IS NULL
);

-- 用户管理子权限
INSERT INTO sys_permission(parent_id, name, code, type, created_at, updated_at, deleted_at)
SELECT pg.id, p.name, p.code, 'api', NOW(), NOW(), NULL
FROM sys_permission pg
JOIN (
    SELECT 'user' AS group_code, '用户查询' AS name, 'user:read' AS code
    UNION ALL SELECT 'user', '用户更新', 'user:update'
    UNION ALL SELECT 'user', '用户状态管理', 'user:status'
    UNION ALL SELECT 'user', '用户密码重置', 'user:password:reset'
    UNION ALL SELECT 'user', '用户删除', 'user:delete'
) p ON pg.code = p.group_code
WHERE pg.deleted_at IS NULL
  AND NOT EXISTS (
    SELECT 1 FROM sys_permission sp WHERE sp.code = p.code AND sp.deleted_at IS NULL
);

-- 学生管理子权限
INSERT INTO sys_permission(parent_id, name, code, type, created_at, updated_at, deleted_at)
SELECT pg.id, p.name, p.code, 'api', NOW(), NOW(), NULL
FROM sys_permission pg
JOIN (
    SELECT 'student' AS group_code, '学生查询' AS name, 'student:read' AS code
    UNION ALL SELECT 'student', '学生新增', 'student:create'
    UNION ALL SELECT 'student', '学生更新', 'student:update'
    UNION ALL SELECT 'student', '学生删除', 'student:delete'
) p ON pg.code = p.group_code
WHERE pg.deleted_at IS NULL
  AND NOT EXISTS (
    SELECT 1 FROM sys_permission sp WHERE sp.code = p.code AND sp.deleted_at IS NULL
);

-- 成绩管理子权限
INSERT INTO sys_permission(parent_id, name, code, type, created_at, updated_at, deleted_at)
SELECT pg.id, p.name, p.code, 'api', NOW(), NOW(), NULL
FROM sys_permission pg
JOIN (
    SELECT 'score' AS group_code, '成绩查询' AS name, 'score:read' AS code
    UNION ALL SELECT 'score', '成绩新增', 'score:create'
    UNION ALL SELECT 'score', '成绩更新', 'score:update'
    UNION ALL SELECT 'score', '成绩删除', 'score:delete'
) p ON pg.code = p.group_code
WHERE pg.deleted_at IS NULL
  AND NOT EXISTS (
    SELECT 1 FROM sys_permission sp WHERE sp.code = p.code AND sp.deleted_at IS NULL
);

-- 班级管理子权限
INSERT INTO sys_permission(parent_id, name, code, type, created_at, updated_at, deleted_at)
SELECT pg.id, p.name, p.code, 'api', NOW(), NOW(), NULL
FROM sys_permission pg
JOIN (
    SELECT 'class' AS group_code, '班级查询' AS name, 'class:read' AS code
    UNION ALL SELECT 'class', '班级新增', 'class:create'
    UNION ALL SELECT 'class', '班级更新', 'class:update'
    UNION ALL SELECT 'class', '班级删除', 'class:delete'
) p ON pg.code = p.group_code
WHERE pg.deleted_at IS NULL
  AND NOT EXISTS (
    SELECT 1 FROM sys_permission sp WHERE sp.code = p.code AND sp.deleted_at IS NULL
);

-- 课程管理子权限
INSERT INTO sys_permission(parent_id, name, code, type, created_at, updated_at, deleted_at)
SELECT pg.id, p.name, p.code, 'api', NOW(), NOW(), NULL
FROM sys_permission pg
JOIN (
    SELECT 'course' AS group_code, '课程查询' AS name, 'course:read' AS code
    UNION ALL SELECT 'course', '课程新增', 'course:create'
    UNION ALL SELECT 'course', '课程更新', 'course:update'
    UNION ALL SELECT 'course', '课程删除', 'course:delete'
) p ON pg.code = p.group_code
WHERE pg.deleted_at IS NULL
  AND NOT EXISTS (
    SELECT 1 FROM sys_permission sp WHERE sp.code = p.code AND sp.deleted_at IS NULL
);

-- 就业管理子权限
INSERT INTO sys_permission(parent_id, name, code, type, created_at, updated_at, deleted_at)
SELECT pg.id, p.name, p.code, 'api', NOW(), NOW(), NULL
FROM sys_permission pg
JOIN (
    SELECT 'employment' AS group_code, '就业查询' AS name, 'employment:read' AS code
    UNION ALL SELECT 'employment', '就业新增', 'employment:create'
    UNION ALL SELECT 'employment', '就业更新', 'employment:update'
    UNION ALL SELECT 'employment', '就业删除', 'employment:delete'
) p ON pg.code = p.group_code
WHERE pg.deleted_at IS NULL
  AND NOT EXISTS (
    SELECT 1 FROM sys_permission sp WHERE sp.code = p.code AND sp.deleted_at IS NULL
);

-- 班级授课管理子权限
INSERT INTO sys_permission(parent_id, name, code, type, created_at, updated_at, deleted_at)
SELECT pg.id, p.name, p.code, 'api', NOW(), NOW(), NULL
FROM sys_permission pg
JOIN (
    SELECT 'class_teaching' AS group_code, '班级授课查询' AS name, 'class_teaching:read' AS code
    UNION ALL SELECT 'class_teaching', '班级授课新增', 'class_teaching:create'
    UNION ALL SELECT 'class_teaching', '班级授课更新', 'class_teaching:update'
    UNION ALL SELECT 'class_teaching', '班级授课删除', 'class_teaching:delete'
) p ON pg.code = p.group_code
WHERE pg.deleted_at IS NULL
  AND NOT EXISTS (
    SELECT 1 FROM sys_permission sp WHERE sp.code = p.code AND sp.deleted_at IS NULL
);

-- AI助手子权限
INSERT INTO sys_permission(parent_id, name, code, type, created_at, updated_at, deleted_at)
SELECT pg.id, p.name, p.code, 'api', NOW(), NOW(), NULL
FROM sys_permission pg
JOIN (
    SELECT 'ai' AS group_code, 'AI对话' AS name, 'ai:chat' AS code
    UNION ALL SELECT 'ai', 'AI Text2SQL', 'ai:text2sql'
) p ON pg.code = p.group_code
WHERE pg.deleted_at IS NULL
  AND NOT EXISTS (
    SELECT 1 FROM sys_permission sp WHERE sp.code = p.code AND sp.deleted_at IS NULL
);

-- 赋权：admin 拥有全部权限（包括权限组节点和子权限）
INSERT INTO sys_role_permission(role_id, permission_id, created_at)
SELECT r.id, p.id, NOW()
FROM sys_role r
JOIN sys_permission p ON p.deleted_at IS NULL
LEFT JOIN sys_role_permission rp ON rp.role_id = r.id AND rp.permission_id = p.id
WHERE r.code = 'admin' AND r.deleted_at IS NULL AND rp.role_id IS NULL;

-- 赋权：teacher 拥有主要业务模块权限（包含权限组节点）
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
LEFT JOIN sys_role_permission rp ON rp.role_id = r.id AND rp.permission_id = p.id
WHERE r.code = 'teacher' AND r.deleted_at IS NULL AND rp.role_id IS NULL;

-- 绑定 admin 用户到 admin 角色（按用户名匹配）
INSERT INTO sys_user_role(user_id, role_id, created_at)
SELECT u.id, r.id, NOW()
FROM sys_user u
JOIN sys_role r ON r.code = 'admin' AND r.deleted_at IS NULL
LEFT JOIN sys_user_role ur ON ur.user_id = u.id AND ur.role_id = r.id
WHERE u.username = 'admin' AND u.deleted_at IS NULL AND ur.user_id IS NULL;

SET FOREIGN_KEY_CHECKS = 1;
