USE nfc_portal;

-- ─────────────────────────────────────────
-- 1. DEPARTMENTS
-- ─────────────────────────────────────────
INSERT INTO departments (name, code) VALUES
('Computer Science', 'CS'),
('Electrical Engineering', 'EE'),
('Mechanical Engineering', 'ME'),
('Civil Engineering', 'CE'),
('Business Administration', 'BBA');

-- ─────────────────────────────────────────
-- 2. PROGRAMS
-- ─────────────────────────────────────────
INSERT INTO programs (name, dept_id, duration_years, total_semesters) VALUES
('BS Computer Science', 1, 4, 8),
('BS Software Engineering', 1, 4, 8),
('BS Data Science', 1, 4, 8),
('BS Electrical Engineering', 2, 4, 8),
('BS Mechanical Engineering', 3, 4, 8),
('BS Civil Engineering', 4, 4, 8),
('BBA (Hons)', 5, 4, 8);

-- ─────────────────────────────────────────
-- 3. COURSES
-- ─────────────────────────────────────────
INSERT INTO courses (code, name, dept_id, credit_hours, total_marks, mid_weight, final_weight, assign_weight) VALUES
('CC-221', 'Operating Systems', 1, 3, 100, 30, 50, 20),
('CC-222', 'Database Systems', 1, 3, 100, 30, 50, 20),
('CS-221', 'Theory of Automata', 1, 3, 100, 30, 50, 20),
('MT-221', 'Linear Algebra', 1, 3, 100, 30, 50, 20),
('MS-201', 'Entrepreneurship', 1, 2, 100, 30, 50, 20),
('HM-201', 'Civics & Community Engagement', 1, 2, 100, 30, 50, 20),
('CC-LAB1', 'Operating Systems Lab', 1, 1, 100, 0, 50, 50),
('CC-LAB2', 'Database Systems Lab', 1, 1, 100, 0, 50, 50),
('EE-101', 'Circuit Analysis I', 2, 3, 100, 30, 50, 20),
('EE-102', 'Electronics I', 2, 3, 100, 30, 50, 20),
('EE-201', 'Digital Logic Design', 2, 3, 100, 30, 50, 20),
('ME-101', 'Engineering Mechanics', 3, 3, 100, 30, 50, 20),
('ME-102', 'Thermodynamics', 3, 3, 100, 30, 50, 20),
('ENG-101', 'English Composition', 1, 3, 100, 30, 50, 20),
('MATH-101', 'Calculus I', 1, 3, 100, 30, 50, 20),
('BBA-101', 'Principles of Management', 5, 3, 100, 30, 50, 20),
('BBA-102', 'Business Communication', 5, 3, 100, 30, 50, 20);

-- ─────────────────────────────────────────
-- 4. USERS
-- ─────────────────────────────────────────
INSERT INTO users (email, password_hash, role) VALUES
('admin@nfc.edu',          'admin123',    'admin'),
('zara.azhar@nfc.edu',     'faculty',     'teacher'),
('fatima.khan@nfc.edu',    'faculty',     'teacher'),
('usman.malik@nfc.edu',    'faculty',     'teacher'),
('imran.qureshi@nfc.edu',  'faculty',     'teacher'),
('nadia.hassan@nfc.edu',   'faculty',     'teacher'),
('tariq.jamal@nfc.edu',    'faculty',     'teacher'),
('2022cs001@nfc.edu',      'student123',  'student'),
('2022cs002@nfc.edu',      'student123',  'student'),
('2022cs003@nfc.edu',      'student123',  'student'),
('2022cs004@nfc.edu',      'student123',  'student'),
('2022cs005@nfc.edu',      'student123',  'student'),
('2022ee001@nfc.edu',      'student123',  'student'),
('2022me001@nfc.edu',      'student123',  'student'),
('2022bba001@nfc.edu',     'student123',  'student');

-- ─────────────────────────────────────────
-- 5. TEACHERS
-- ─────────────────────────────────────────
INSERT INTO teachers (user_id, name, dept_id, designation, phone, qualification, specialization) VALUES
(2, 'Dr. Zara Azhar',    1, 'Professor',            '0300-1234567', 'PhD CS',          'Machine Learning'),
(3, 'Dr. Fatima Khan',   1, 'Associate Professor',   '0301-2345678', 'PhD SE',          'Software Architecture'),
(4, 'Usman Malik',       2, 'Assistant Professor',   '0302-3456789', 'MS EE',           'Power Electronics'),
(5, 'Iman Qureshi',     1, 'Lecturer',              '0304-5678901', 'MS CS',           'Web Development'),
(6, 'Dr. Nadia Hassan',  1, 'Professor',             '0305-6789012', 'PhD Mathematics', 'Applied Mathematics'),
(7, 'Tariq Jamal',       5, 'Assistant Professor',   '0306-7890123', 'MBA',             'Finance');

-- ─────────────────────────────────────────
-- 6. STUDENTS
-- ─────────────────────────────────────────
INSERT INTO students (user_id, name, roll_no, program_id, batch, semester, phone, gender, status) VALUES
(8,  'Ahmed Hassan',    '2022-CS-001', 1, '2022', 6, '0311-1111111', 'male',   'active'),
(9,  'Bilal Khan',      '2022-CS-002', 1, '2022', 6, '0312-2222222', 'male',   'active'),
(10, 'Ayesha Siddiqui', '2022-CS-003', 2, '2022', 6, '0313-3333333', 'female', 'active'),
(11, 'Zara Malik',      '2022-CS-004', 1, '2022', 6, '0314-4444444', 'female', 'active'),
(12, 'Usman Ghani',     '2022-CS-005', 3, '2022', 6, '0315-5555555', 'male',   'active'),
(13, 'Hamza Tariq',     '2022-EE-001', 4, '2022', 6, '0316-6666666', 'male',   'active'),
(14, 'Rashid Amin',     '2022-ME-001', 5, '2022', 6, '0318-8888888', 'male',   'active'),
(15, 'Fatima Zahra',    '2022-BBA-001',7, '2022', 6, '0319-9999999', 'female', 'active');

-- ─────────────────────────────────────────
-- 7. SECTIONS
-- ─────────────────────────────────────────
INSERT INTO sections (course_id, teacher_id, section_label, semester, year, room) VALUES
(1,  1, 'A', 'Spring', 2025, 'Lab-101'),
(2,  2, 'A', 'Spring', 2025, 'Lab-102'),
(3,  1, 'A', 'Spring', 2025, 'Room-201'),
(4,  5, 'A', 'Spring', 2025, 'Room-202'),
(5,  1, 'A', 'Spring', 2025, 'Room-203'),
(6,  4, 'A', 'Spring', 2025, 'Lab-103'),
(14, 5, 'A', 'Spring', 2025, 'Room-301'),
(15, 5, 'A', 'Spring', 2025, 'Room-302'),
(9,  3, 'A', 'Spring', 2025, 'Lab-201'),
(10, 3, 'A', 'Spring', 2025, 'Lab-202'),
(12, 3, 'A', 'Spring', 2025, 'Workshop-A'),
(13, 3, 'A', 'Spring', 2025, 'Workshop-B'),
(16, 6, 'A', 'Spring', 2025, 'Room-501'),
(17, 6, 'A', 'Spring', 2025, 'Room-502');

-- ─────────────────────────────────────────
-- 8. ENROLLMENTS
-- ─────────────────────────────────────────
-- Ahmed Hassan (CS-001) in CS sections
INSERT INTO enrollments (student_id, section_id) VALUES
(1,1),(1,2),(1,3),(1,4),(1,5),(1,6),(1,7),(1,8);

-- Bilal Khan (CS-002)
INSERT INTO enrollments (student_id, section_id) VALUES
(2,1),(2,2),(2,3),(2,4),(2,5),(2,6),(2,7),(2,8);

-- Ayesha Siddiqui (CS-003)
INSERT INTO enrollments (student_id, section_id) VALUES
(3,1),(3,2),(3,3),(3,4),(3,5),(3,6),(3,7),(3,8);

-- Zara Malik (CS-004)
INSERT INTO enrollments (student_id, section_id) VALUES
(4,1),(4,2),(4,3),(4,4),(4,5),(4,6),(4,7),(4,8);

-- Usman Ghani (CS-005)
INSERT INTO enrollments (student_id, section_id) VALUES
(5,1),(5,2),(5,3),(5,4),(5,5),(5,6),(5,7),(5,8);

-- Hamza Tariq (EE-001)
INSERT INTO enrollments (student_id, section_id) VALUES
(6,9),(6,10),(6,7),(6,8);

-- Rashid Amin (ME-001)
INSERT INTO enrollments (student_id, section_id) VALUES
(7,11),(7,12),(7,7),(7,8);

-- Fatima Zahra (BBA-001)
INSERT INTO enrollments (student_id, section_id) VALUES
(8,13),(8,14),(8,7),(8,8);

-- ─────────────────────────────────────────
-- 9. GRADES
-- ─────────────────────────────────────────
INSERT INTO grades (enrollment_id, mid_marks, final_marks, assignment_marks) VALUES
(1, 25.5, 42.0, 18.0),
(2, 24.0, 40.5, 17.5),
(3, 26.0, 43.0, 18.5),
(4, 23.5, 38.0, 16.0),
(5, 27.0, 44.0, 19.0),
(6, 22.0, 36.5, 15.5),
(7, 28.0, 45.0, 19.5),
(8, 25.0, 41.0, 17.0),
(9, 20.0, 35.0, 15.0),
(10, 22.5, 37.5, 16.5),
(11, 24.0, 39.0, 17.0),
(12, 21.0, 34.0, 14.5),
(13, 23.5, 38.5, 16.0),
(14, 20.5, 33.0, 14.0),
(15, 26.0, 42.0, 18.0),
(16, 24.5, 40.0, 17.0);

-- ─────────────────────────────────────────
-- 10. ATTENDANCE
-- ─────────────────────────────────────────
INSERT INTO attendance (enrollment_id, date, status) VALUES
(1, '2025-04-01', 'present'),
(1, '2025-04-03', 'present'),
(1, '2025-04-05', 'present'),
(1, '2025-04-08', 'late'),
(1, '2025-04-10', 'present'),
(1, '2025-04-12', 'present'),
(1, '2025-04-15', 'absent'),
(1, '2025-04-17', 'present'),
(1, '2025-04-19', 'present'),
(1, '2025-04-22', 'present'),
(1, '2025-04-24', 'present'),
(1, '2025-04-26', 'late'),
(1, '2025-04-29', 'present'),
(2, '2025-04-01', 'present'),
(2, '2025-04-03', 'absent'),
(2, '2025-04-05', 'present'),
(2, '2025-04-08', 'present'),
(2, '2025-04-10', 'absent'),
(2, '2025-04-12', 'present'),
(2, '2025-04-15', 'present'),
(2, '2025-04-17', 'late'),
(2, '2025-04-19', 'present'),
(2, '2025-04-22', 'absent');

-- ─────────────────────────────────────────
-- 11. TIMETABLE
-- ─────────────────────────────────────────
INSERT INTO timetable (section_id, day, start_time, end_time, room) VALUES
(1, 'Monday',    '09:00:00', '11:00:00', 'Lab-101'),
(1, 'Wednesday', '09:00:00', '11:00:00', 'Lab-101'),
(1, 'Friday',    '11:00:00', '13:00:00', 'Lab-101'),
(2, 'Monday',    '11:00:00', '13:00:00', 'Lab-102'),
(2, 'Wednesday', '11:00:00', '13:00:00', 'Lab-102'),
(3, 'Tuesday',   '09:00:00', '11:00:00', 'Room-201'),
(3, 'Thursday',  '09:00:00', '11:00:00', 'Room-201'),
(4, 'Tuesday',   '11:00:00', '13:00:00', 'Lab-103'),
(4, 'Thursday',  '11:00:00', '13:00:00', 'Lab-103'),
(7, 'Monday',    '14:00:00', '16:00:00', 'Room-301'),
(7, 'Wednesday', '14:00:00', '16:00:00', 'Room-301'),
(8, 'Tuesday',   '14:00:00', '16:00:00', 'Room-302'),
(8, 'Thursday',  '14:00:00', '16:00:00', 'Room-302');

-- ─────────────────────────────────────────
-- 12. FEE RECORDS
-- ─────────────────────────────────────────
INSERT INTO fee_records (student_id, semester, year, amount, due_date, status, paid_at) VALUES
(1, 'Fall',   2024, 85000, '2024-09-15', 'paid',    '2024-09-10'),
(1, 'Spring', 2025, 85000, '2025-02-15', 'paid',    '2025-02-08'),
(2, 'Fall',   2024, 85000, '2024-09-15', 'paid',    '2024-09-12'),
(2, 'Spring', 2025, 85000, '2025-02-15', 'overdue', NULL),
(3, 'Fall',   2024, 85000, '2024-09-15', 'paid',    '2024-09-08'),
(3, 'Spring', 2025, 85000, '2025-02-15', 'paid',    '2025-02-05'),
(4, 'Spring', 2025, 85000, '2025-02-15', 'pending', NULL),
(5, 'Spring', 2025, 95000, '2025-02-15', 'paid',    '2025-02-10'),
(6, 'Spring', 2025, 85000, '2025-02-15', 'pending', NULL),
(7, 'Spring', 2025, 85000, '2025-02-15', 'paid',    '2025-02-12'),
(8, 'Spring', 2025, 75000, '2025-02-15', 'paid',    '2025-02-03');

-- ─────────────────────────────────────────
-- 13. ANNOUNCEMENTS
-- ─────────────────────────────────────────
INSERT INTO announcements (teacher_id, section_id, title, body) VALUES
(1, 1, 'Mid-Term Exam Schedule', 'Mid-term exams will be held from May 15-20, 2025. Please prepare accordingly.'),
(1, 1, 'Assignment 3 Deadline Extended', 'The deadline for Assignment 3 has been extended to May 10, 2025.'),
(2, 2, 'Lab Report Guidelines', 'All lab reports must follow the IEEE format. Templates are available on the portal.'),
(4, 4, 'Project Groups Formation', 'Please form groups of 3-4 students for the final project by May 5, 2025.'),
(5, 7, 'Quiz on April 30', 'There will be a quiz on Linear Transformations on April 30. Be prepared!');

-- ─────────────────────────────────────────
-- 14. NOTIFICATIONS
-- ─────────────────────────────────────────
INSERT INTO notifications (user_id, type, title, message) VALUES
(8,  'info',    'Welcome to Spring 2025', 'Your classes for Spring 2025 have started. Check your timetable.'),
(8,  'success', 'Fee Paid',               'Your fee payment of Rs. 85,000 has been received.'),
(9,  'info',    'Welcome to Spring 2025', 'Your classes for Spring 2025 have started. Check your timetable.'),
(9,  'error',   'Fee Overdue',            'Your Spring 2025 fee is overdue. Please pay immediately.'),
(10, 'info',    'Welcome to Spring 2025', 'Your classes for Spring 2025 have started. Check your timetable.'),
(10, 'success', 'Fee Paid',               'Your fee payment of Rs. 85,000 has been received.');