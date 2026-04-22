SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 用户权限版本号（角色/权限变更后递增，用于access token快速失效）
ALTER TABLE `sys_user`
ADD COLUMN IF NOT EXISTS `perm_version` BIGINT NOT NULL DEFAULT 1 COMMENT '权限版本号';

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
INSERT INTO sys_permission(parent_id, name, code, type, created_at, updated_at, deleted_at)
SELECT NULL, p.name, p.code, 'api', NOW(), NOW(), NULL
FROM (
    SELECT '角色查询' AS name, 'rbac:role:read' AS code
    UNION ALL SELECT '角色创建', 'rbac:role:create'
    UNION ALL SELECT '角色更新', 'rbac:role:update'
    UNION ALL SELECT '角色删除', 'rbac:role:delete'
    UNION ALL SELECT '权限查询', 'rbac:permission:read'
    UNION ALL SELECT '用户绑定角色', 'rbac:user:bind_role'
    UNION ALL SELECT '角色绑定权限', 'rbac:role:bind_permission'
    UNION ALL SELECT '学生查询', 'student:read'
    UNION ALL SELECT '学生新增', 'student:create'
    UNION ALL SELECT '学生更新', 'student:update'
    UNION ALL SELECT '学生删除', 'student:delete'
    UNION ALL SELECT '成绩查询', 'score:read'
    UNION ALL SELECT '成绩新增', 'score:create'
    UNION ALL SELECT '成绩更新', 'score:update'
    UNION ALL SELECT '成绩删除', 'score:delete'
    UNION ALL SELECT '班级查询', 'class:read'
    UNION ALL SELECT '班级新增', 'class:create'
    UNION ALL SELECT '班级更新', 'class:update'
    UNION ALL SELECT '班级删除', 'class:delete'
    UNION ALL SELECT '课程查询', 'course:read'
    UNION ALL SELECT '课程新增', 'course:create'
    UNION ALL SELECT '课程更新', 'course:update'
    UNION ALL SELECT '课程删除', 'course:delete'
    UNION ALL SELECT '就业查询', 'employment:read'
    UNION ALL SELECT '就业新增', 'employment:create'
    UNION ALL SELECT '就业更新', 'employment:update'
    UNION ALL SELECT '就业删除', 'employment:delete'
    UNION ALL SELECT '班级授课查询', 'class_teaching:read'
    UNION ALL SELECT '班级授课新增', 'class_teaching:create'
    UNION ALL SELECT '班级授课更新', 'class_teaching:update'
    UNION ALL SELECT '班级授课删除', 'class_teaching:delete'
    UNION ALL SELECT 'AI对话', 'ai:chat'
    UNION ALL SELECT 'AI Text2SQL', 'ai:text2sql'
) p
WHERE NOT EXISTS (
    SELECT 1 FROM sys_permission sp WHERE sp.code = p.code AND sp.deleted_at IS NULL
);

-- 赋权：admin 拥有全部权限
INSERT INTO sys_role_permission(role_id, permission_id, created_at)
SELECT r.id, p.id, NOW()
FROM sys_role r
JOIN sys_permission p ON p.deleted_at IS NULL
LEFT JOIN sys_role_permission rp ON rp.role_id = r.id AND rp.permission_id = p.id
WHERE r.code = 'admin' AND r.deleted_at IS NULL AND rp.role_id IS NULL;

-- 赋权：teacher 拥有主要业务模块权限（不含RBAC管理）
INSERT INTO sys_role_permission(role_id, permission_id, created_at)
SELECT r.id, p.id, NOW()
FROM sys_role r
JOIN sys_permission p ON p.code IN (
    'student:read', 'student:create', 'student:update', 'student:delete',
    'score:read', 'score:create', 'score:update', 'score:delete',
    'class:read', 'class:create', 'class:update', 'class:delete',
    'course:read', 'course:create', 'course:update', 'course:delete',
    'employment:read', 'employment:create', 'employment:update', 'employment:delete',
    'class_teaching:read', 'class_teaching:create', 'class_teaching:update', 'class_teaching:delete',
    'ai:chat', 'ai:text2sql'
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
