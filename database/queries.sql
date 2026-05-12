USE academia360;

SELECT * FROM students;

SELECT * FROM professors;

SELECT * FROM disciplines;

SELECT * FROM rooms;

SELECT 
    students.full_name AS student,
    classes.name AS class,
    classes.course_name
FROM students
JOIN classes ON students.class_id = classes.id;

SELECT 
    professors.full_name AS professor,
    disciplines.name AS discipline
FROM professor_disciplines
JOIN professors ON professor_disciplines.professor_id = professors.id
JOIN disciplines ON professor_disciplines.discipline_id = disciplines.id;

SELECT 
    professors.full_name AS professor,
    teacher_availability.day_of_week,
    teacher_availability.start_time,
    teacher_availability.end_time
FROM teacher_availability
JOIN professors ON teacher_availability.professor_id = professors.id;

SELECT 
    generated_schedule.schedule_date,
    generated_schedule.start_time,
    generated_schedule.end_time,
    classes.name AS class,
    disciplines.name AS discipline,
    professors.full_name AS professor,
    rooms.name AS room
FROM generated_schedule
JOIN classes ON generated_schedule.class_id = classes.id
JOIN disciplines ON generated_schedule.discipline_id = disciplines.id
JOIN professors ON generated_schedule.professor_id = professors.id
JOIN rooms ON generated_schedule.room_id = rooms.id;

SELECT 
    attendance_records.punch_time,
    students.full_name AS student,
    disciplines.name AS discipline,
    attendance_records.punch_type,
    attendance_records.punch_method
FROM attendance_records
JOIN students ON attendance_records.student_id = students.id
LEFT JOIN generated_schedule ON attendance_records.schedule_id = generated_schedule.id
LEFT JOIN disciplines ON generated_schedule.discipline_id = disciplines.id;