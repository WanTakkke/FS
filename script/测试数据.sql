-- 可选：先切库
-- USE project01;

START TRANSACTION;

-- 1) teachers
INSERT IGNORE INTO teachers
(teacher_code, name, phone, email, is_deleted)
VALUES
('TCH001', '张老师', '13800000001', 'zhang.teacher@example.com', 0),
('TCH002', '李老师', '13800000002', 'li.teacher@example.com', 0),
('TCH003', '王老师', '13800000003', 'wang.teacher@example.com', 0);

-- 2) classes
INSERT IGNORE INTO classes
(class_code, start_date, head_teacher_id, is_deleted)
VALUES
('CLS2026A', '2026-03-01', (SELECT id FROM teachers WHERE teacher_code='TCH001' AND is_deleted=0 LIMIT 1), 0),
('CLS2026B', '2026-04-01', (SELECT id FROM teachers WHERE teacher_code='TCH002' AND is_deleted=0 LIMIT 1), 0);

-- 3) class_teaching_periods
INSERT IGNORE INTO class_teaching_periods
(class_id, lecturer_id, start_date, end_date, is_deleted)
VALUES
(
  (SELECT id FROM classes WHERE class_code='CLS2026A' AND is_deleted=0 LIMIT 1),
  (SELECT id FROM teachers WHERE teacher_code='TCH003' AND is_deleted=0 LIMIT 1),
  '2026-03-01', '2026-05-31', 0
),
(
  (SELECT id FROM classes WHERE class_code='CLS2026B' AND is_deleted=0 LIMIT 1),
  (SELECT id FROM teachers WHERE teacher_code='TCH001' AND is_deleted=0 LIMIT 1),
  '2026-04-01', NULL, 0
);

-- 4) students
INSERT IGNORE INTO students
(student_code, class_id, advisor_id, name, gender, age, hometown, graduate_school, major, enrollment_date, graduation_date, education_level, is_deleted)
VALUES
(
  'STU001',
  (SELECT id FROM classes WHERE class_code='CLS2026A' AND is_deleted=0 LIMIT 1),
  (SELECT id FROM teachers WHERE teacher_code='TCH002' AND is_deleted=0 LIMIT 1),
  '李四', 1, 23, '北京', '北京大学', '计算机科学', '2026-03-05', NULL, '本科', 0
),
(
  'STU002',
  (SELECT id FROM classes WHERE class_code='CLS2026A' AND is_deleted=0 LIMIT 1),
  (SELECT id FROM teachers WHERE teacher_code='TCH003' AND is_deleted=0 LIMIT 1),
  '王五', 0, 22, '上海', '复旦大学', '软件工程', '2026-03-06', NULL, '本科', 0
),
(
  'STU003',
  (SELECT id FROM classes WHERE class_code='CLS2026B' AND is_deleted=0 LIMIT 1),
  (SELECT id FROM teachers WHERE teacher_code='TCH001' AND is_deleted=0 LIMIT 1),
  '赵六', 1, 24, '广州', '中山大学', '信息管理', '2026-04-02', NULL, '本科', 0
);

-- 5) scores
INSERT IGNORE INTO scores
(student_id, exam_sequence, score, is_deleted)
VALUES
((SELECT id FROM students WHERE student_code='STU001' AND is_deleted=0 LIMIT 1), '期中', 86.50, 0),
((SELECT id FROM students WHERE student_code='STU001' AND is_deleted=0 LIMIT 1), '期末', 90.00, 0),
((SELECT id FROM students WHERE student_code='STU002' AND is_deleted=0 LIMIT 1), '期中', 79.00, 0),
((SELECT id FROM students WHERE student_code='STU003' AND is_deleted=0 LIMIT 1), '期中', 92.00, 0);

-- 6) employments
INSERT IGNORE INTO employments
(student_id, company_name, job_open_date, offer_date, salary, is_current, is_deleted)
VALUES
(
  (SELECT id FROM students WHERE student_code='STU001' AND is_deleted=0 LIMIT 1),
  '腾讯科技', '2026-10-01 10:00:00', '2026-10-20 15:00:00', 18000.00, 1, 0
),
(
  (SELECT id FROM students WHERE student_code='STU002' AND is_deleted=0 LIMIT 1),
  '阿里巴巴', '2026-10-05 09:30:00', '2026-10-25 14:00:00', 17000.00, 1, 0
);

-- -- 7) sys_user
-- -- 注意：hashed_password 这里是示例字符串，真实环境请用 bcrypt 等加密后的值
-- INSERT IGNORE INTO sys_user
-- (username, hashed_password, email, is_active, deleted_at)
-- VALUES
-- ('admin', '$2b$12$abcdefghijklmnopqrstuv1234567890abcdefghi', 'admin@example.com', 1, NULL),
-- ('operator', '$2b$12$mnopqrstuvwxyzabcdef1234567890abcdefghijkl', 'operator@example.com', 1, NULL);
--
-- -- 8) sys_role
-- INSERT IGNORE INTO sys_role
-- (name, code, description, deleted_at)
-- VALUES
-- ('超级管理员', 'admin', '系统最高权限角色', NULL),
-- ('普通用户', 'user', '基础操作权限角色', NULL);
--
-- -- 9) sys_permission
-- INSERT IGNORE INTO sys_permission
-- (parent_id, name, code, type, deleted_at)
-- VALUES
-- (NULL, '用户管理', 'user:menu', 'menu', NULL),
-- (NULL, '班级管理', 'class:menu', 'menu', NULL),
-- (NULL, '学生管理', 'student:menu', 'menu', NULL),
-- (NULL, '创建用户', 'user:create', 'api', NULL),
-- (NULL, '查询班级', 'class:query', 'api', NULL),
-- (NULL, '新增学生', 'student:add', 'api', NULL);
--
-- -- 10) sys_user_role
-- INSERT IGNORE INTO sys_user_role (user_id, role_id, created_at)
-- SELECT u.id, r.id, NOW()
-- FROM sys_user u
-- JOIN sys_role r ON r.code = 'admin' AND r.deleted_at IS NULL
-- WHERE u.username = 'admin' AND u.deleted_at IS NULL;
--
-- INSERT IGNORE INTO sys_user_role (user_id, role_id, created_at)
-- SELECT u.id, r.id, NOW()
-- FROM sys_user u
-- JOIN sys_role r ON r.code = 'user' AND r.deleted_at IS NULL
-- WHERE u.username = 'operator' AND u.deleted_at IS NULL;
--
-- -- 11) sys_role_permission
-- -- admin 角色授予全部示例权限
-- INSERT IGNORE INTO sys_role_permission (role_id, permission_id, created_at)
-- SELECT r.id, p.id, NOW()
-- FROM sys_role r
-- JOIN sys_permission p ON p.deleted_at IS NULL
-- WHERE r.code = 'admin' AND r.deleted_at IS NULL;
--
-- -- user 角色授予部分权限
-- INSERT IGNORE INTO sys_role_permission (role_id, permission_id, created_at)
-- SELECT r.id, p.id, NOW()
-- FROM sys_role r
-- JOIN sys_permission p ON p.code IN ('class:query', 'student:add') AND p.deleted_at IS NULL
-- WHERE r.code = 'user' AND r.deleted_at IS NULL;

COMMIT;