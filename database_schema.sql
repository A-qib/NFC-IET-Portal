-- ═══════════════════════════════════════════════════════════════
-- NFC IET Portal — Complete Database Schema
-- Generated from app.py analysis + standard academic portal structure
-- ═══════════════════════════════════════════════════════════════

-- Drop and recreate database
DROP DATABASE IF EXISTS nfc_portal;
CREATE DATABASE nfc_portal CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE nfc_portal;

-- ═══════════════════════════════════════════════════════════════
-- 1. CORE TABLES
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE departments (
    dept_id     INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    code        VARCHAR(10) UNIQUE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE programs (
    program_id  INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    dept_id     INT NOT NULL,
    duration_years INT DEFAULT 4,
    total_semesters INT DEFAULT 8,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id) ON DELETE CASCADE
);

CREATE TABLE users (
    user_id     INT AUTO_INCREMENT PRIMARY KEY,
    email       VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role        ENUM('admin','student','teacher') NOT NULL DEFAULT 'student',
    photo       VARCHAR(255),
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login  TIMESTAMP NULL
);

CREATE TABLE students (
    student_id  INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT UNIQUE NOT NULL,
    name        VARCHAR(100) NOT NULL,
    roll_no     VARCHAR(20) UNIQUE NOT NULL,
    program_id  INT NOT NULL,
    batch       VARCHAR(10) NOT NULL,
    semester    INT NOT NULL DEFAULT 1,
    phone       VARCHAR(20),
    gender      ENUM('male','female','other'),
    address     TEXT,
    dob         DATE,
    cnic        VARCHAR(15),
    guardian_name VARCHAR(100),
    guardian_phone VARCHAR(20),
    admission_date DATE,
    status      ENUM('active','suspended','graduated','dropped') DEFAULT 'active',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (program_id) REFERENCES programs(program_id)
);

CREATE TABLE teachers (
    teacher_id  INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT UNIQUE NOT NULL,
    name        VARCHAR(100) NOT NULL,
    dept_id     INT NOT NULL,
    designation VARCHAR(50) NOT NULL,
    phone       VARCHAR(20),
    qualification VARCHAR(100),
    specialization VARCHAR(100),
    joining_date DATE,
    status      ENUM('active','on_leave','retired') DEFAULT 'active',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
);

-- ═══════════════════════════════════════════════════════════════
-- 2. ACADEMIC TABLES
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE courses (
    course_id   INT AUTO_INCREMENT PRIMARY KEY,
    code        VARCHAR(20) UNIQUE NOT NULL,
    name        VARCHAR(100) NOT NULL,
    dept_id     INT NOT NULL,
    credit_hours INT NOT NULL DEFAULT 3,
    total_marks  INT DEFAULT 100,
    mid_weight   INT DEFAULT 30,
    final_weight INT DEFAULT 50,
    assign_weight INT DEFAULT 20,
    description  TEXT,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
);

CREATE TABLE sections (
    section_id  INT AUTO_INCREMENT PRIMARY KEY,
    course_id   INT NOT NULL,
    teacher_id  INT NOT NULL,
    section_label VARCHAR(10) NOT NULL,
    semester    VARCHAR(10) NOT NULL,
    year        INT NOT NULL,
    max_students INT DEFAULT 50,
    room        VARCHAR(20),
    FOREIGN KEY (course_id) REFERENCES courses(course_id),
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id),
    UNIQUE KEY unique_section (course_id, section_label, semester, year)
);

CREATE TABLE enrollments (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id  INT NOT NULL,
    section_id  INT NOT NULL,
    enroll_date DATE DEFAULT (CURRENT_DATE),
    status      ENUM('active','dropped','completed') DEFAULT 'active',
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES sections(section_id) ON DELETE CASCADE,
    UNIQUE KEY unique_enrollment (student_id, section_id)
);

CREATE TABLE grades (
    grade_id    INT AUTO_INCREMENT PRIMARY KEY,
    enrollment_id INT UNIQUE NOT NULL,
    mid_marks   DECIMAL(5,2) DEFAULT 0,
    final_marks DECIMAL(5,2) DEFAULT 0,
    assignment_marks DECIMAL(5,2) DEFAULT 0,
    total       DECIMAL(5,2) GENERATED ALWAYS AS (
        COALESCE(mid_marks,0) + COALESCE(final_marks,0) + COALESCE(assignment_marks,0)
    ) STORED,
    FOREIGN KEY (enrollment_id) REFERENCES enrollments(enrollment_id) ON DELETE CASCADE
);

CREATE TABLE attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    enrollment_id INT NOT NULL,
    date        DATE NOT NULL,
    status      ENUM('present','absent','late','excused') NOT NULL DEFAULT 'present',
    marked_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (enrollment_id) REFERENCES enrollments(enrollment_id) ON DELETE CASCADE,
    UNIQUE KEY unique_attendance (enrollment_id, date)
);

CREATE TABLE timetable (
    timetable_id INT AUTO_INCREMENT PRIMARY KEY,
    section_id  INT NOT NULL,
    day         ENUM('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday') NOT NULL,
    start_time  TIME NOT NULL,
    end_time    TIME NOT NULL,
    room        VARCHAR(20),
    FOREIGN KEY (section_id) REFERENCES sections(section_id) ON DELETE CASCADE
);

CREATE TABLE announcements (
    announcement_id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id  INT NOT NULL,
    section_id  INT NOT NULL,
    title       VARCHAR(200) NOT NULL,
    body        TEXT NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES sections(section_id) ON DELETE CASCADE
);

-- ═══════════════════════════════════════════════════════════════
-- 3. FINANCIAL TABLES
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE fee_records (
    fee_id      INT AUTO_INCREMENT PRIMARY KEY,
    student_id  INT NOT NULL,
    semester    VARCHAR(10) NOT NULL,
    year        INT NOT NULL,
    amount      DECIMAL(10,2) NOT NULL,
    due_date    DATE NOT NULL,
    status      ENUM('pending','paid','overdue','waived') DEFAULT 'pending',
    paid_at     TIMESTAMP NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

-- ═══════════════════════════════════════════════════════════════
-- 4. NOTIFICATIONS
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    type        ENUM('info','warning','success','error') DEFAULT 'info',
    title       VARCHAR(200) NOT NULL,
    message     TEXT NOT NULL,
    is_read     BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ═══════════════════════════════════════════════════════════════
-- 5. VIEWS (for app.py compatibility)
-- ═══════════════════════════════════════════════════════════════

CREATE VIEW vw_section_details AS
SELECT 
    s.section_id,
    c.course_id,
    c.name AS course_name,
    c.code AS course_code,
    c.credit_hours,
    t.name AS teacher_name,
    t.teacher_id,
    s.section_label,
    s.semester,
    s.year,
    s.room
FROM sections s
JOIN courses c ON c.course_id = s.course_id
JOIN teachers t ON t.teacher_id = s.teacher_id;

CREATE VIEW vw_attendance_summary AS
SELECT 
    e.enrollment_id,
    COUNT(a.attendance_id) AS total_classes,
    SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) AS present_count,
    SUM(CASE WHEN a.status = 'absent' THEN 1 ELSE 0 END) AS absent_count,
    SUM(CASE WHEN a.status = 'late' THEN 1 ELSE 0 END) AS late_count,
    ROUND(
        (SUM(CASE WHEN a.status IN ('present','late') THEN 1 ELSE 0 END) / COUNT(a.attendance_id)) * 100, 
        1
    ) AS attendance_pct,
    CASE 
        WHEN (SUM(CASE WHEN a.status IN ('present','late') THEN 1 ELSE 0 END) / COUNT(a.attendance_id)) * 100 < 75 
        THEN 'SHORTAGE' 
        ELSE 'OK' 
    END AS attendance_status
FROM enrollments e
LEFT JOIN attendance a ON a.enrollment_id = e.enrollment_id
GROUP BY e.enrollment_id;

CREATE VIEW vw_shortage_alerts AS
SELECT 
    st.student_id,
    st.name AS student_name,
    st.roll_no,
    c.code AS course_code,
    c.name AS course_name,
    vas.attendance_pct
FROM students st
JOIN enrollments e ON e.student_id = st.student_id
JOIN vw_attendance_summary vas ON vas.enrollment_id = e.enrollment_id
JOIN sections s ON s.section_id = e.section_id
JOIN courses c ON c.course_id = s.course_id
WHERE vas.attendance_status = 'SHORTAGE';

CREATE VIEW vw_teacher_dashboard AS
SELECT 
    s.section_id,
    c.code AS course_code,
    c.name AS course_name,
    s.section_label,
    s.semester,
    s.year,
    COUNT(e.enrollment_id) AS enrolled_students,
    s.teacher_id
FROM sections s
JOIN courses c ON c.course_id = s.course_id
LEFT JOIN enrollments e ON e.section_id = s.section_id AND e.status = 'active'
GROUP BY s.section_id;

CREATE VIEW vw_admin_student_list AS
SELECT 
    st.student_id,
    st.name,
    st.roll_no,
    st.batch,
    st.semester,
    p.name AS program,
    d.name AS department,
    u.email,
    u.photo,
    st.phone,
    st.status AS student_status,
    (SELECT status FROM fee_records WHERE student_id = st.student_id ORDER BY year DESC, 
        CASE semester WHEN 'Fall' THEN 3 WHEN 'Spring' THEN 2 ELSE 1 END DESC LIMIT 1
    ) AS fee_status
FROM students st
JOIN programs p ON p.program_id = st.program_id
JOIN departments d ON d.dept_id = p.dept_id
JOIN users u ON u.user_id = st.user_id;

-- ═══════════════════════════════════════════════════════════════
-- 6. FUNCTIONS
-- ═══════════════════════════════════════════════════════════════

DELIMITER //

CREATE FUNCTION fn_attendance_pct(p_enrollment_id INT) 
RETURNS DECIMAL(5,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_total INT;
    DECLARE v_present INT;
    DECLARE v_pct DECIMAL(5,2);

    SELECT COUNT(*) INTO v_total FROM attendance WHERE enrollment_id = p_enrollment_id;

    IF v_total = 0 THEN
        RETURN 0.00;
    END IF;

    SELECT COUNT(*) INTO v_present 
    FROM attendance 
    WHERE enrollment_id = p_enrollment_id AND status IN ('present', 'late');

    SET v_pct = ROUND((v_present / v_total) * 100, 2);
    RETURN v_pct;
END //

CREATE FUNCTION fn_letter_grade(p_total DECIMAL(5,2))
RETURNS VARCHAR(2)
DETERMINISTIC
BEGIN
    IF p_total >= 90 THEN RETURN 'A+';
    ELSEIF p_total >= 85 THEN RETURN 'A';
    ELSEIF p_total >= 80 THEN RETURN 'A-';
    ELSEIF p_total >= 75 THEN RETURN 'B+';
    ELSEIF p_total >= 70 THEN RETURN 'B';
    ELSEIF p_total >= 65 THEN RETURN 'B-';
    ELSEIF p_total >= 60 THEN RETURN 'C+';
    ELSEIF p_total >= 55 THEN RETURN 'C';
    ELSEIF p_total >= 50 THEN RETURN 'D';
    ELSE RETURN 'F';
    END IF;
END //

CREATE FUNCTION fn_grade_points(p_total DECIMAL(5,2))
RETURNS DECIMAL(3,2)
DETERMINISTIC
BEGIN
    IF p_total >= 90 THEN RETURN 4.00;
    ELSEIF p_total >= 85 THEN RETURN 4.00;
    ELSEIF p_total >= 80 THEN RETURN 3.70;
    ELSEIF p_total >= 75 THEN RETURN 3.30;
    ELSEIF p_total >= 70 THEN RETURN 3.00;
    ELSEIF p_total >= 65 THEN RETURN 2.70;
    ELSEIF p_total >= 60 THEN RETURN 2.30;
    ELSEIF p_total >= 55 THEN RETURN 2.00;
    ELSEIF p_total >= 50 THEN RETURN 1.00;
    ELSE RETURN 0.00;
    END IF;
END //

CREATE FUNCTION fn_calculate_cgpa(p_student_id INT)
RETURNS DECIMAL(4,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_cgpa DECIMAL(4,2);

    SELECT COALESCE(
        SUM(fn_grade_points(g.total) * c.credit_hours) / SUM(c.credit_hours),
        0.00
    ) INTO v_cgpa
    FROM enrollments e
    JOIN grades g ON g.enrollment_id = e.enrollment_id
    JOIN sections s ON s.section_id = e.section_id
    JOIN courses c ON c.course_id = s.course_id
    WHERE e.student_id = p_student_id AND g.total IS NOT NULL;

    RETURN v_cgpa;
END //

-- ═══════════════════════════════════════════════════════════════
-- 7. STORED PROCEDURES
-- ═══════════════════════════════════════════════════════════════

CREATE PROCEDURE sp_add_student(
    IN p_email VARCHAR(120),
    IN p_password VARCHAR(255),
    IN p_name VARCHAR(100),
    IN p_roll_no VARCHAR(20),
    IN p_program_id INT,
    IN p_batch VARCHAR(10),
    IN p_semester INT
)
BEGIN
    DECLARE v_user_id INT;

    INSERT INTO users (email, password_hash, role) 
    VALUES (p_email, p_password, 'student');

    SET v_user_id = LAST_INSERT_ID();

    INSERT INTO students (user_id, name, roll_no, program_id, batch, semester)
    VALUES (v_user_id, p_name, p_roll_no, p_program_id, p_batch, p_semester);

    -- Welcome notification
    INSERT INTO notifications (user_id, type, title, message)
    VALUES (v_user_id, 'success', 'Welcome!', 'Your student account has been created successfully.');
END //

CREATE PROCEDURE sp_add_teacher(
    IN p_email VARCHAR(120),
    IN p_password VARCHAR(255),
    IN p_name VARCHAR(100),
    IN p_dept_id INT,
    IN p_designation VARCHAR(50)
)
BEGIN
    DECLARE v_user_id INT;

    INSERT INTO users (email, password_hash, role) 
    VALUES (p_email, p_password, 'teacher');

    SET v_user_id = LAST_INSERT_ID();

    INSERT INTO teachers (user_id, name, dept_id, designation)
    VALUES (v_user_id, p_name, p_dept_id, p_designation);

    INSERT INTO notifications (user_id, type, title, message)
    VALUES (v_user_id, 'success', 'Welcome!', 'Your teacher account has been created successfully.');
END //

DELIMITER ;

-- ═══════════════════════════════════════════════════════════════
-- 8. INDEXES FOR PERFORMANCE
-- ═══════════════════════════════════════════════════════════════

CREATE INDEX idx_students_roll ON students(roll_no);
CREATE INDEX idx_students_user ON students(user_id);
CREATE INDEX idx_teachers_user ON teachers(user_id);
CREATE INDEX idx_enrollments_student ON enrollments(student_id);
CREATE INDEX idx_enrollments_section ON enrollments(section_id);
CREATE INDEX idx_attendance_enrollment ON attendance(enrollment_id);
CREATE INDEX idx_attendance_date ON attendance(date);
CREATE INDEX idx_fee_student ON fee_records(student_id);
CREATE INDEX idx_notif_user ON notifications(user_id, is_read);
