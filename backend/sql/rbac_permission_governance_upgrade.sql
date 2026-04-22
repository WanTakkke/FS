SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 1) 预检查：活动权限码不能重复（deleted_at IS NULL）
SET @dup_active := (
  SELECT COUNT(*)
  FROM (
    SELECT code
    FROM sys_permission
    WHERE deleted_at IS NULL
    GROUP BY code
    HAVING COUNT(*) > 1
  ) t
);

SET @check_sql := IF(
  @dup_active > 0,
  'SELECT ''存在重复活动权限码，请先清理后再执行治理升级'' AS error_message',
  'SELECT ''OK'' AS status_message'
);

PREPARE stmt_check FROM @check_sql;
EXECUTE stmt_check;
DEALLOCATE PREPARE stmt_check;

-- 2) deleted_flag 生成列（用于软删除场景下的唯一约束）
SET @col_exists := (
  SELECT COUNT(*)
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'sys_permission'
    AND COLUMN_NAME = 'deleted_flag'
);

SET @add_col_sql := IF(
  @col_exists = 0,
  'ALTER TABLE sys_permission ADD COLUMN deleted_flag TINYINT AS (IF(deleted_at IS NULL, 0, 1)) STORED',
  'SELECT 1'
);

PREPARE stmt_add_col FROM @add_col_sql;
EXECUTE stmt_add_col;
DEALLOCATE PREPARE stmt_add_col;

-- 3) 清理旧索引（uk_code_deleted 语义在MySQL中对NULL不严谨）
SET @old_idx_exists := (
  SELECT COUNT(*)
  FROM information_schema.STATISTICS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'sys_permission'
    AND INDEX_NAME = 'uk_code_deleted'
);

SET @drop_old_idx_sql := IF(
  @old_idx_exists > 0,
  'ALTER TABLE sys_permission DROP INDEX uk_code_deleted',
  'SELECT 1'
);

PREPARE stmt_drop_old_idx FROM @drop_old_idx_sql;
EXECUTE stmt_drop_old_idx;
DEALLOCATE PREPARE stmt_drop_old_idx;

-- 4) 新唯一索引：同一code只能存在1条活动权限( deleted_flag = 0 )
-- 同时也限制最多1条已删除记录( deleted_flag = 1 )，有助于权限码治理稳定
SET @new_idx_exists := (
  SELECT COUNT(*)
  FROM information_schema.STATISTICS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'sys_permission'
    AND INDEX_NAME = 'uk_code_deleted_flag'
);

SET @add_new_idx_sql := IF(
  @new_idx_exists = 0,
  'ALTER TABLE sys_permission ADD UNIQUE INDEX uk_code_deleted_flag(code, deleted_flag)',
  'SELECT 1'
);

PREPARE stmt_add_new_idx FROM @add_new_idx_sql;
EXECUTE stmt_add_new_idx;
DEALLOCATE PREPARE stmt_add_new_idx;

SET FOREIGN_KEY_CHECKS = 1;
