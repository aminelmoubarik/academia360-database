USE academia360;

SET FOREIGN_KEY_CHECKS = 0;

DELETE FROM Tbl_AttendanceRecords;
DELETE FROM Tbl_GeneratedSchedule;
DELETE FROM Tbl_TeacherAvailability;
DELETE FROM Tbl_SchoolCalendar;
DELETE FROM Tbl_Rooms;
DELETE FROM trx_Professor_DisciplineCourseYear;
DELETE FROM trx_Discipline_CourseYear;
DELETE FROM Tbl_Disciplines;
DELETE FROM Tbl_Professors;
DELETE FROM Tbl_Students;
DELETE FROM Tbl_Classes;
DELETE FROM Tbl_Courses;
DELETE FROM Tbl_Users;
DELETE FROM Tref_SchoolYears;
DELETE FROM Tref_Gender;
DELETE FROM Tref_UserRoles;

SET FOREIGN_KEY_CHECKS = 1;

ALTER TABLE Tref_UserRoles AUTO_INCREMENT = 1;
ALTER TABLE Tref_Gender AUTO_INCREMENT = 1;
ALTER TABLE Tref_SchoolYears AUTO_INCREMENT = 1;
ALTER TABLE Tbl_Users AUTO_INCREMENT = 1;
ALTER TABLE Tbl_Courses AUTO_INCREMENT = 1;
ALTER TABLE Tbl_Classes AUTO_INCREMENT = 1;
ALTER TABLE Tbl_Students AUTO_INCREMENT = 1;
ALTER TABLE Tbl_Professors AUTO_INCREMENT = 1;
ALTER TABLE Tbl_Disciplines AUTO_INCREMENT = 1;
ALTER TABLE trx_Discipline_CourseYear AUTO_INCREMENT = 1;
ALTER TABLE Tbl_Rooms AUTO_INCREMENT = 1;
ALTER TABLE Tbl_SchoolCalendar AUTO_INCREMENT = 1;
ALTER TABLE Tbl_TeacherAvailability AUTO_INCREMENT = 1;
ALTER TABLE Tbl_GeneratedSchedule AUTO_INCREMENT = 1;
ALTER TABLE Tbl_AttendanceRecords AUTO_INCREMENT = 1;

INSERT INTO Tref_UserRoles (
    RoleID,
    Name,
    InsertUsername
) VALUES
(1, 'admin', 'seed'),
(2, 'director', 'seed'),
(3, 'secretary', 'seed'),
(4, 'professor', 'seed');

INSERT INTO Tref_Gender (
    GenderID,
    Name,
    InsertUsername
) VALUES
(1, 'Male', 'seed'),
(2, 'Female', 'seed'),
(3, 'Other', 'seed');

INSERT INTO Tref_SchoolYears (
    SchoolYearID,
    Name,
    StartDate,
    EndDate,
    InsertUsername
) VALUES
(1, '2025/2026', '2025-09-01', '2026-07-31', 'seed'),
(2, '2026/2027', '2026-09-01', '2027-07-31', 'seed');

INSERT INTO Tbl_Courses (
    CourseID,
    Code,
    Name,
    InsertUsername
) VALUES
(1, 'TGEI', 'Técnico de Gestão de Equipamentos Informáticos', 'seed'),
(2, 'TGPSI', 'Técnico de Gestão e Programação de Sistemas Informáticos', 'seed'),
(3, 'TCIB', 'Técnico de Cibersegurança', 'seed');

INSERT INTO Tbl_Classes (
    ClassID,
    Name,
    CourseID,
    SchoolYearID,
    CourseYearNumber,
    InsertUsername
) VALUES
(1, 'TGEI 1A', 1, 1, 1, 'seed'),
(2, 'TGEI 2A', 1, 1, 2, 'seed'),
(3, 'TGPSI 1A', 2, 1, 1, 'seed'),
(4, 'TCIB 2A', 3, 1, 2, 'seed');

INSERT INTO Tbl_Users (
    UserID,
    FullName,
    Email,
    PasswordHash,
    RoleID,
    InsertUsername
) VALUES
(1, 'System Administrator', 'admin@academia360.local', NULL, 1, 'seed'),
(2, 'Laura Mendes', 'laura.mendes@academia360.local', NULL, 2, 'seed'),
(3, 'Rita Almeida', 'rita.almeida@academia360.local', NULL, 3, 'seed'),
(4, 'Miguel Ramos', 'miguel.ramos@academia360.local', NULL, 4, 'seed'),
(5, 'Inês Duarte', 'ines.duarte@academia360.local', NULL, 4, 'seed'),
(6, 'Pedro Neves', 'pedro.neves@academia360.local', NULL, 4, 'seed');

INSERT INTO Tbl_Professors (
    ProfessorID,
    UserID,
    PhotoPath,
    GenderID,
    Address,
    PostalCode,
    City,
    Contact,
    DateOfBirth,
    InsertUsername
) VALUES
(1, 4, NULL, 1, 'Rua das Flores 12', '4590-111', 'Paços de Ferreira', '910000001', '1985-03-12', 'seed'),
(2, 5, NULL, 2, 'Rua Nova 25', '4590-222', 'Paços de Ferreira', '910000002', '1990-07-20', 'seed'),
(3, 6, NULL, 1, 'Avenida Central 8', '4590-333', 'Paços de Ferreira', '910000003', '1982-11-05', 'seed');

INSERT INTO Tbl_Students (
    StudentID,
    FullName,
    StudentNumber,
    CardUID,
    ClassID,
    PhotoPath,
    GenderID,
    Address,
    PostalCode,
    City,
    Contact,
    DateOfBirth,
    InsertUsername
) VALUES
(1, 'João Pereira', 'STU001', 'CARD001', 1, NULL, 1, 'Rua A', '4590-001', 'Paços de Ferreira', '920000001', '2008-02-15', 'seed'),
(2, 'Mariana Costa', 'STU002', 'CARD002', 1, NULL, 2, 'Rua B', '4590-002', 'Paços de Ferreira', '920000002', '2008-05-22', 'seed'),
(3, 'Tiago Martins', 'STU003', 'CARD003', 2, NULL, 1, 'Rua C', '4590-003', 'Paços de Ferreira', '920000003', '2007-09-10', 'seed'),
(4, 'Beatriz Sousa', 'STU004', 'CARD004', 3, NULL, 2, 'Rua D', '4590-004', 'Paços de Ferreira', '920000004', '2008-12-01', 'seed'),
(5, 'Rui Almeida', 'STU005', 'CARD005', 4, NULL, 1, 'Rua E', '4590-005', 'Paços de Ferreira', '920000005', '2007-06-18', 'seed');

INSERT INTO Tbl_Disciplines (
    DisciplineID,
    Name,
    Code,
    InsertUsername
) VALUES
(1, 'Programming', 'PROG', 'seed'),
(2, 'Networks', 'NET', 'seed'),
(3, 'Databases', 'DB', 'seed'),
(4, 'Operating Systems', 'OS', 'seed'),
(5, 'Mathematics', 'MATH', 'seed');

INSERT INTO trx_Discipline_CourseYear (
    DisciplineCourseYearID,
    DisciplineID,
    CourseID,
    SchoolYearID,
    CourseYearNumber,
    TotalMinutes,
    LessonDurationMinutes,
    IsPractical,
    InsertUsername
) VALUES
(1, 1, 1, 1, 1, 7200, 60, TRUE, 'seed'),
(2, 2, 1, 1, 1, 6000, 60, TRUE, 'seed'),
(3, 3, 1, 1, 1, 4800, 60, TRUE, 'seed'),
(4, 1, 2, 1, 1, 8400, 60, TRUE, 'seed'),
(5, 3, 2, 1, 1, 6000, 60, TRUE, 'seed'),
(6, 2, 3, 1, 2, 7200, 60, TRUE, 'seed'),
(7, 4, 3, 1, 2, 6000, 60, TRUE, 'seed'),
(8, 5, 1, 1, 1, 3600, 60, FALSE, 'seed');

INSERT INTO trx_Professor_DisciplineCourseYear (
    ProfessorID,
    DisciplineCourseYearID,
    InsertUsername
) VALUES
(1, 1, 'seed'),
(1, 2, 'seed'),
(2, 3, 'seed'),
(2, 5, 'seed'),
(3, 6, 'seed'),
(3, 7, 'seed');

INSERT INTO Tbl_Rooms (
    RoomID,
    Name,
    Capacity,
    IsPracticeRoom,
    Location,
    InsertUsername
) VALUES
(1, 'Room 101', 30, FALSE, 'Main building - First floor', 'seed'),
(2, 'Computer Lab 1', 24, TRUE, 'Main building - Second floor', 'seed'),
(3, 'Computer Lab 2', 20, TRUE, 'Main building - Second floor', 'seed'),
(4, 'Room 202', 28, FALSE, 'Main building - Second floor', 'seed');

INSERT INTO Tbl_SchoolCalendar (
    CalendarID,
    SchoolYearID,
    CalendarDate,
    IsSchoolDay,
    Description,
    InsertUsername
) VALUES
(1, 1, '2025-09-15', TRUE, 'First school day', 'seed'),
(2, 1, '2025-09-16', TRUE, 'Regular school day', 'seed'),
(3, 1, '2025-09-17', TRUE, 'Regular school day', 'seed'),
(4, 1, '2025-12-25', FALSE, 'Christmas holiday', 'seed'),
(5, 1, '2026-01-01', FALSE, 'New year holiday', 'seed'),
(6, 1, '2026-05-15', TRUE, 'Regular school day', 'seed');

INSERT INTO Tbl_TeacherAvailability (
    TeacherAvailabilityID,
    ProfessorID,
    SchoolYearID,
    DayOfWeek,
    StartTime,
    EndTime,
    InsertUsername
) VALUES
(1, 1, 1, 'monday', '09:00:00', '13:00:00', 'seed'),
(2, 1, 1, 'tuesday', '09:00:00', '13:00:00', 'seed'),
(3, 2, 1, 'monday', '10:00:00', '16:00:00', 'seed'),
(4, 2, 1, 'wednesday', '09:00:00', '13:00:00', 'seed'),
(5, 3, 1, 'friday', '09:00:00', '15:00:00', 'seed');

INSERT INTO Tbl_GeneratedSchedule (
    ScheduleID,
    ClassID,
    DisciplineCourseYearID,
    ProfessorID,
    RoomID,
    CalendarID,
    StartTime,
    EndTime,
    Status,
    InsertUsername
) VALUES
(1, 1, 1, 1, 2, 1, '09:00:00', '10:00:00', 'approved', 'seed'),
(2, 1, 2, 1, 2, 1, '10:00:00', '11:00:00', 'approved', 'seed'),
(3, 1, 3, 2, 3, 2, '09:00:00', '10:00:00', 'approved', 'seed'),
(4, 3, 4, 1, 2, 3, '11:00:00', '12:00:00', 'draft', 'seed'),
(5, 4, 6, 3, 3, 6, '09:00:00', '10:00:00', 'approved', 'seed');

INSERT INTO Tbl_AttendanceRecords (
    AttendanceRecordID,
    StudentID,
    ScheduleID,
    PunchType,
    PunchMethod,
    PunchTime,
    IsSynced,
    InsertUsername
) VALUES
(1, 1, 1, 'in', 'nfc', '2025-09-15 08:58:00', TRUE, 'seed'),
(2, 1, 1, 'out', 'nfc', '2025-09-15 10:01:00', TRUE, 'seed'),
(3, 2, 1, 'in', 'qr', '2025-09-15 09:02:00', TRUE, 'seed'),
(4, 2, 1, 'out', 'qr', '2025-09-15 10:00:00', TRUE, 'seed'),
(5, 5, 5, 'in', 'manual', '2026-05-15 09:05:00', TRUE, 'seed');