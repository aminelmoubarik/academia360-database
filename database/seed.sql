USE academia360;

INSERT INTO users (full_name, email, role)
VALUES
('Admin User', 'admin@academia360.pt', 'admin'),
('Director User', 'director@academia360.pt', 'director'),
('Secretary User', 'secretary@academia360.pt', 'secretary'),
('Professor Afonso', 'afonso@academia360.pt', 'professor'),
('Professor Joana', 'joana@academia360.pt', 'professor');

INSERT INTO classes (name, school_year, course_name)
VALUES
('Class A', '2025/2026', 'Computer Systems'),
('Class B', '2025/2026', 'Multimedia');

INSERT INTO students (full_name, student_number, card_uid, class_id)
VALUES
('Miguel Santos', 'STU001', 'CARD001', 1),
('Inês Ferreira', 'STU002', 'CARD002', 1),
('Tiago Costa', 'STU003', 'CARD003', 2);

INSERT INTO professors (user_id, full_name, email)
VALUES
(4, 'Professor Afonso', 'afonso@academia360.pt'),
(5, 'Professor Joana', 'joana@academia360.pt');

INSERT INTO disciplines (name, total_hours, lesson_duration_minutes, is_practical)
VALUES
('Databases', 80, 60, TRUE),
('Programming', 120, 90, TRUE),
('Mathematics', 60, 60, FALSE);

INSERT INTO professor_disciplines (professor_id, discipline_id)
VALUES
(1, 1),
(1, 2),
(2, 3);

INSERT INTO rooms (name, capacity, is_practice_room, location)
VALUES
('Room 101', 25, FALSE, 'Main Building'),
('Computer Lab 1', 20, TRUE, 'IT Building'),
('Computer Lab 2', 20, TRUE, 'IT Building');

INSERT INTO teacher_availability (professor_id, day_of_week, start_time, end_time)
VALUES
(1, 'monday', '14:00:00', '16:00:00'),
(1, 'tuesday', '14:00:00', '16:00:00'),
(2, 'monday', '09:00:00', '17:00:00'),
(2, 'tuesday', '09:00:00', '17:00:00');

INSERT INTO school_calendar (calendar_date, is_school_day, description)
VALUES
('2026-05-11', TRUE, 'School day'),
('2026-05-12', TRUE, 'School day'),
('2026-05-13', TRUE, 'School day'),
('2026-06-10', FALSE, 'Holiday');

INSERT INTO generated_schedule 
(class_id, discipline_id, professor_id, room_id, schedule_date, start_time, end_time, status)
VALUES
(1, 1, 1, 2, '2026-05-11', '14:00:00', '15:00:00', 'draft'),
(1, 3, 2, 1, '2026-05-12', '10:00:00', '11:00:00', 'draft');

INSERT INTO attendance_records 
(student_id, schedule_id, punch_type, punch_method)
VALUES
(1, 1, 'in', 'nfc'),
(2, 1, 'in', 'qr');