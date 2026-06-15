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
(1, 'Admin User', 'admin@academia360.local', NULL, 1, 'seed'),
(2, 'Director User', 'director@academia360.local', NULL, 2, 'seed'),
(3, 'Secretary User', 'secretary@academia360.local', NULL, 3, 'seed'),
(4, 'Daniel Martins', 'daniel.martins@academia360.local', NULL, 4, 'seed'),
(5, 'Ana Costa', 'ana.costa@academia360.local', NULL, 4, 'seed'),
(6, 'Carlos Ferreira', 'carlos.ferreira@academia360.local', NULL, 4, 'seed');

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
(3, 7, 'seed'),
(2, 8, 'seed');

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

-- Extra school days for realistic schedule generation tests.
-- The first seed only had a few isolated days; this gives the generator
-- enough valid dates to test a month or a full school year.
INSERT INTO Tbl_SchoolCalendar (
    CalendarID,
    SchoolYearID,
    CalendarDate,
    IsSchoolDay,
    Description,
    InsertUsername
) VALUES
(7, 1, '2025-09-18', TRUE, 'Regular school day', 'seed'),
(8, 1, '2025-09-19', TRUE, 'Regular school day', 'seed'),
(9, 1, '2025-09-22', TRUE, 'Regular school day', 'seed'),
(10, 1, '2025-09-23', TRUE, 'Regular school day', 'seed'),
(11, 1, '2025-09-24', TRUE, 'Regular school day', 'seed'),
(12, 1, '2025-09-25', TRUE, 'Regular school day', 'seed'),
(13, 1, '2025-09-26', TRUE, 'Regular school day', 'seed'),
(14, 1, '2025-09-29', TRUE, 'Regular school day', 'seed'),
(15, 1, '2025-09-30', TRUE, 'Regular school day', 'seed'),
(16, 1, '2025-10-01', TRUE, 'Regular school day', 'seed'),
(17, 1, '2025-10-02', TRUE, 'Regular school day', 'seed'),
(18, 1, '2025-10-03', TRUE, 'Regular school day', 'seed'),
(19, 1, '2025-10-06', TRUE, 'Regular school day', 'seed'),
(20, 1, '2025-10-07', TRUE, 'Regular school day', 'seed'),
(21, 1, '2025-10-08', TRUE, 'Regular school day', 'seed'),
(22, 1, '2025-10-09', TRUE, 'Regular school day', 'seed'),
(23, 1, '2025-10-10', TRUE, 'Regular school day', 'seed'),
(24, 1, '2025-10-13', TRUE, 'Regular school day', 'seed'),
(25, 1, '2025-10-14', TRUE, 'Regular school day', 'seed'),
(26, 1, '2025-10-15', TRUE, 'Regular school day', 'seed'),
(27, 1, '2025-10-16', TRUE, 'Regular school day', 'seed'),
(28, 1, '2025-10-17', TRUE, 'Regular school day', 'seed'),
(29, 1, '2025-10-20', TRUE, 'Regular school day', 'seed'),
(30, 1, '2025-10-21', TRUE, 'Regular school day', 'seed'),
(31, 1, '2025-10-22', TRUE, 'Regular school day', 'seed'),
(32, 1, '2025-10-23', TRUE, 'Regular school day', 'seed'),
(33, 1, '2025-10-24', TRUE, 'Regular school day', 'seed'),
(34, 1, '2025-10-27', TRUE, 'Regular school day', 'seed'),
(35, 1, '2025-10-28', TRUE, 'Regular school day', 'seed'),
(36, 1, '2025-10-29', TRUE, 'Regular school day', 'seed'),
(37, 1, '2025-10-30', TRUE, 'Regular school day', 'seed'),
(38, 1, '2025-10-31', TRUE, 'Regular school day', 'seed'),
(39, 1, '2025-11-03', TRUE, 'Regular school day', 'seed'),
(40, 1, '2025-11-04', TRUE, 'Regular school day', 'seed'),
(41, 1, '2025-11-05', TRUE, 'Regular school day', 'seed'),
(42, 1, '2025-11-06', TRUE, 'Regular school day', 'seed'),
(43, 1, '2025-11-07', TRUE, 'Regular school day', 'seed'),
(44, 1, '2025-11-10', TRUE, 'Regular school day', 'seed'),
(45, 1, '2025-11-11', TRUE, 'Regular school day', 'seed'),
(46, 1, '2025-11-12', TRUE, 'Regular school day', 'seed'),
(47, 1, '2025-11-13', TRUE, 'Regular school day', 'seed'),
(48, 1, '2025-11-14', TRUE, 'Regular school day', 'seed'),
(49, 1, '2025-11-17', TRUE, 'Regular school day', 'seed'),
(50, 1, '2025-11-18', TRUE, 'Regular school day', 'seed'),
(51, 1, '2025-11-19', TRUE, 'Regular school day', 'seed'),
(52, 1, '2025-11-20', TRUE, 'Regular school day', 'seed'),
(53, 1, '2025-11-21', TRUE, 'Regular school day', 'seed'),
(54, 1, '2025-11-24', TRUE, 'Regular school day', 'seed'),
(55, 1, '2025-11-25', TRUE, 'Regular school day', 'seed'),
(56, 1, '2025-11-26', TRUE, 'Regular school day', 'seed'),
(57, 1, '2025-11-27', TRUE, 'Regular school day', 'seed'),
(58, 1, '2025-11-28', TRUE, 'Regular school day', 'seed'),
(59, 1, '2025-12-01', TRUE, 'Regular school day', 'seed'),
(60, 1, '2025-12-02', TRUE, 'Regular school day', 'seed'),
(61, 1, '2025-12-03', TRUE, 'Regular school day', 'seed'),
(62, 1, '2025-12-04', TRUE, 'Regular school day', 'seed'),
(63, 1, '2025-12-05', TRUE, 'Regular school day', 'seed'),
(64, 1, '2025-12-08', TRUE, 'Regular school day', 'seed'),
(65, 1, '2025-12-09', TRUE, 'Regular school day', 'seed'),
(66, 1, '2025-12-10', TRUE, 'Regular school day', 'seed'),
(67, 1, '2025-12-11', TRUE, 'Regular school day', 'seed'),
(68, 1, '2025-12-12', TRUE, 'Regular school day', 'seed'),
(69, 1, '2025-12-15', TRUE, 'Regular school day', 'seed'),
(70, 1, '2025-12-16', TRUE, 'Regular school day', 'seed'),
(71, 1, '2025-12-17', TRUE, 'Regular school day', 'seed'),
(72, 1, '2025-12-18', TRUE, 'Regular school day', 'seed'),
(73, 1, '2025-12-19', TRUE, 'Regular school day', 'seed'),
(74, 1, '2025-12-22', TRUE, 'Regular school day', 'seed'),
(75, 1, '2025-12-23', TRUE, 'Regular school day', 'seed'),
(76, 1, '2025-12-24', TRUE, 'Regular school day', 'seed'),
(77, 1, '2025-12-26', TRUE, 'Regular school day', 'seed'),
(78, 1, '2025-12-29', TRUE, 'Regular school day', 'seed'),
(79, 1, '2025-12-30', TRUE, 'Regular school day', 'seed'),
(80, 1, '2025-12-31', TRUE, 'Regular school day', 'seed'),
(81, 1, '2026-01-02', TRUE, 'Regular school day', 'seed'),
(82, 1, '2026-01-05', TRUE, 'Regular school day', 'seed'),
(83, 1, '2026-01-06', TRUE, 'Regular school day', 'seed'),
(84, 1, '2026-01-07', TRUE, 'Regular school day', 'seed'),
(85, 1, '2026-01-08', TRUE, 'Regular school day', 'seed'),
(86, 1, '2026-01-09', TRUE, 'Regular school day', 'seed'),
(87, 1, '2026-01-12', TRUE, 'Regular school day', 'seed'),
(88, 1, '2026-01-13', TRUE, 'Regular school day', 'seed'),
(89, 1, '2026-01-14', TRUE, 'Regular school day', 'seed'),
(90, 1, '2026-01-15', TRUE, 'Regular school day', 'seed'),
(91, 1, '2026-01-16', TRUE, 'Regular school day', 'seed'),
(92, 1, '2026-01-19', TRUE, 'Regular school day', 'seed'),
(93, 1, '2026-01-20', TRUE, 'Regular school day', 'seed'),
(94, 1, '2026-01-21', TRUE, 'Regular school day', 'seed'),
(95, 1, '2026-01-22', TRUE, 'Regular school day', 'seed'),
(96, 1, '2026-01-23', TRUE, 'Regular school day', 'seed'),
(97, 1, '2026-01-26', TRUE, 'Regular school day', 'seed'),
(98, 1, '2026-01-27', TRUE, 'Regular school day', 'seed'),
(99, 1, '2026-01-28', TRUE, 'Regular school day', 'seed'),
(100, 1, '2026-01-29', TRUE, 'Regular school day', 'seed'),
(101, 1, '2026-01-30', TRUE, 'Regular school day', 'seed'),
(102, 1, '2026-02-02', TRUE, 'Regular school day', 'seed'),
(103, 1, '2026-02-03', TRUE, 'Regular school day', 'seed'),
(104, 1, '2026-02-04', TRUE, 'Regular school day', 'seed'),
(105, 1, '2026-02-05', TRUE, 'Regular school day', 'seed'),
(106, 1, '2026-02-06', TRUE, 'Regular school day', 'seed'),
(107, 1, '2026-02-09', TRUE, 'Regular school day', 'seed'),
(108, 1, '2026-02-10', TRUE, 'Regular school day', 'seed'),
(109, 1, '2026-02-11', TRUE, 'Regular school day', 'seed'),
(110, 1, '2026-02-12', TRUE, 'Regular school day', 'seed'),
(111, 1, '2026-02-13', TRUE, 'Regular school day', 'seed'),
(112, 1, '2026-02-16', TRUE, 'Regular school day', 'seed'),
(113, 1, '2026-02-17', TRUE, 'Regular school day', 'seed'),
(114, 1, '2026-02-18', TRUE, 'Regular school day', 'seed'),
(115, 1, '2026-02-19', TRUE, 'Regular school day', 'seed'),
(116, 1, '2026-02-20', TRUE, 'Regular school day', 'seed'),
(117, 1, '2026-02-23', TRUE, 'Regular school day', 'seed'),
(118, 1, '2026-02-24', TRUE, 'Regular school day', 'seed'),
(119, 1, '2026-02-25', TRUE, 'Regular school day', 'seed'),
(120, 1, '2026-02-26', TRUE, 'Regular school day', 'seed'),
(121, 1, '2026-02-27', TRUE, 'Regular school day', 'seed'),
(122, 1, '2026-03-02', TRUE, 'Regular school day', 'seed'),
(123, 1, '2026-03-03', TRUE, 'Regular school day', 'seed'),
(124, 1, '2026-03-04', TRUE, 'Regular school day', 'seed'),
(125, 1, '2026-03-05', TRUE, 'Regular school day', 'seed'),
(126, 1, '2026-03-06', TRUE, 'Regular school day', 'seed'),
(127, 1, '2026-03-09', TRUE, 'Regular school day', 'seed'),
(128, 1, '2026-03-10', TRUE, 'Regular school day', 'seed'),
(129, 1, '2026-03-11', TRUE, 'Regular school day', 'seed'),
(130, 1, '2026-03-12', TRUE, 'Regular school day', 'seed'),
(131, 1, '2026-03-13', TRUE, 'Regular school day', 'seed'),
(132, 1, '2026-03-16', TRUE, 'Regular school day', 'seed'),
(133, 1, '2026-03-17', TRUE, 'Regular school day', 'seed'),
(134, 1, '2026-03-18', TRUE, 'Regular school day', 'seed'),
(135, 1, '2026-03-19', TRUE, 'Regular school day', 'seed'),
(136, 1, '2026-03-20', TRUE, 'Regular school day', 'seed'),
(137, 1, '2026-03-23', TRUE, 'Regular school day', 'seed'),
(138, 1, '2026-03-24', TRUE, 'Regular school day', 'seed'),
(139, 1, '2026-03-25', TRUE, 'Regular school day', 'seed'),
(140, 1, '2026-03-26', TRUE, 'Regular school day', 'seed'),
(141, 1, '2026-03-27', TRUE, 'Regular school day', 'seed'),
(142, 1, '2026-03-30', TRUE, 'Regular school day', 'seed'),
(143, 1, '2026-03-31', TRUE, 'Regular school day', 'seed'),
(144, 1, '2026-04-01', TRUE, 'Regular school day', 'seed'),
(145, 1, '2026-04-02', TRUE, 'Regular school day', 'seed'),
(146, 1, '2026-04-03', TRUE, 'Regular school day', 'seed'),
(147, 1, '2026-04-06', TRUE, 'Regular school day', 'seed'),
(148, 1, '2026-04-07', TRUE, 'Regular school day', 'seed'),
(149, 1, '2026-04-08', TRUE, 'Regular school day', 'seed'),
(150, 1, '2026-04-09', TRUE, 'Regular school day', 'seed'),
(151, 1, '2026-04-10', TRUE, 'Regular school day', 'seed'),
(152, 1, '2026-04-13', TRUE, 'Regular school day', 'seed'),
(153, 1, '2026-04-14', TRUE, 'Regular school day', 'seed'),
(154, 1, '2026-04-15', TRUE, 'Regular school day', 'seed'),
(155, 1, '2026-04-16', TRUE, 'Regular school day', 'seed'),
(156, 1, '2026-04-17', TRUE, 'Regular school day', 'seed'),
(157, 1, '2026-04-20', TRUE, 'Regular school day', 'seed'),
(158, 1, '2026-04-21', TRUE, 'Regular school day', 'seed'),
(159, 1, '2026-04-22', TRUE, 'Regular school day', 'seed'),
(160, 1, '2026-04-23', TRUE, 'Regular school day', 'seed'),
(161, 1, '2026-04-24', TRUE, 'Regular school day', 'seed'),
(162, 1, '2026-04-27', TRUE, 'Regular school day', 'seed'),
(163, 1, '2026-04-28', TRUE, 'Regular school day', 'seed'),
(164, 1, '2026-04-29', TRUE, 'Regular school day', 'seed'),
(165, 1, '2026-04-30', TRUE, 'Regular school day', 'seed'),
(166, 1, '2026-05-01', TRUE, 'Regular school day', 'seed'),
(167, 1, '2026-05-04', TRUE, 'Regular school day', 'seed'),
(168, 1, '2026-05-05', TRUE, 'Regular school day', 'seed'),
(169, 1, '2026-05-06', TRUE, 'Regular school day', 'seed'),
(170, 1, '2026-05-07', TRUE, 'Regular school day', 'seed'),
(171, 1, '2026-05-08', TRUE, 'Regular school day', 'seed'),
(172, 1, '2026-05-11', TRUE, 'Regular school day', 'seed'),
(173, 1, '2026-05-12', TRUE, 'Regular school day', 'seed'),
(174, 1, '2026-05-13', TRUE, 'Regular school day', 'seed'),
(175, 1, '2026-05-14', TRUE, 'Regular school day', 'seed'),
(176, 1, '2026-05-18', TRUE, 'Regular school day', 'seed'),
(177, 1, '2026-05-19', TRUE, 'Regular school day', 'seed'),
(178, 1, '2026-05-20', TRUE, 'Regular school day', 'seed'),
(179, 1, '2026-05-21', TRUE, 'Regular school day', 'seed'),
(180, 1, '2026-05-22', TRUE, 'Regular school day', 'seed'),
(181, 1, '2026-05-25', TRUE, 'Regular school day', 'seed'),
(182, 1, '2026-05-26', TRUE, 'Regular school day', 'seed'),
(183, 1, '2026-05-27', TRUE, 'Regular school day', 'seed'),
(184, 1, '2026-05-28', TRUE, 'Regular school day', 'seed'),
(185, 1, '2026-05-29', TRUE, 'Regular school day', 'seed'),
(186, 1, '2026-06-01', TRUE, 'Regular school day', 'seed'),
(187, 1, '2026-06-02', TRUE, 'Regular school day', 'seed'),
(188, 1, '2026-06-03', TRUE, 'Regular school day', 'seed'),
(189, 1, '2026-06-04', TRUE, 'Regular school day', 'seed'),
(190, 1, '2026-06-05', TRUE, 'Regular school day', 'seed'),
(191, 1, '2026-06-08', TRUE, 'Regular school day', 'seed'),
(192, 1, '2026-06-09', TRUE, 'Regular school day', 'seed'),
(193, 1, '2026-06-10', TRUE, 'Regular school day', 'seed'),
(194, 1, '2026-06-11', TRUE, 'Regular school day', 'seed'),
(195, 1, '2026-06-12', TRUE, 'Regular school day', 'seed'),
(196, 1, '2026-06-15', TRUE, 'Regular school day', 'seed'),
(197, 1, '2026-06-16', TRUE, 'Regular school day', 'seed'),
(198, 1, '2026-06-17', TRUE, 'Regular school day', 'seed'),
(199, 1, '2026-06-18', TRUE, 'Regular school day', 'seed'),
(200, 1, '2026-06-19', TRUE, 'Regular school day', 'seed'),
(201, 1, '2026-06-22', TRUE, 'Regular school day', 'seed'),
(202, 1, '2026-06-23', TRUE, 'Regular school day', 'seed'),
(203, 1, '2026-06-24', TRUE, 'Regular school day', 'seed'),
(204, 1, '2026-06-25', TRUE, 'Regular school day', 'seed'),
(205, 1, '2026-06-26', TRUE, 'Regular school day', 'seed'),
(206, 1, '2026-06-29', TRUE, 'Regular school day', 'seed'),
(207, 1, '2026-06-30', TRUE, 'Regular school day', 'seed'),
(208, 1, '2026-07-01', TRUE, 'Regular school day', 'seed'),
(209, 1, '2026-07-02', TRUE, 'Regular school day', 'seed'),
(210, 1, '2026-07-03', TRUE, 'Regular school day', 'seed'),
(211, 1, '2026-07-06', TRUE, 'Regular school day', 'seed'),
(212, 1, '2026-07-07', TRUE, 'Regular school day', 'seed'),
(213, 1, '2026-07-08', TRUE, 'Regular school day', 'seed'),
(214, 1, '2026-07-09', TRUE, 'Regular school day', 'seed'),
(215, 1, '2026-07-10', TRUE, 'Regular school day', 'seed'),
(216, 1, '2026-07-13', TRUE, 'Regular school day', 'seed'),
(217, 1, '2026-07-14', TRUE, 'Regular school day', 'seed'),
(218, 1, '2026-07-15', TRUE, 'Regular school day', 'seed'),
(219, 1, '2026-07-16', TRUE, 'Regular school day', 'seed'),
(220, 1, '2026-07-17', TRUE, 'Regular school day', 'seed'),
(221, 1, '2026-07-20', TRUE, 'Regular school day', 'seed'),
(222, 1, '2026-07-21', TRUE, 'Regular school day', 'seed'),
(223, 1, '2026-07-22', TRUE, 'Regular school day', 'seed'),
(224, 1, '2026-07-23', TRUE, 'Regular school day', 'seed'),
(225, 1, '2026-07-24', TRUE, 'Regular school day', 'seed'),
(226, 1, '2026-07-27', TRUE, 'Regular school day', 'seed'),
(227, 1, '2026-07-28', TRUE, 'Regular school day', 'seed'),
(228, 1, '2026-07-29', TRUE, 'Regular school day', 'seed'),
(229, 1, '2026-07-30', TRUE, 'Regular school day', 'seed'),
(230, 1, '2026-07-31', TRUE, 'Regular school day', 'seed');


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