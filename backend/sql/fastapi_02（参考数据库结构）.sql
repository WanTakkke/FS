/*
 Navicat Premium Data Transfer

 Source Server Type    : MySQL
 Source Server Version : 80402 (8.4.2)
 Source Schema         : fastapi_02

 Target Server Type    : MySQL
 Target Server Version : 80402 (8.4.2)
 File Encoding         : 65001

 Date: 22/04/2026 16:34:32
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for class_teaching_periods
-- ----------------------------
DROP TABLE IF EXISTS `class_teaching_periods`;
CREATE TABLE `class_teaching_periods`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `class_id` bigint NOT NULL COMMENT '班级ID (逻辑关联 classes.id)',
  `lecturer_id` bigint NOT NULL COMMENT '授课老师ID (逻辑关联 teachers.id)',
  `course_id` bigint NOT NULL COMMENT '课程ID (逻辑关联 courses.id)',
  `start_date` date NOT NULL COMMENT '授课开始日期',
  `end_date` date NULL DEFAULT NULL COMMENT '授课结束日期 (NULL表示当前仍在授课)',
  `is_deleted` tinyint(1) NULL DEFAULT 0 COMMENT '逻辑删除标志',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_ctp_business`(`class_id` ASC, `lecturer_id` ASC, `course_id` ASC, `start_date` ASC) USING BTREE,
  INDEX `idx_ctp_class_id`(`class_id` ASC) USING BTREE,
  INDEX `idx_ctp_lecturer_id`(`lecturer_id` ASC) USING BTREE,
  INDEX `idx_ctp_course_id`(`course_id` ASC) USING BTREE,
  INDEX `idx_ctp_start_date`(`start_date` ASC) USING BTREE,
  INDEX `idx_ctp_end_date`(`end_date` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 9 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '班级授课周期历史表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of class_teaching_periods
-- ----------------------------
INSERT INTO `class_teaching_periods` VALUES (1, 1, 3, 0, '2026-03-01', '2026-05-31', 0, '2026-04-20 19:43:51', '2026-04-20 19:43:51');
INSERT INTO `class_teaching_periods` VALUES (2, 2, 1, 0, '2026-04-01', NULL, 0, '2026-04-20 19:43:51', '2026-04-20 19:43:51');
INSERT INTO `class_teaching_periods` VALUES (3, 1, 1, 1, '2026-04-01', '2026-06-30', 0, '2026-04-20 23:03:30', '2026-04-20 23:03:30');
INSERT INTO `class_teaching_periods` VALUES (4, 1, 1, 2, '2026-04-01', '2026-06-30', 0, '2026-04-20 23:03:30', '2026-04-20 23:03:30');
INSERT INTO `class_teaching_periods` VALUES (5, 1, 2, 5, '2026-05-01', '2026-05-31', 0, '2026-04-20 23:03:30', '2026-04-20 23:03:30');
INSERT INTO `class_teaching_periods` VALUES (6, 2, 3, 3, '2026-06-01', NULL, 0, '2026-04-20 23:03:30', '2026-04-20 23:03:30');
INSERT INTO `class_teaching_periods` VALUES (7, 2, 3, 4, '2026-06-01', NULL, 0, '2026-04-20 23:03:30', '2026-04-20 23:03:30');
INSERT INTO `class_teaching_periods` VALUES (8, 1, 1, 4, '2026-04-20', '2026-04-20', 1, '2026-04-20 23:38:25', '2026-04-20 23:41:01');

-- ----------------------------
-- Table structure for classes
-- ----------------------------
DROP TABLE IF EXISTS `classes`;
CREATE TABLE `classes`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `class_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '班级业务编号',
  `start_date` date NOT NULL COMMENT '开课时间',
  `head_teacher_id` bigint NULL DEFAULT NULL COMMENT '班主任ID (逻辑关联 teachers.id)',
  `is_deleted` tinyint(1) NULL DEFAULT 0 COMMENT '逻辑删除标志',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `class_code`(`class_code` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '班级信息表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of classes
-- ----------------------------
INSERT INTO `classes` VALUES (1, 'CLS2026A', '2026-03-01', 1, 0, '2026-04-20 19:43:51', '2026-04-20 19:43:51');
INSERT INTO `classes` VALUES (2, 'CLS2026B', '2026-04-01', 2, 0, '2026-04-20 19:43:51', '2026-04-20 19:43:51');
INSERT INTO `classes` VALUES (3, 'CLS2026C', '2026-05-20', 2, 1, '2026-04-20 20:18:07', '2026-04-20 20:22:26');

-- ----------------------------
-- Table structure for courses
-- ----------------------------
DROP TABLE IF EXISTS `courses`;
CREATE TABLE `courses`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `course_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '课程编码(业务唯一)',
  `course_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '课程名称',
  `description` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '课程描述',
  `is_deleted` tinyint(1) NULL DEFAULT 0 COMMENT '逻辑删除标志',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_courses_course_code`(`course_code` ASC) USING BTREE,
  INDEX `idx_courses_name`(`course_name` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '课程表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of courses
-- ----------------------------
INSERT INTO `courses` VALUES (1, 'C001', 'Python基础', 'Python语法、函数、面向对象基础', 0, '2026-04-20 23:03:30', '2026-04-20 23:07:09');
INSERT INTO `courses` VALUES (2, 'C002', '数据库结构', '关系模型、范式、索引与约束设计', 0, '2026-04-20 23:03:30', '2026-04-20 23:07:15');
INSERT INTO `courses` VALUES (3, 'C003', 'FastAPI开发', 'FastAPI接口开发、依赖注入与校验', 0, '2026-04-20 23:03:30', '2026-04-20 23:07:17');
INSERT INTO `courses` VALUES (4, 'C004', 'SQL优化', '执行计划分析、索引优化、慢查询排查', 0, '2026-04-20 23:03:30', '2026-04-20 23:07:20');
INSERT INTO `courses` VALUES (5, 'C005', 'Git协作', '分支策略、冲突处理、代码评审流程', 0, '2026-04-20 23:03:30', '2026-04-20 23:07:25');
INSERT INTO `courses` VALUES (6, 'C006', 'string', 'string', 1, '2026-04-20 23:48:58', '2026-04-20 23:49:35');

-- ----------------------------
-- Table structure for employments
-- ----------------------------
DROP TABLE IF EXISTS `employments`;
CREATE TABLE `employments`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL COMMENT '学生ID (逻辑关联 students.id)',
  `company_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '就业公司名称',
  `job_open_date` datetime NOT NULL COMMENT '就业开放时间',
  `offer_date` datetime NULL DEFAULT NULL COMMENT 'offer下发时间',
  `salary` decimal(10, 2) NULL DEFAULT NULL COMMENT '就业薪资 (单位: 元)',
  `is_current` tinyint(1) NULL DEFAULT 0 COMMENT '是否当前最新就业: 0-否, 1-是',
  `is_deleted` tinyint(1) NULL DEFAULT 0 COMMENT '逻辑删除标志',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 8 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '学生就业信息表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of employments
-- ----------------------------
INSERT INTO `employments` VALUES (1, 5, '腾讯科技', '2026-10-01 10:00:00', '2026-10-20 15:00:00', 18000.00, 1, 0, '2026-04-20 19:45:22', '2026-04-20 19:45:22');
INSERT INTO `employments` VALUES (2, 6, '阿里巴巴', '2026-10-05 09:30:00', '2026-10-25 14:00:00', 17000.00, 0, 0, '2026-04-20 19:45:22', '2026-04-20 22:38:50');
INSERT INTO `employments` VALUES (6, 6, '亚特拉迪斯', '2026-04-20 14:37:55', '2026-04-20 14:37:55', 9999.00, 1, 1, '2026-04-20 22:44:45', '2026-04-20 22:51:48');

-- ----------------------------
-- Table structure for scores
-- ----------------------------
DROP TABLE IF EXISTS `scores`;
CREATE TABLE `scores`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `student_id` bigint NOT NULL COMMENT '学生ID (逻辑关联 students.id)',
  `exam_sequence` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '考核序次 (如: 期中, 期末, 阶段1)',
  `score` decimal(5, 2) NOT NULL COMMENT '成绩 (0.00-100.00)',
  `is_deleted` tinyint(1) NULL DEFAULT 0 COMMENT '逻辑删除标志',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '学生成绩表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of scores
-- ----------------------------
INSERT INTO `scores` VALUES (1, 5, '期中', 86.50, 0, '2026-04-20 19:43:51', '2026-04-20 21:55:00');
INSERT INTO `scores` VALUES (2, 5, '期末', 90.00, 0, '2026-04-20 19:43:51', '2026-04-20 19:43:51');
INSERT INTO `scores` VALUES (3, 6, '期中', 79.00, 0, '2026-04-20 19:43:51', '2026-04-20 19:43:51');
INSERT INTO `scores` VALUES (4, 7, '期中', 92.00, 0, '2026-04-20 19:43:51', '2026-04-20 19:43:51');
INSERT INTO `scores` VALUES (5, 7, '0420月考', 98.12, 1, '2026-04-20 21:16:26', '2026-04-20 22:03:13');
INSERT INTO `scores` VALUES (6, 7, '0420月考', 98.12, 0, '2026-04-20 22:05:58', '2026-04-20 22:05:58');

-- ----------------------------
-- Table structure for students
-- ----------------------------
DROP TABLE IF EXISTS `students`;
CREATE TABLE `students`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `student_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '学生业务编号',
  `class_id` bigint NOT NULL COMMENT '所属班级ID (逻辑关联 classes.id)',
  `advisor_id` bigint NULL DEFAULT NULL COMMENT '顾问老师ID (逻辑关联 teachers.id)',
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '姓名',
  `gender` tinyint NOT NULL COMMENT '性别: 0-女, 1-男',
  `age` int NULL DEFAULT NULL COMMENT '年龄',
  `hometown` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '籍贯',
  `graduate_school` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '毕业院校',
  `major` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '专业',
  `enrollment_date` date NOT NULL COMMENT '入学时间',
  `graduation_date` date NULL DEFAULT NULL COMMENT '毕业时间',
  `education_level` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '学历',
  `is_deleted` tinyint(1) NULL DEFAULT 0 COMMENT '逻辑删除标志',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `student_code`(`student_code` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 8 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '学生基本信息表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of students
-- ----------------------------
INSERT INTO `students` VALUES (4, '废弃', 1, 100, '李四', 1, 20, '北京', '清华大学', '计算机科学', '2024-09-01', '2028-07-01', '本科', 1, '2026-04-17 16:39:09', '2026-04-20 21:13:51');
INSERT INTO `students` VALUES (5, 'S2026001', 1, 2, '李四', 1, 23, '北京', '北京大学', '计算机科学', '2026-03-05', NULL, '本科', 0, '2026-04-20 19:43:51', '2026-04-20 19:49:42');
INSERT INTO `students` VALUES (6, 'S2026002', 1, 3, '王五', 0, 22, '上海', '复旦大学', '软件工程', '2026-03-06', NULL, '本科', 0, '2026-04-20 19:43:51', '2026-04-20 19:49:44');
INSERT INTO `students` VALUES (7, 'S2026003', 2, 1, '赵六', 1, 24, '广州', '中山大学', '信息管理', '2026-04-02', NULL, '本科', 0, '2026-04-20 19:43:51', '2026-04-20 19:49:46');

-- ----------------------------
-- Table structure for sys_audit_log
-- ----------------------------
DROP TABLE IF EXISTS `sys_audit_log`;
CREATE TABLE `sys_audit_log`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `module` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '模块名称，如rbac',
  `action` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '动作编码，如role.create',
  `operator_id` bigint NULL DEFAULT NULL COMMENT '操作者用户ID',
  `operator_username` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '操作者用户名',
  `target_type` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '目标类型，如role/user',
  `target_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '目标标识',
  `detail_json` json NULL COMMENT '变更详情JSON',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_sal_module_action`(`module` ASC, `action` ASC) USING BTREE,
  INDEX `idx_sal_operator_id`(`operator_id` ASC) USING BTREE,
  INDEX `idx_sal_created_at`(`created_at` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '系统审计日志表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_audit_log
-- ----------------------------

-- ----------------------------
-- Table structure for sys_permission
-- ----------------------------
DROP TABLE IF EXISTS `sys_permission`;
CREATE TABLE `sys_permission`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `parent_id` bigint NULL DEFAULT NULL COMMENT '父级权限ID(用于菜单/权限树)',
  `name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '权限显示名称(如: 创建用户)',
  `code` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '权限编码(如: user:create)',
  `type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '权限类型(menu-菜单, button-按钮, api-接口)',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted_at` datetime NULL DEFAULT NULL COMMENT '删除时间，NULL表示未删除',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_code_deleted`(`code` ASC, `deleted_at` ASC) USING BTREE COMMENT '权限编码唯一索引',
  INDEX `idx_parent_id`(`parent_id` ASC) USING BTREE COMMENT '父节点查询索引'
) ENGINE = InnoDB AUTO_INCREMENT = 47 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '系统权限表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_permission
-- ----------------------------
INSERT INTO `sys_permission` VALUES (1, NULL, '角色查询', 'rbac:role:read', 'api', '2026-04-22 11:24:56', '2026-04-22 11:24:56', NULL);
INSERT INTO `sys_permission` VALUES (2, NULL, '角色创建', 'rbac:role:create', 'api', '2026-04-22 11:24:56', '2026-04-22 11:24:56', NULL);
INSERT INTO `sys_permission` VALUES (3, NULL, '角色更新', 'rbac:role:update', 'api', '2026-04-22 11:24:56', '2026-04-22 11:24:56', NULL);
INSERT INTO `sys_permission` VALUES (4, NULL, '角色删除', 'rbac:role:delete', 'api', '2026-04-22 11:24:56', '2026-04-22 11:24:56', NULL);
INSERT INTO `sys_permission` VALUES (5, NULL, '权限查询', 'rbac:permission:read', 'api', '2026-04-22 11:24:56', '2026-04-22 11:24:56', NULL);
INSERT INTO `sys_permission` VALUES (6, NULL, '用户绑定角色', 'rbac:user:bind_role', 'api', '2026-04-22 11:24:56', '2026-04-22 11:24:56', NULL);
INSERT INTO `sys_permission` VALUES (7, NULL, '角色绑定权限', 'rbac:role:bind_permission', 'api', '2026-04-22 11:24:56', '2026-04-22 11:24:56', NULL);
INSERT INTO `sys_permission` VALUES (8, NULL, '学生查询', 'student:read', 'api', '2026-04-22 11:24:56', '2026-04-22 11:24:56', NULL);
INSERT INTO `sys_permission` VALUES (9, NULL, '学生新增', 'student:create', 'api', '2026-04-22 11:24:56', '2026-04-22 11:24:56', NULL);
INSERT INTO `sys_permission` VALUES (10, NULL, '学生更新', 'student:update', 'api', '2026-04-22 11:24:56', '2026-04-22 11:24:56', NULL);
INSERT INTO `sys_permission` VALUES (11, NULL, '学生删除', 'student:delete', 'api', '2026-04-22 11:24:56', '2026-04-22 11:24:56', NULL);
INSERT INTO `sys_permission` VALUES (12, NULL, '成绩查询', 'score:read', 'api', '2026-04-22 11:24:56', '2026-04-22 11:24:56', NULL);
INSERT INTO `sys_permission` VALUES (13, NULL, '成绩新增', 'score:create', 'api', '2026-04-22 11:24:56', '2026-04-22 11:24:56', NULL);
INSERT INTO `sys_permission` VALUES (14, NULL, '成绩更新', 'score:update', 'api', '2026-04-22 11:24:56', '2026-04-22 11:24:56', NULL);
INSERT INTO `sys_permission` VALUES (15, NULL, '成绩删除', 'score:delete', 'api', '2026-04-22 11:24:56', '2026-04-22 11:24:56', NULL);
INSERT INTO `sys_permission` VALUES (16, NULL, '班级查询', 'class:read', 'api', '2026-04-22 11:38:03', '2026-04-22 11:38:03', NULL);
INSERT INTO `sys_permission` VALUES (17, NULL, '班级新增', 'class:create', 'api', '2026-04-22 11:38:03', '2026-04-22 11:38:03', NULL);
INSERT INTO `sys_permission` VALUES (18, NULL, '班级更新', 'class:update', 'api', '2026-04-22 11:38:03', '2026-04-22 11:38:03', NULL);
INSERT INTO `sys_permission` VALUES (19, NULL, '班级删除', 'class:delete', 'api', '2026-04-22 11:38:03', '2026-04-22 11:38:03', NULL);
INSERT INTO `sys_permission` VALUES (20, NULL, '课程查询', 'course:read', 'api', '2026-04-22 11:38:03', '2026-04-22 11:38:03', NULL);
INSERT INTO `sys_permission` VALUES (21, NULL, '课程新增', 'course:create', 'api', '2026-04-22 11:38:03', '2026-04-22 11:38:03', NULL);
INSERT INTO `sys_permission` VALUES (22, NULL, '课程更新', 'course:update', 'api', '2026-04-22 11:38:03', '2026-04-22 11:38:03', NULL);
INSERT INTO `sys_permission` VALUES (23, NULL, '课程删除', 'course:delete', 'api', '2026-04-22 11:38:03', '2026-04-22 11:38:03', NULL);
INSERT INTO `sys_permission` VALUES (24, NULL, '就业查询', 'employment:read', 'api', '2026-04-22 11:38:03', '2026-04-22 11:38:03', NULL);
INSERT INTO `sys_permission` VALUES (25, NULL, '就业新增', 'employment:create', 'api', '2026-04-22 11:38:03', '2026-04-22 11:38:03', NULL);
INSERT INTO `sys_permission` VALUES (26, NULL, '就业更新', 'employment:update', 'api', '2026-04-22 11:38:03', '2026-04-22 11:38:03', NULL);
INSERT INTO `sys_permission` VALUES (27, NULL, '就业删除', 'employment:delete', 'api', '2026-04-22 11:38:03', '2026-04-22 11:38:03', NULL);
INSERT INTO `sys_permission` VALUES (28, NULL, '班级授课查询', 'class_teaching:read', 'api', '2026-04-22 11:38:03', '2026-04-22 11:38:03', NULL);
INSERT INTO `sys_permission` VALUES (29, NULL, '班级授课新增', 'class_teaching:create', 'api', '2026-04-22 11:38:03', '2026-04-22 11:38:03', NULL);
INSERT INTO `sys_permission` VALUES (30, NULL, '班级授课更新', 'class_teaching:update', 'api', '2026-04-22 11:38:03', '2026-04-22 11:38:03', NULL);
INSERT INTO `sys_permission` VALUES (31, NULL, '班级授课删除', 'class_teaching:delete', 'api', '2026-04-22 11:38:03', '2026-04-22 11:38:03', NULL);
INSERT INTO `sys_permission` VALUES (32, NULL, 'AI对话', 'ai:chat', 'api', '2026-04-22 11:38:03', '2026-04-22 11:38:03', NULL);
INSERT INTO `sys_permission` VALUES (33, NULL, 'AI Text2SQL', 'ai:text2sql', 'api', '2026-04-22 11:38:03', '2026-04-22 11:38:03', NULL);

-- ----------------------------
-- Table structure for sys_refresh_token
-- ----------------------------
DROP TABLE IF EXISTS `sys_refresh_token`;
CREATE TABLE `sys_refresh_token`  (
  `token_jti` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'refresh token唯一ID(JTI)',
  `user_id` bigint NOT NULL COMMENT '用户ID',
  `expires_at` datetime NOT NULL COMMENT 'refresh token过期时间',
  `revoked_at` datetime NULL DEFAULT NULL COMMENT '失效时间，NULL表示有效',
  `replaced_by_jti` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '被轮换的新token_jti',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`token_jti`) USING BTREE,
  INDEX `idx_srt_user_id`(`user_id` ASC) USING BTREE,
  INDEX `idx_srt_expires_at`(`expires_at` ASC) USING BTREE,
  INDEX `idx_srt_revoked_at`(`revoked_at` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '刷新令牌表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_refresh_token
-- ----------------------------

-- ----------------------------
-- Table structure for sys_role
-- ----------------------------
DROP TABLE IF EXISTS `sys_role`;
CREATE TABLE `sys_role`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '角色显示名称(如: 超级管理员)',
  `code` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '角色编码(如: admin, user)',
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '角色描述',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted_at` datetime NULL DEFAULT NULL COMMENT '删除时间，NULL表示未删除',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_code_deleted`(`code` ASC, `deleted_at` ASC) USING BTREE COMMENT '角色编码唯一索引',
  INDEX `idx_name`(`name` ASC) USING BTREE COMMENT '角色名称查询索引'
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '系统角色表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_role
-- ----------------------------
INSERT INTO `sys_role` VALUES (1, '超级管理员', 'admin', '系统超级管理员', '2026-04-22 11:24:56', '2026-04-22 11:24:56', NULL);
INSERT INTO `sys_role` VALUES (2, '教务老师', 'teacher', '教学业务操作角色', '2026-04-22 11:24:56', '2026-04-22 11:24:56', NULL);

-- ----------------------------
-- Table structure for sys_role_permission
-- ----------------------------
DROP TABLE IF EXISTS `sys_role_permission`;
CREATE TABLE `sys_role_permission`  (
  `role_id` bigint NOT NULL COMMENT '角色ID',
  `permission_id` bigint NOT NULL COMMENT '权限ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '授权时间',
  PRIMARY KEY (`role_id`, `permission_id`) USING BTREE,
  INDEX `idx_permission_id`(`permission_id` ASC) USING BTREE COMMENT '反向查询：通过权限查角色'
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '角色-权限关联表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_role_permission
-- ----------------------------
INSERT INTO `sys_role_permission` VALUES (1, 1, '2026-04-22 11:24:56');
INSERT INTO `sys_role_permission` VALUES (1, 2, '2026-04-22 11:24:56');
INSERT INTO `sys_role_permission` VALUES (1, 3, '2026-04-22 11:24:56');
INSERT INTO `sys_role_permission` VALUES (1, 4, '2026-04-22 11:24:56');
INSERT INTO `sys_role_permission` VALUES (1, 5, '2026-04-22 11:24:56');
INSERT INTO `sys_role_permission` VALUES (1, 6, '2026-04-22 11:24:56');
INSERT INTO `sys_role_permission` VALUES (1, 7, '2026-04-22 11:24:56');
INSERT INTO `sys_role_permission` VALUES (1, 8, '2026-04-22 11:24:56');
INSERT INTO `sys_role_permission` VALUES (1, 9, '2026-04-22 11:24:56');
INSERT INTO `sys_role_permission` VALUES (1, 10, '2026-04-22 11:24:56');
INSERT INTO `sys_role_permission` VALUES (1, 11, '2026-04-22 11:24:56');
INSERT INTO `sys_role_permission` VALUES (1, 12, '2026-04-22 11:24:56');
INSERT INTO `sys_role_permission` VALUES (1, 13, '2026-04-22 11:24:56');
INSERT INTO `sys_role_permission` VALUES (1, 14, '2026-04-22 11:24:56');
INSERT INTO `sys_role_permission` VALUES (1, 15, '2026-04-22 11:24:56');
INSERT INTO `sys_role_permission` VALUES (1, 16, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (1, 17, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (1, 18, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (1, 19, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (1, 20, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (1, 21, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (1, 22, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (1, 23, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (1, 24, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (1, 25, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (1, 26, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (1, 27, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (1, 28, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (1, 29, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (1, 30, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (1, 31, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (1, 32, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (1, 33, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (2, 8, '2026-04-22 11:24:56');
INSERT INTO `sys_role_permission` VALUES (2, 9, '2026-04-22 11:24:56');
INSERT INTO `sys_role_permission` VALUES (2, 10, '2026-04-22 11:24:56');
INSERT INTO `sys_role_permission` VALUES (2, 11, '2026-04-22 11:24:56');
INSERT INTO `sys_role_permission` VALUES (2, 12, '2026-04-22 11:24:56');
INSERT INTO `sys_role_permission` VALUES (2, 13, '2026-04-22 11:24:56');
INSERT INTO `sys_role_permission` VALUES (2, 14, '2026-04-22 11:24:56');
INSERT INTO `sys_role_permission` VALUES (2, 15, '2026-04-22 11:24:56');
INSERT INTO `sys_role_permission` VALUES (2, 16, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (2, 17, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (2, 18, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (2, 19, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (2, 20, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (2, 21, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (2, 22, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (2, 23, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (2, 24, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (2, 25, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (2, 26, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (2, 27, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (2, 28, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (2, 29, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (2, 30, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (2, 31, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (2, 32, '2026-04-22 11:38:03');
INSERT INTO `sys_role_permission` VALUES (2, 33, '2026-04-22 11:38:03');

-- ----------------------------
-- Table structure for sys_user
-- ----------------------------
DROP TABLE IF EXISTS `sys_user`;
CREATE TABLE `sys_user`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `username` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户名',
  `hashed_password` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '密码哈希',
  `email` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '邮箱',
  `is_active` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否启用: 1-启用, 0-禁用',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted_at` datetime NULL DEFAULT NULL COMMENT '删除时间，NULL表示未删除',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_username_deleted`(`username` ASC, `deleted_at` ASC) USING BTREE COMMENT '用户名唯一索引(兼容软删除)',
  UNIQUE INDEX `uk_email_deleted`(`email` ASC, `deleted_at` ASC) USING BTREE COMMENT '邮箱唯一索引(兼容软删除)',
  INDEX `idx_created_at`(`created_at` ASC) USING BTREE COMMENT '按创建时间查询的辅助索引'
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '系统用户表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_user
-- ----------------------------
INSERT INTO `sys_user` VALUES (2, 'admin', '$2b$12$8E3LmZ.GpLpEUFlPvUCeZulwao/0qsnw52YxcrPI2q23VOOHsOxaK', NULL, 1, '2026-04-17 21:07:43', '2026-04-17 21:07:43', NULL);
INSERT INTO `sys_user` VALUES (3, '张三', '$2b$12$K17iyNtPNiI59lkKwCHIHOW2U4TRlpkjnqFTstfST/Nm.rGrYPlVG', NULL, 1, '2026-04-17 21:08:41', '2026-04-17 21:08:41', NULL);
INSERT INTO `sys_user` VALUES (4, '李四', '$2b$12$fimy5f.AeJueZFI1hN2a5uEsZ78iUJFQ1V.8ZYnr3k9nA5mLCPiLm', '123@qq.com', 1, '2026-04-17 21:20:00', '2026-04-17 21:20:00', NULL);

-- ----------------------------
-- Table structure for sys_user_role
-- ----------------------------
DROP TABLE IF EXISTS `sys_user_role`;
CREATE TABLE `sys_user_role`  (
  `user_id` bigint NOT NULL COMMENT '用户ID',
  `role_id` bigint NOT NULL COMMENT '角色ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '授权时间',
  PRIMARY KEY (`user_id`, `role_id`) USING BTREE,
  INDEX `idx_role_id`(`role_id` ASC) USING BTREE COMMENT '反向查询：通过角色查用户'
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '用户-角色关联表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_user_role
-- ----------------------------
INSERT INTO `sys_user_role` VALUES (2, 1, '2026-04-22 11:24:56');

-- ----------------------------
-- Table structure for teachers
-- ----------------------------
DROP TABLE IF EXISTS `teachers`;
CREATE TABLE `teachers`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `teacher_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '老师业务编号',
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '姓名',
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '联系电话',
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '邮箱',
  `is_deleted` tinyint(1) NULL DEFAULT 0 COMMENT '逻辑删除标志: 0-未删除, 1-已删除',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `teacher_code`(`teacher_code` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '老师信息表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of teachers
-- ----------------------------
INSERT INTO `teachers` VALUES (1, 'TCH001', '张老师', '13800000001', 'zhang.teacher@example.com', 0, '2026-04-20 19:43:51', '2026-04-20 19:43:51');
INSERT INTO `teachers` VALUES (2, 'TCH002', '李老师', '13800000002', 'li.teacher@example.com', 0, '2026-04-20 19:43:51', '2026-04-20 19:43:51');
INSERT INTO `teachers` VALUES (3, 'TCH003', '王老师', '13800000003', 'wang.teacher@example.com', 0, '2026-04-20 19:43:51', '2026-04-20 19:43:51');

SET FOREIGN_KEY_CHECKS = 1;
