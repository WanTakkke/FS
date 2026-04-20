START TRANSACTION;

-- =========================================
-- 1) 初始化课程表 courses
-- 使用 INSERT ... ON DUPLICATE KEY UPDATE，重复执行也安全
-- =========================================
INSERT INTO `courses` (`course_code`, `course_name`, `description`, `is_deleted`)
VALUES
('CRS_PY_BASE',   'Python基础',   'Python语法、函数、面向对象基础', 0),
('CRS_DB_DESIGN', '数据库结构',   '关系模型、范式、索引与约束设计', 0),
('CRS_WEB_FASTAPI','FastAPI开发', 'FastAPI接口开发、依赖注入与校验', 0),
('CRS_SQL_OPT',   'SQL优化',      '执行计划分析、索引优化、慢查询排查', 0),
('CRS_GIT',       'Git协作',      '分支策略、冲突处理、代码评审流程', 0)
ON DUPLICATE KEY UPDATE
`course_name` = VALUES(`course_name`),
`description` = VALUES(`description`),
`is_deleted` = 0;


-- =========================================
-- 2) 初始化班级授课周期表 class_teaching_periods
-- 业务唯一键: (class_id, lecturer_id, course_id, start_date)
-- 这里用 INSERT IGNORE，避免重复执行冲突
-- 依赖已有 teachers/classes 数据（按 teacher_code/class_code 关联）
-- =========================================
INSERT IGNORE INTO `class_teaching_periods`
(`class_id`, `lecturer_id`, `course_id`, `start_date`, `end_date`, `is_deleted`)
VALUES
-- CLS2026A：同一老师同一时间段两门课（符合你确认的“可以”）
(
  (SELECT c.id FROM classes c WHERE c.class_code='CLS2026A' AND c.is_deleted=0 LIMIT 1),
  (SELECT t.id FROM teachers t WHERE t.teacher_code='TCH001' AND t.is_deleted=0 LIMIT 1),
  (SELECT co.id FROM courses co WHERE co.course_code='CRS_PY_BASE' AND co.is_deleted=0 LIMIT 1),
  '2026-04-01', '2026-06-30', 0
),
(
  (SELECT c.id FROM classes c WHERE c.class_code='CLS2026A' AND c.is_deleted=0 LIMIT 1),
  (SELECT t.id FROM teachers t WHERE t.teacher_code='TCH001' AND t.is_deleted=0 LIMIT 1),
  (SELECT co.id FROM courses co WHERE co.course_code='CRS_DB_DESIGN' AND co.is_deleted=0 LIMIT 1),
  '2026-04-01', '2026-06-30', 0
),

-- CLS2026A：另一位老师并行授课
(
  (SELECT c.id FROM classes c WHERE c.class_code='CLS2026A' AND c.is_deleted=0 LIMIT 1),
  (SELECT t.id FROM teachers t WHERE t.teacher_code='TCH002' AND t.is_deleted=0 LIMIT 1),
  (SELECT co.id FROM courses co WHERE co.course_code='CRS_GIT' AND co.is_deleted=0 LIMIT 1),
  '2026-05-01', '2026-05-31', 0
),

-- CLS2026B：当前仍在授课（end_date = NULL）
(
  (SELECT c.id FROM classes c WHERE c.class_code='CLS2026B' AND c.is_deleted=0 LIMIT 1),
  (SELECT t.id FROM teachers t WHERE t.teacher_code='TCH003' AND t.is_deleted=0 LIMIT 1),
  (SELECT co.id FROM courses co WHERE co.course_code='CRS_WEB_FASTAPI' AND co.is_deleted=0 LIMIT 1),
  '2026-06-01', NULL, 0
),

-- CLS2026B：同老师不同课程，同期开课（再次验证“可以多门课”）
(
  (SELECT c.id FROM classes c WHERE c.class_code='CLS2026B' AND c.is_deleted=0 LIMIT 1),
  (SELECT t.id FROM teachers t WHERE t.teacher_code='TCH003' AND t.is_deleted=0 LIMIT 1),
  (SELECT co.id FROM courses co WHERE co.course_code='CRS_SQL_OPT' AND co.is_deleted=0 LIMIT 1),
  '2026-06-01', NULL, 0
);

COMMIT;