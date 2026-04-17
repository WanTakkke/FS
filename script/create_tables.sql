-- 老师表
CREATE TABLE teachers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    teacher_code VARCHAR(50) NOT NULL UNIQUE COMMENT '老师业务编号',
    name VARCHAR(100) NOT NULL COMMENT '姓名',
    phone VARCHAR(20) COMMENT '联系电话',
    email VARCHAR(100) COMMENT '邮箱',
    is_deleted TINYINT(1) DEFAULT 0 COMMENT '逻辑删除标志: 0-未删除, 1-已删除',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT '老师信息表';

-- 班级表
CREATE TABLE classes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    class_code VARCHAR(50) NOT NULL UNIQUE COMMENT '班级业务编号',
    start_date DATE NOT NULL COMMENT '开课时间',
    head_teacher_id INT COMMENT '班主任ID (逻辑关联 teachers.id)',
    is_deleted TINYINT(1) DEFAULT 0 COMMENT '逻辑删除标志',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT '班级信息表';

-- 班级授课周期表
CREATE TABLE class_teaching_periods (
    id INT PRIMARY KEY AUTO_INCREMENT,
    class_id INT NOT NULL COMMENT '班级ID (逻辑关联 classes.id)',
    lecturer_id INT NOT NULL COMMENT '授课老师ID (逻辑关联 teachers.id)',
    start_date DATE NOT NULL COMMENT '授课开始日期',
    end_date DATE COMMENT '授课结束日期 (NULL表示当前仍在授课)',
    is_deleted TINYINT(1) DEFAULT 0 COMMENT '逻辑删除标志',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT '班级授课周期历史表';

-- 学生表
CREATE TABLE students (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_code VARCHAR(50) NOT NULL UNIQUE COMMENT '学生业务编号',
    class_id INT NOT NULL COMMENT '所属班级ID (逻辑关联 classes.id)',
    advisor_id INT COMMENT '顾问老师ID (逻辑关联 teachers.id)',
    name VARCHAR(100) NOT NULL COMMENT '姓名',
    gender TINYINT NOT NULL COMMENT '性别: 0-女, 1-男',
    age INT COMMENT '年龄',
    hometown VARCHAR(100) COMMENT '籍贯',
    graduate_school VARCHAR(100) COMMENT '毕业院校',
    major VARCHAR(100) COMMENT '专业',
    enrollment_date DATE NOT NULL COMMENT '入学时间',
    graduation_date DATE COMMENT '毕业时间',
    education_level VARCHAR(50) COMMENT '学历',
    is_deleted TINYINT(1) DEFAULT 0 COMMENT '逻辑删除标志',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT '学生基本信息表';

-- 成绩表
CREATE TABLE scores (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL COMMENT '学生ID (逻辑关联 students.id)',
    exam_sequence VARCHAR(20) NOT NULL COMMENT '考核序次 (如: 期中, 期末, 阶段1)',
    score DECIMAL(5,2) NOT NULL COMMENT '成绩 (0.00-100.00)',
    is_deleted TINYINT(1) DEFAULT 0 COMMENT '逻辑删除标志',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
--     CHECK (score >= 0.00 AND score <= 100.00)
) COMMENT '学生成绩表';

-- 就业表
CREATE TABLE employments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL COMMENT '学生ID (逻辑关联 students.id)',
    company_name VARCHAR(200) NOT NULL COMMENT '就业公司名称',
    job_open_date DATETIME NOT NULL COMMENT '就业开放时间',
    offer_date DATETIME COMMENT 'offer下发时间',
    salary DECIMAL(10,2) COMMENT '就业薪资 (单位: 元)',
    is_current TINYINT(1) DEFAULT 0 COMMENT '是否当前最新就业: 0-否, 1-是',
    is_deleted TINYINT(1) DEFAULT 0 COMMENT '逻辑删除标志',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT '学生就业信息表';



-- 1. 用户表
CREATE TABLE `sys_user` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `username` VARCHAR(64) NOT NULL COMMENT '用户名',
  `hashed_password` VARCHAR(128) NOT NULL COMMENT '密码哈希',
  `email` VARCHAR(128) DEFAULT NULL COMMENT '邮箱',
  `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用: 1-启用, 0-禁用',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted_at` DATETIME DEFAULT NULL COMMENT '删除时间，NULL表示未删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username_deleted` (`username`, `deleted_at`) COMMENT '用户名唯一索引(兼容软删除)',
  UNIQUE KEY `uk_email_deleted` (`email`, `deleted_at`) COMMENT '邮箱唯一索引(兼容软删除)',
  KEY `idx_created_at` (`created_at`) COMMENT '按创建时间查询的辅助索引'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统用户表';

-- 2. 角色表
CREATE TABLE `sys_role` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `name` VARCHAR(64) NOT NULL COMMENT '角色显示名称(如: 超级管理员)',
  `code` VARCHAR(64) NOT NULL COMMENT '角色编码(如: admin, user)',
  `description` VARCHAR(255) DEFAULT NULL COMMENT '角色描述',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted_at` DATETIME DEFAULT NULL COMMENT '删除时间，NULL表示未删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_code_deleted` (`code`, `deleted_at`) COMMENT '角色编码唯一索引',
  KEY `idx_name` (`name`) COMMENT '角色名称查询索引'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统角色表';

-- 3. 权限表
CREATE TABLE `sys_permission` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `parent_id` BIGINT DEFAULT NULL COMMENT '父级权限ID(用于菜单/权限树)',
  `name` VARCHAR(64) NOT NULL COMMENT '权限显示名称(如: 创建用户)',
  `code` VARCHAR(128) NOT NULL COMMENT '权限编码(如: user:create)',
  `type` VARCHAR(32) NOT NULL COMMENT '权限类型(menu-菜单, button-按钮, api-接口)',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted_at` DATETIME DEFAULT NULL COMMENT '删除时间，NULL表示未删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_code_deleted` (`code`, `deleted_at`) COMMENT '权限编码唯一索引',
  KEY `idx_parent_id` (`parent_id`) COMMENT '父节点查询索引'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统权限表';

-- 4. 用户-角色关联表 (关系表无需软删除，直接硬删保证查询性能)
CREATE TABLE `sys_user_role` (
  `user_id` BIGINT NOT NULL COMMENT '用户ID',
  `role_id` BIGINT NOT NULL COMMENT '角色ID',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '授权时间',
  PRIMARY KEY (`user_id`, `role_id`),
  KEY `idx_role_id` (`role_id`) COMMENT '反向查询：通过角色查用户'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户-角色关联表';

-- 5. 角色-权限关联表 (关系表无需软删除)
CREATE TABLE `sys_role_permission` (
  `role_id` BIGINT NOT NULL COMMENT '角色ID',
  `permission_id` BIGINT NOT NULL COMMENT '权限ID',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '授权时间',
  PRIMARY KEY (`role_id`, `permission_id`),
  KEY `idx_permission_id` (`permission_id`) COMMENT '反向查询：通过权限查角色'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色-权限关联表';