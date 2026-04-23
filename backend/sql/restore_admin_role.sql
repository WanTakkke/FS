SET NAMES utf8mb4;

-- 恢复张三的超级管理员角色
-- 请先确认张三的用户ID和admin角色ID

-- 查看张三的用户信息
SELECT id, username, email FROM sys_user WHERE username = '张三' AND deleted_at IS NULL;

-- 查看admin角色信息
SELECT id, name, code FROM sys_role WHERE code = 'admin' AND deleted_at IS NULL;

-- 给张三添加admin角色（请根据实际ID修改）
-- 假设张三ID=2，admin角色ID=1
INSERT INTO sys_user_role(user_id, role_id, created_at)
SELECT u.id, r.id, NOW()
FROM sys_user u
CROSS JOIN sys_role r
WHERE u.username = '张三' AND u.deleted_at IS NULL
  AND r.code = 'admin' AND r.deleted_at IS NULL
  AND NOT EXISTS (
    SELECT 1 FROM sys_user_role ur WHERE ur.user_id = u.id AND ur.role_id = r.id
  );

-- 验证结果
SELECT 
    u.id as user_id,
    u.username,
    r.id as role_id,
    r.name as role_name,
    r.code as role_code
FROM sys_user u
JOIN sys_user_role ur ON u.id = ur.user_id
JOIN sys_role r ON r.id = ur.role_id
WHERE u.username = '张三' AND u.deleted_at IS NULL AND r.deleted_at IS NULL;
