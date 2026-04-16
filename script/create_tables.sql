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