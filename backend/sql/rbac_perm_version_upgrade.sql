SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 给sys_user补充perm_version字段（已存在则跳过）
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

UPDATE sys_user SET perm_version = 1 WHERE perm_version IS NULL;

SET FOREIGN_KEY_CHECKS = 1;
