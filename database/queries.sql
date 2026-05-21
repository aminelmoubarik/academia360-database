USE academia360;

SELECT 'Academia360 database is working' AS status;

SELECT DATABASE() AS current_database;

SELECT 
    TABLE_NAME
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'academia360'
ORDER BY TABLE_NAME;

SELECT 'Tref_UserRoles' AS table_name, COUNT(*) AS total_records FROM Tref_UserRoles
UNION ALL
SELECT 'Tref_Gender', COUNT(*) FROM Tref_Gender
UNION ALL
SELECT 'Tref_SchoolYears', COUNT(*) FROM Tref_SchoolYears
UNION ALL
SELECT 'Tbl_Users', COUNT(*) FROM Tbl_Users
UNION ALL
SELECT 'Tbl_Courses', COUNT(*) FROM Tbl_Courses
UNION ALL
SELECT 'Tbl_Classes', COUNT(*) FROM Tbl_Classes
UNION ALL
SELECT 'Tbl_Students', COUNT(*) FROM Tbl_Students
UNION ALL
SELECT 'Tbl_Professors', COUNT(*) FROM Tbl_Professors
UNION ALL
SELECT 'Tbl_Disciplines', COUNT(*) FROM Tbl_Disciplines
UNION ALL
SELECT 'trx_Discipline_CourseYear', COUNT(*) FROM trx_Discipline_CourseYear
UNION ALL
SELECT 'trx_Professor_DisciplineCourseYear', COUNT(*) FROM trx_Professor_DisciplineCourseYear
UNION ALL
SELECT 'Tbl_Rooms', COUNT(*) FROM Tbl_Rooms
UNION ALL
SELECT 'Tbl_SchoolCalendar', COUNT(*) FROM Tbl_SchoolCalendar
UNION ALL
SELECT 'Tbl_TeacherAvailability', COUNT(*) FROM Tbl_TeacherAvailability
UNION ALL
SELECT 'Tbl_GeneratedSchedule', COUNT(*) FROM Tbl_GeneratedSchedule
UNION ALL
SELECT 'Tbl_AttendanceRecords', COUNT(*) FROM Tbl_AttendanceRecords;

SELECT
    RoleID AS id,
    Name AS name,
    InsertUsername AS insert_username,
    InsertDate AS insert_date,
    ChangeUsername AS change_username,
    ChangeDate AS change_date
FROM Tref_UserRoles
ORDER BY RoleID;

SELECT
    GenderID AS id,
    Name AS name,
    InsertUsername AS insert_username,
    InsertDate AS insert_date,
    ChangeUsername AS change_username,
    ChangeDate AS change_date
FROM Tref_Gender
ORDER BY GenderID;

SELECT
    SchoolYearID AS id,
    Name AS name,
    StartDate AS start_date,
    EndDate AS end_date,
    InsertUsername AS insert_username,
    InsertDate AS insert_date,
    ChangeUsername AS change_username,
    ChangeDate AS change_date
FROM Tref_SchoolYears
ORDER BY StartDate;

SELECT
    u.UserID AS id,
    u.FullName AS full_name,
    u.Email AS email,
    r.Name AS role,
    CASE 
        WHEN u.PasswordHash IS NULL THEN 'NO PASSWORD'
        ELSE 'PASSWORD SET'
    END AS password_status,
    u.InsertUsername AS insert_username,
    u.InsertDate AS insert_date,
    u.ChangeUsername AS change_username,
    u.ChangeDate AS change_date
FROM Tbl_Users u
JOIN Tref_UserRoles r ON u.RoleID = r.RoleID
ORDER BY u.UserID;

SELECT
    CourseID AS id,
    Code AS code,
    Name AS name,
    InsertUsername AS insert_username,
    InsertDate AS insert_date,
    ChangeUsername AS change_username,
    ChangeDate AS change_date
FROM Tbl_Courses
ORDER BY CourseID;

SELECT
    cl.ClassID AS id,
    cl.Name AS class_name,
    cl.CourseID AS course_id,
    c.Code AS course_code,
    c.Name AS course_name,
    cl.SchoolYearID AS school_year_id,
    sy.Name AS school_year,
    cl.CourseYearNumber AS course_year_number,
    cl.InsertUsername AS insert_username,
    cl.InsertDate AS insert_date,
    cl.ChangeUsername AS change_username,
    cl.ChangeDate AS change_date
FROM Tbl_Classes cl
JOIN Tbl_Courses c ON cl.CourseID = c.CourseID
JOIN Tref_SchoolYears sy ON cl.SchoolYearID = sy.SchoolYearID
ORDER BY cl.ClassID;

SELECT
    s.StudentID AS id,
    s.FullName AS full_name,
    s.StudentNumber AS student_number,
    s.CardUID AS card_uid,
    s.ClassID AS class_id,
    cl.Name AS class_name,
    c.CourseID AS course_id,
    c.Code AS course_code,
    c.Name AS course_name,
    sy.SchoolYearID AS school_year_id,
    sy.Name AS school_year,
    s.PhotoPath AS photo_path,
    s.GenderID AS gender_id,
    g.Name AS gender,
    s.Address AS address,
    s.PostalCode AS postal_code,
    s.City AS city,
    s.Contact AS contact,
    s.DateOfBirth AS date_of_birth,
    s.InsertUsername AS insert_username,
    s.InsertDate AS insert_date,
    s.ChangeUsername AS change_username,
    s.ChangeDate AS change_date
FROM Tbl_Students s
LEFT JOIN Tbl_Classes cl ON s.ClassID = cl.ClassID
LEFT JOIN Tbl_Courses c ON cl.CourseID = c.CourseID
LEFT JOIN Tref_SchoolYears sy ON cl.SchoolYearID = sy.SchoolYearID
LEFT JOIN Tref_Gender g ON s.GenderID = g.GenderID
ORDER BY s.StudentID;

SELECT
    cl.ClassID AS class_id,
    cl.Name AS class_name,
    c.Code AS course_code,
    sy.Name AS school_year,
    cl.CourseYearNumber AS course_year_number,
    s.StudentID AS student_id,
    s.FullName AS student_name,
    s.StudentNumber AS student_number,
    s.CardUID AS card_uid
FROM Tbl_Students s
JOIN Tbl_Classes cl ON s.ClassID = cl.ClassID
JOIN Tbl_Courses c ON cl.CourseID = c.CourseID
JOIN Tref_SchoolYears sy ON cl.SchoolYearID = sy.SchoolYearID
ORDER BY cl.Name, s.FullName;

SELECT
    cl.ClassID AS class_id,
    cl.Name AS class_name,
    c.Code AS course_code,
    sy.Name AS school_year,
    COUNT(s.StudentID) AS total_students
FROM Tbl_Classes cl
JOIN Tbl_Courses c ON cl.CourseID = c.CourseID
JOIN Tref_SchoolYears sy ON cl.SchoolYearID = sy.SchoolYearID
LEFT JOIN Tbl_Students s ON cl.ClassID = s.ClassID
GROUP BY
    cl.ClassID,
    cl.Name,
    c.Code,
    sy.Name
ORDER BY cl.ClassID;

SELECT
    p.ProfessorID AS id,
    p.UserID AS user_id,
    u.FullName AS full_name,
    u.Email AS email,
    r.Name AS role,
    p.PhotoPath AS photo_path,
    p.GenderID AS gender_id,
    g.Name AS gender,
    p.Address AS address,
    p.PostalCode AS postal_code,
    p.City AS city,
    p.Contact AS contact,
    p.DateOfBirth AS date_of_birth,
    p.InsertUsername AS insert_username,
    p.InsertDate AS insert_date,
    p.ChangeUsername AS change_username,
    p.ChangeDate AS change_date
FROM Tbl_Professors p
JOIN Tbl_Users u ON p.UserID = u.UserID
JOIN Tref_UserRoles r ON u.RoleID = r.RoleID
LEFT JOIN Tref_Gender g ON p.GenderID = g.GenderID
ORDER BY p.ProfessorID;

SELECT
    RoomID AS id,
    Name AS name,
    Capacity AS capacity,
    IsPracticeRoom AS is_practice_room,
    Location AS location,
    InsertUsername AS insert_username,
    InsertDate AS insert_date,
    ChangeUsername AS change_username,
    ChangeDate AS change_date
FROM Tbl_Rooms
ORDER BY RoomID;

SELECT
    DisciplineID AS id,
    Name AS name,
    Code AS code,
    InsertUsername AS insert_username,
    InsertDate AS insert_date,
    ChangeUsername AS change_username,
    ChangeDate AS change_date
FROM Tbl_Disciplines
ORDER BY DisciplineID;

SELECT
    dc.DisciplineCourseYearID AS id,
    dc.DisciplineID AS discipline_id,
    d.Name AS discipline_name,
    d.Code AS discipline_code,
    dc.CourseID AS course_id,
    c.Code AS course_code,
    c.Name AS course_name,
    dc.SchoolYearID AS school_year_id,
    sy.Name AS school_year,
    dc.CourseYearNumber AS course_year_number,
    dc.TotalMinutes AS total_minutes,
    ROUND(dc.TotalMinutes / 60, 2) AS total_hours,
    dc.LessonDurationMinutes AS lesson_duration_minutes,
    dc.IsPractical AS is_practical,
    dc.InsertUsername AS insert_username,
    dc.InsertDate AS insert_date,
    dc.ChangeUsername AS change_username,
    dc.ChangeDate AS change_date
FROM trx_Discipline_CourseYear dc
JOIN Tbl_Disciplines d ON dc.DisciplineID = d.DisciplineID
JOIN Tbl_Courses c ON dc.CourseID = c.CourseID
JOIN Tref_SchoolYears sy ON dc.SchoolYearID = sy.SchoolYearID
ORDER BY dc.DisciplineCourseYearID;

SELECT
    pd.ProfessorID AS professor_id,
    u.FullName AS professor_name,
    u.Email AS professor_email,
    pd.DisciplineCourseYearID AS discipline_course_year_id,
    d.DisciplineID AS discipline_id,
    d.Name AS discipline_name,
    d.Code AS discipline_code,
    c.CourseID AS course_id,
    c.Code AS course_code,
    c.Name AS course_name,
    sy.SchoolYearID AS school_year_id,
    sy.Name AS school_year,
    dc.CourseYearNumber AS course_year_number,
    dc.TotalMinutes AS total_minutes,
    ROUND(dc.TotalMinutes / 60, 2) AS total_hours,
    dc.LessonDurationMinutes AS lesson_duration_minutes,
    dc.IsPractical AS is_practical,
    pd.InsertUsername AS insert_username,
    pd.InsertDate AS insert_date,
    pd.ChangeUsername AS change_username,
    pd.ChangeDate AS change_date
FROM trx_Professor_DisciplineCourseYear pd
JOIN Tbl_Professors p ON pd.ProfessorID = p.ProfessorID
JOIN Tbl_Users u ON p.UserID = u.UserID
JOIN trx_Discipline_CourseYear dc ON pd.DisciplineCourseYearID = dc.DisciplineCourseYearID
JOIN Tbl_Disciplines d ON dc.DisciplineID = d.DisciplineID
JOIN Tbl_Courses c ON dc.CourseID = c.CourseID
JOIN Tref_SchoolYears sy ON dc.SchoolYearID = sy.SchoolYearID
ORDER BY pd.ProfessorID, pd.DisciplineCourseYearID;

SELECT
    p.ProfessorID AS professor_id,
    u.FullName AS professor_name,
    u.Email AS professor_email,
    GROUP_CONCAT(
        DISTINCT CONCAT(d.Name, ' - ', c.Code, ' - ', sy.Name, ' - Year ', dc.CourseYearNumber)
        ORDER BY d.Name
        SEPARATOR ', '
    ) AS assigned_disciplines
FROM Tbl_Professors p
JOIN Tbl_Users u ON p.UserID = u.UserID
LEFT JOIN trx_Professor_DisciplineCourseYear pd ON p.ProfessorID = pd.ProfessorID
LEFT JOIN trx_Discipline_CourseYear dc ON pd.DisciplineCourseYearID = dc.DisciplineCourseYearID
LEFT JOIN Tbl_Disciplines d ON dc.DisciplineID = d.DisciplineID
LEFT JOIN Tbl_Courses c ON dc.CourseID = c.CourseID
LEFT JOIN Tref_SchoolYears sy ON dc.SchoolYearID = sy.SchoolYearID
GROUP BY
    p.ProfessorID,
    u.FullName,
    u.Email
ORDER BY p.ProfessorID;

SELECT
    sc.CalendarID AS id,
    sc.SchoolYearID AS school_year_id,
    sy.Name AS school_year,
    sc.CalendarDate AS calendar_date,
    DAYNAME(sc.CalendarDate) AS day_name,
    sc.IsSchoolDay AS is_school_day,
    sc.Description AS description,
    sc.InsertUsername AS insert_username,
    sc.InsertDate AS insert_date,
    sc.ChangeUsername AS change_username,
    sc.ChangeDate AS change_date
FROM Tbl_SchoolCalendar sc
JOIN Tref_SchoolYears sy ON sc.SchoolYearID = sy.SchoolYearID
ORDER BY sc.CalendarDate;

SELECT
    sc.CalendarID AS id,
    sy.Name AS school_year,
    sc.CalendarDate AS calendar_date,
    DAYNAME(sc.CalendarDate) AS day_name,
    sc.Description AS description
FROM Tbl_SchoolCalendar sc
JOIN Tref_SchoolYears sy ON sc.SchoolYearID = sy.SchoolYearID
WHERE sc.IsSchoolDay = FALSE
ORDER BY sc.CalendarDate;

SELECT
    ta.TeacherAvailabilityID AS id,
    ta.ProfessorID AS professor_id,
    u.FullName AS professor_name,
    u.Email AS professor_email,
    ta.SchoolYearID AS school_year_id,
    sy.Name AS school_year,
    ta.DayOfWeek AS day_of_week,
    ta.StartTime AS start_time,
    ta.EndTime AS end_time,
    ta.InsertUsername AS insert_username,
    ta.InsertDate AS insert_date,
    ta.ChangeUsername AS change_username,
    ta.ChangeDate AS change_date
FROM Tbl_TeacherAvailability ta
JOIN Tbl_Professors p ON ta.ProfessorID = p.ProfessorID
JOIN Tbl_Users u ON p.UserID = u.UserID
JOIN Tref_SchoolYears sy ON ta.SchoolYearID = sy.SchoolYearID
ORDER BY ta.ProfessorID, ta.DayOfWeek, ta.StartTime;

SELECT
    gs.ScheduleID AS id,
    gs.ClassID AS class_id,
    cl.Name AS class_name,
    c.CourseID AS course_id,
    c.Code AS course_code,
    c.Name AS course_name,
    sy.SchoolYearID AS school_year_id,
    sy.Name AS school_year,
    gs.DisciplineCourseYearID AS discipline_course_year_id,
    d.DisciplineID AS discipline_id,
    d.Name AS discipline_name,
    d.Code AS discipline_code,
    dc.CourseYearNumber AS course_year_number,
    gs.ProfessorID AS professor_id,
    u.FullName AS professor_name,
    u.Email AS professor_email,
    gs.RoomID AS room_id,
    r.Name AS room_name,
    r.IsPracticeRoom AS is_practice_room,
    gs.CalendarID AS calendar_id,
    sc.CalendarDate AS schedule_date,
    DAYNAME(sc.CalendarDate) AS day_name,
    gs.StartTime AS start_time,
    gs.EndTime AS end_time,
    gs.Status AS status,
    gs.InsertUsername AS insert_username,
    gs.InsertDate AS insert_date,
    gs.ChangeUsername AS change_username,
    gs.ChangeDate AS change_date
FROM Tbl_GeneratedSchedule gs
JOIN Tbl_Classes cl ON gs.ClassID = cl.ClassID
JOIN Tbl_Courses c ON cl.CourseID = c.CourseID
JOIN Tref_SchoolYears sy ON cl.SchoolYearID = sy.SchoolYearID
JOIN trx_Discipline_CourseYear dc ON gs.DisciplineCourseYearID = dc.DisciplineCourseYearID
JOIN Tbl_Disciplines d ON dc.DisciplineID = d.DisciplineID
JOIN Tbl_Professors p ON gs.ProfessorID = p.ProfessorID
JOIN Tbl_Users u ON p.UserID = u.UserID
JOIN Tbl_Rooms r ON gs.RoomID = r.RoomID
JOIN Tbl_SchoolCalendar sc ON gs.CalendarID = sc.CalendarID
ORDER BY sc.CalendarDate, gs.StartTime;

SELECT
    cl.ClassID AS class_id,
    cl.Name AS class_name,
    sc.CalendarDate AS schedule_date,
    gs.StartTime AS start_time,
    gs.EndTime AS end_time,
    d.Name AS discipline_name,
    u.FullName AS professor_name,
    r.Name AS room_name,
    gs.Status AS status
FROM Tbl_GeneratedSchedule gs
JOIN Tbl_Classes cl ON gs.ClassID = cl.ClassID
JOIN trx_Discipline_CourseYear dc ON gs.DisciplineCourseYearID = dc.DisciplineCourseYearID
JOIN Tbl_Disciplines d ON dc.DisciplineID = d.DisciplineID
JOIN Tbl_Professors p ON gs.ProfessorID = p.ProfessorID
JOIN Tbl_Users u ON p.UserID = u.UserID
JOIN Tbl_Rooms r ON gs.RoomID = r.RoomID
JOIN Tbl_SchoolCalendar sc ON gs.CalendarID = sc.CalendarID
ORDER BY cl.Name, sc.CalendarDate, gs.StartTime;

SELECT
    p.ProfessorID AS professor_id,
    u.FullName AS professor_name,
    sc.CalendarDate AS schedule_date,
    gs.StartTime AS start_time,
    gs.EndTime AS end_time,
    cl.Name AS class_name,
    d.Name AS discipline_name,
    r.Name AS room_name,
    gs.Status AS status
FROM Tbl_GeneratedSchedule gs
JOIN Tbl_Professors p ON gs.ProfessorID = p.ProfessorID
JOIN Tbl_Users u ON p.UserID = u.UserID
JOIN Tbl_Classes cl ON gs.ClassID = cl.ClassID
JOIN trx_Discipline_CourseYear dc ON gs.DisciplineCourseYearID = dc.DisciplineCourseYearID
JOIN Tbl_Disciplines d ON dc.DisciplineID = d.DisciplineID
JOIN Tbl_Rooms r ON gs.RoomID = r.RoomID
JOIN Tbl_SchoolCalendar sc ON gs.CalendarID = sc.CalendarID
ORDER BY u.FullName, sc.CalendarDate, gs.StartTime;

SELECT
    r.RoomID AS room_id,
    r.Name AS room_name,
    r.IsPracticeRoom AS is_practice_room,
    sc.CalendarDate AS schedule_date,
    gs.StartTime AS start_time,
    gs.EndTime AS end_time,
    cl.Name AS class_name,
    d.Name AS discipline_name,
    u.FullName AS professor_name,
    gs.Status AS status
FROM Tbl_GeneratedSchedule gs
JOIN Tbl_Rooms r ON gs.RoomID = r.RoomID
JOIN Tbl_SchoolCalendar sc ON gs.CalendarID = sc.CalendarID
JOIN Tbl_Classes cl ON gs.ClassID = cl.ClassID
JOIN trx_Discipline_CourseYear dc ON gs.DisciplineCourseYearID = dc.DisciplineCourseYearID
JOIN Tbl_Disciplines d ON dc.DisciplineID = d.DisciplineID
JOIN Tbl_Professors p ON gs.ProfessorID = p.ProfessorID
JOIN Tbl_Users u ON p.UserID = u.UserID
ORDER BY r.Name, sc.CalendarDate, gs.StartTime;

SELECT
    ar.AttendanceRecordID AS id,
    ar.StudentID AS student_id,
    s.FullName AS student_name,
    s.StudentNumber AS student_number,
    s.CardUID AS card_uid,
    cl.ClassID AS class_id,
    cl.Name AS class_name,
    c.Code AS course_code,
    sy.Name AS school_year,
    ar.ScheduleID AS schedule_id,
    d.Name AS discipline_name,
    sc.CalendarDate AS schedule_date,
    gs.StartTime AS class_start_time,
    gs.EndTime AS class_end_time,
    ar.PunchType AS punch_type,
    ar.PunchMethod AS punch_method,
    ar.PunchTime AS punch_time,
    ar.IsSynced AS is_synced,
    ar.InsertUsername AS insert_username,
    ar.InsertDate AS insert_date,
    ar.ChangeUsername AS change_username,
    ar.ChangeDate AS change_date
FROM Tbl_AttendanceRecords ar
JOIN Tbl_Students s ON ar.StudentID = s.StudentID
LEFT JOIN Tbl_Classes cl ON s.ClassID = cl.ClassID
LEFT JOIN Tbl_Courses c ON cl.CourseID = c.CourseID
LEFT JOIN Tref_SchoolYears sy ON cl.SchoolYearID = sy.SchoolYearID
LEFT JOIN Tbl_GeneratedSchedule gs ON ar.ScheduleID = gs.ScheduleID
LEFT JOIN Tbl_SchoolCalendar sc ON gs.CalendarID = sc.CalendarID
LEFT JOIN trx_Discipline_CourseYear dc ON gs.DisciplineCourseYearID = dc.DisciplineCourseYearID
LEFT JOIN Tbl_Disciplines d ON dc.DisciplineID = d.DisciplineID
ORDER BY ar.PunchTime DESC;

SELECT
    s.StudentID AS student_id,
    s.FullName AS student_name,
    s.StudentNumber AS student_number,
    ar.AttendanceRecordID AS attendance_id,
    ar.PunchType AS punch_type,
    ar.PunchMethod AS punch_method,
    ar.PunchTime AS punch_time,
    sc.CalendarDate AS schedule_date,
    d.Name AS discipline_name
FROM Tbl_AttendanceRecords ar
JOIN Tbl_Students s ON ar.StudentID = s.StudentID
LEFT JOIN Tbl_GeneratedSchedule gs ON ar.ScheduleID = gs.ScheduleID
LEFT JOIN Tbl_SchoolCalendar sc ON gs.CalendarID = sc.CalendarID
LEFT JOIN trx_Discipline_CourseYear dc ON gs.DisciplineCourseYearID = dc.DisciplineCourseYearID
LEFT JOIN Tbl_Disciplines d ON dc.DisciplineID = d.DisciplineID
ORDER BY s.FullName, ar.PunchTime DESC;

SELECT
    s.StudentID AS student_id,
    s.FullName AS student_name,
    s.StudentNumber AS student_number,
    COUNT(ar.AttendanceRecordID) AS total_punches,
    SUM(CASE WHEN ar.PunchType = 'in' THEN 1 ELSE 0 END) AS total_entries,
    SUM(CASE WHEN ar.PunchType = 'out' THEN 1 ELSE 0 END) AS total_exits
FROM Tbl_Students s
LEFT JOIN Tbl_AttendanceRecords ar ON s.StudentID = ar.StudentID
GROUP BY
    s.StudentID,
    s.FullName,
    s.StudentNumber
ORDER BY s.StudentID;

SELECT
    cl.ClassID AS class_id,
    cl.Name AS class_name,
    c.Code AS course_code,
    COUNT(DISTINCT s.StudentID) AS total_students,
    COUNT(ar.AttendanceRecordID) AS total_punches,
    SUM(CASE WHEN ar.PunchType = 'in' THEN 1 ELSE 0 END) AS total_entries,
    SUM(CASE WHEN ar.PunchType = 'out' THEN 1 ELSE 0 END) AS total_exits
FROM Tbl_Classes cl
JOIN Tbl_Courses c ON cl.CourseID = c.CourseID
LEFT JOIN Tbl_Students s ON cl.ClassID = s.ClassID
LEFT JOIN Tbl_AttendanceRecords ar ON s.StudentID = ar.StudentID
GROUP BY
    cl.ClassID,
    cl.Name,
    c.Code
ORDER BY cl.ClassID;

SELECT
    gs1.ScheduleID AS schedule_1,
    gs2.ScheduleID AS schedule_2,
    gs1.ClassID AS class_id,
    cl.Name AS class_name,
    sc.CalendarDate AS schedule_date,
    gs1.StartTime AS schedule_1_start,
    gs1.EndTime AS schedule_1_end,
    gs2.StartTime AS schedule_2_start,
    gs2.EndTime AS schedule_2_end
FROM Tbl_GeneratedSchedule gs1
JOIN Tbl_GeneratedSchedule gs2
    ON gs1.ClassID = gs2.ClassID
   AND gs1.CalendarID = gs2.CalendarID
   AND gs1.ScheduleID < gs2.ScheduleID
   AND NOT (gs1.EndTime <= gs2.StartTime OR gs1.StartTime >= gs2.EndTime)
JOIN Tbl_Classes cl ON gs1.ClassID = cl.ClassID
JOIN Tbl_SchoolCalendar sc ON gs1.CalendarID = sc.CalendarID
ORDER BY sc.CalendarDate, cl.Name;

SELECT
    gs1.ScheduleID AS schedule_1,
    gs2.ScheduleID AS schedule_2,
    gs1.ProfessorID AS professor_id,
    u.FullName AS professor_name,
    sc.CalendarDate AS schedule_date,
    gs1.StartTime AS schedule_1_start,
    gs1.EndTime AS schedule_1_end,
    gs2.StartTime AS schedule_2_start,
    gs2.EndTime AS schedule_2_end
FROM Tbl_GeneratedSchedule gs1
JOIN Tbl_GeneratedSchedule gs2
    ON gs1.ProfessorID = gs2.ProfessorID
   AND gs1.CalendarID = gs2.CalendarID
   AND gs1.ScheduleID < gs2.ScheduleID
   AND NOT (gs1.EndTime <= gs2.StartTime OR gs1.StartTime >= gs2.EndTime)
JOIN Tbl_Professors p ON gs1.ProfessorID = p.ProfessorID
JOIN Tbl_Users u ON p.UserID = u.UserID
JOIN Tbl_SchoolCalendar sc ON gs1.CalendarID = sc.CalendarID
ORDER BY sc.CalendarDate, u.FullName;

SELECT
    gs1.ScheduleID AS schedule_1,
    gs2.ScheduleID AS schedule_2,
    gs1.RoomID AS room_id,
    r.Name AS room_name,
    sc.CalendarDate AS schedule_date,
    gs1.StartTime AS schedule_1_start,
    gs1.EndTime AS schedule_1_end,
    gs2.StartTime AS schedule_2_start,
    gs2.EndTime AS schedule_2_end
FROM Tbl_GeneratedSchedule gs1
JOIN Tbl_GeneratedSchedule gs2
    ON gs1.RoomID = gs2.RoomID
   AND gs1.CalendarID = gs2.CalendarID
   AND gs1.ScheduleID < gs2.ScheduleID
   AND NOT (gs1.EndTime <= gs2.StartTime OR gs1.StartTime >= gs2.EndTime)
JOIN Tbl_Rooms r ON gs1.RoomID = r.RoomID
JOIN Tbl_SchoolCalendar sc ON gs1.CalendarID = sc.CalendarID
ORDER BY sc.CalendarDate, r.Name;

SELECT
    gs.ScheduleID AS schedule_id,
    d.Name AS discipline_name,
    dc.IsPractical AS is_practical,
    r.Name AS room_name,
    r.IsPracticeRoom AS is_practice_room,
    sc.CalendarDate AS schedule_date,
    gs.StartTime AS start_time,
    gs.EndTime AS end_time
FROM Tbl_GeneratedSchedule gs
JOIN trx_Discipline_CourseYear dc ON gs.DisciplineCourseYearID = dc.DisciplineCourseYearID
JOIN Tbl_Disciplines d ON dc.DisciplineID = d.DisciplineID
JOIN Tbl_Rooms r ON gs.RoomID = r.RoomID
JOIN Tbl_SchoolCalendar sc ON gs.CalendarID = sc.CalendarID
WHERE dc.IsPractical = TRUE
  AND r.IsPracticeRoom = FALSE;

SELECT
    gs.ScheduleID AS schedule_id,
    cl.Name AS class_name,
    d.Name AS discipline_name,
    sc.CalendarDate AS schedule_date,
    sc.IsSchoolDay AS is_school_day,
    sc.Description AS calendar_description,
    gs.StartTime AS start_time,
    gs.EndTime AS end_time
FROM Tbl_GeneratedSchedule gs
JOIN Tbl_Classes cl ON gs.ClassID = cl.ClassID
JOIN trx_Discipline_CourseYear dc ON gs.DisciplineCourseYearID = dc.DisciplineCourseYearID
JOIN Tbl_Disciplines d ON dc.DisciplineID = d.DisciplineID
JOIN Tbl_SchoolCalendar sc ON gs.CalendarID = sc.CalendarID
WHERE sc.IsSchoolDay = FALSE;

SELECT
    gs.ScheduleID AS schedule_id,
    gs.ProfessorID AS professor_id,
    u.FullName AS professor_name,
    gs.DisciplineCourseYearID AS discipline_course_year_id,
    d.Name AS discipline_name,
    sc.CalendarDate AS schedule_date,
    gs.StartTime AS start_time,
    gs.EndTime AS end_time
FROM Tbl_GeneratedSchedule gs
JOIN Tbl_Professors p ON gs.ProfessorID = p.ProfessorID
JOIN Tbl_Users u ON p.UserID = u.UserID
JOIN trx_Discipline_CourseYear dc ON gs.DisciplineCourseYearID = dc.DisciplineCourseYearID
JOIN Tbl_Disciplines d ON dc.DisciplineID = d.DisciplineID
JOIN Tbl_SchoolCalendar sc ON gs.CalendarID = sc.CalendarID
LEFT JOIN trx_Professor_DisciplineCourseYear pd
    ON gs.ProfessorID = pd.ProfessorID
   AND gs.DisciplineCourseYearID = pd.DisciplineCourseYearID
WHERE pd.ProfessorID IS NULL;

SELECT
    gs.ScheduleID AS schedule_id,
    cl.Name AS class_name,
    class_course.Code AS class_course_code,
    discipline_course.Code AS discipline_course_code,
    d.Name AS discipline_name
FROM Tbl_GeneratedSchedule gs
JOIN Tbl_Classes cl ON gs.ClassID = cl.ClassID
JOIN Tbl_Courses class_course ON cl.CourseID = class_course.CourseID
JOIN trx_Discipline_CourseYear dc ON gs.DisciplineCourseYearID = dc.DisciplineCourseYearID
JOIN Tbl_Courses discipline_course ON dc.CourseID = discipline_course.CourseID
JOIN Tbl_Disciplines d ON dc.DisciplineID = d.DisciplineID
WHERE cl.CourseID <> dc.CourseID;

SELECT
    gs.ScheduleID AS schedule_id,
    cl.Name AS class_name,
    class_sy.Name AS class_school_year,
    discipline_sy.Name AS discipline_school_year,
    d.Name AS discipline_name
FROM Tbl_GeneratedSchedule gs
JOIN Tbl_Classes cl ON gs.ClassID = cl.ClassID
JOIN Tref_SchoolYears class_sy ON cl.SchoolYearID = class_sy.SchoolYearID
JOIN trx_Discipline_CourseYear dc ON gs.DisciplineCourseYearID = dc.DisciplineCourseYearID
JOIN Tref_SchoolYears discipline_sy ON dc.SchoolYearID = discipline_sy.SchoolYearID
JOIN Tbl_Disciplines d ON dc.DisciplineID = d.DisciplineID
WHERE cl.SchoolYearID <> dc.SchoolYearID;

SELECT
    'Tbl_Users' AS table_name,
    UserID AS id,
    InsertUsername,
    InsertDate,
    ChangeUsername,
    ChangeDate
FROM Tbl_Users
ORDER BY UserID;

SELECT
    'Tbl_Students' AS table_name,
    StudentID AS id,
    InsertUsername,
    InsertDate,
    ChangeUsername,
    ChangeDate
FROM Tbl_Students
ORDER BY StudentID;

SELECT
    'Tbl_Professors' AS table_name,
    ProfessorID AS id,
    InsertUsername,
    InsertDate,
    ChangeUsername,
    ChangeDate
FROM Tbl_Professors
ORDER BY ProfessorID;

SELECT
    'Tbl_GeneratedSchedule' AS table_name,
    ScheduleID AS id,
    InsertUsername,
    InsertDate,
    ChangeUsername,
    ChangeDate
FROM Tbl_GeneratedSchedule
ORDER BY ScheduleID;

SELECT
    'Tbl_AttendanceRecords' AS table_name,
    AttendanceRecordID AS id,
    InsertUsername,
    InsertDate,
    ChangeUsername,
    ChangeDate
FROM Tbl_AttendanceRecords
ORDER BY AttendanceRecordID;

SELECT
    TABLE_NAME AS table_name,
    COLUMN_NAME AS column_name,
    REFERENCED_TABLE_NAME AS referenced_table,
    REFERENCED_COLUMN_NAME AS referenced_column
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'academia360'
  AND REFERENCED_TABLE_NAME IS NOT NULL
ORDER BY TABLE_NAME, COLUMN_NAME;

SELECT
    'Roles' AS category,
    RoleID AS id,
    Name AS value
FROM Tref_UserRoles
UNION ALL
SELECT
    'Genders',
    GenderID,
    Name
FROM Tref_Gender
UNION ALL
SELECT
    'SchoolYears',
    SchoolYearID,
    Name
FROM Tref_SchoolYears
UNION ALL
SELECT
    'Courses',
    CourseID,
    Code
FROM Tbl_Courses
UNION ALL
SELECT
    'Classes',
    ClassID,
    Name
FROM Tbl_Classes
UNION ALL
SELECT
    'Professors',
    p.ProfessorID,
    u.FullName
FROM Tbl_Professors p
JOIN Tbl_Users u ON p.UserID = u.UserID
UNION ALL
SELECT
    'Students',
    StudentID,
    FullName
FROM Tbl_Students
UNION ALL
SELECT
    'Rooms',
    RoomID,
    Name
FROM Tbl_Rooms
UNION ALL
SELECT
    'Disciplines',
    DisciplineID,
    Name
FROM Tbl_Disciplines
ORDER BY category, id;