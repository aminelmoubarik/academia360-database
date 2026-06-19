CREATE DATABASE IF NOT EXISTS academia360;
USE academia360;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS Tbl_AttendanceJustifications;
DROP TABLE IF EXISTS Tbl_AttendanceRecords;
DROP TABLE IF EXISTS Tbl_GeneratedSchedule;
DROP TABLE IF EXISTS Tbl_TeacherAvailability;
DROP TABLE IF EXISTS Tbl_SchoolCalendar;
DROP TABLE IF EXISTS Tbl_Rooms;
DROP TABLE IF EXISTS trx_Professor_DisciplineCourseYear;
DROP TABLE IF EXISTS trx_Discipline_CourseYear;
DROP TABLE IF EXISTS Tbl_Disciplines;
DROP TABLE IF EXISTS Tbl_Professors;
DROP TABLE IF EXISTS Tbl_Students;
DROP TABLE IF EXISTS Tbl_Classes;
DROP TABLE IF EXISTS Tbl_Courses;
DROP TABLE IF EXISTS Tbl_Users;
DROP TABLE IF EXISTS Tref_SchoolYears;
DROP TABLE IF EXISTS Tref_Gender;
DROP TABLE IF EXISTS Tref_UserRoles;

DROP TABLE IF EXISTS attendance_records;
DROP TABLE IF EXISTS generated_schedule;
DROP TABLE IF EXISTS teacher_availability;
DROP TABLE IF EXISTS school_calendar;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS professor_disciplines;
DROP TABLE IF EXISTS disciplines;
DROP TABLE IF EXISTS professors;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS classes;
DROP TABLE IF EXISTS users;

SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE Tref_UserRoles (
    RoleID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(50) NOT NULL UNIQUE,

    InsertUsername VARCHAR(120) NOT NULL DEFAULT 'system',
    InsertDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ChangeUsername VARCHAR(120),
    ChangeDate DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Tref_Gender (
    GenderID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(50) NOT NULL UNIQUE,

    InsertUsername VARCHAR(120) NOT NULL DEFAULT 'system',
    InsertDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ChangeUsername VARCHAR(120),
    ChangeDate DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Tref_SchoolYears (
    SchoolYearID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(20) NOT NULL UNIQUE,
    StartDate DATE NOT NULL,
    EndDate DATE NOT NULL,

    InsertUsername VARCHAR(120) NOT NULL DEFAULT 'system',
    InsertDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ChangeUsername VARCHAR(120),
    ChangeDate DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    CHECK (EndDate > StartDate)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Tbl_Users (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    FullName VARCHAR(120) NOT NULL,
    Email VARCHAR(120) NOT NULL UNIQUE,
    PasswordHash VARCHAR(255),
    RoleID INT NOT NULL,

    InsertUsername VARCHAR(120) NOT NULL DEFAULT 'system',
    InsertDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ChangeUsername VARCHAR(120),
    ChangeDate DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (RoleID) REFERENCES Tref_UserRoles(RoleID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Tbl_Courses (
    CourseID INT AUTO_INCREMENT PRIMARY KEY,
    Code VARCHAR(30) NOT NULL UNIQUE,
    Name VARCHAR(120) NOT NULL,

    InsertUsername VARCHAR(120) NOT NULL DEFAULT 'system',
    InsertDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ChangeUsername VARCHAR(120),
    ChangeDate DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Tbl_Classes (
    ClassID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(50) NOT NULL,
    CourseID INT NOT NULL,
    SchoolYearID INT NOT NULL,
    CourseYearNumber INT NOT NULL,

    InsertUsername VARCHAR(120) NOT NULL DEFAULT 'system',
    InsertDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ChangeUsername VARCHAR(120),
    ChangeDate DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (CourseID) REFERENCES Tbl_Courses(CourseID),
    FOREIGN KEY (SchoolYearID) REFERENCES Tref_SchoolYears(SchoolYearID),

    UNIQUE (Name, CourseID, SchoolYearID),
    CHECK (CourseYearNumber > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Tbl_Students (
    StudentID INT AUTO_INCREMENT PRIMARY KEY,
    FullName VARCHAR(120) NOT NULL,
    StudentNumber VARCHAR(50) UNIQUE,
    CardUID VARCHAR(100) UNIQUE,
    ClassID INT,
    PhotoPath VARCHAR(255),
    GenderID INT,
    Address VARCHAR(255),
    PostalCode VARCHAR(20),
    City VARCHAR(120),
    Contact VARCHAR(120),
    DateOfBirth DATE,

    InsertUsername VARCHAR(120) NOT NULL DEFAULT 'system',
    InsertDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ChangeUsername VARCHAR(120),
    ChangeDate DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (ClassID) REFERENCES Tbl_Classes(ClassID),
    FOREIGN KEY (GenderID) REFERENCES Tref_Gender(GenderID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Tbl_Professors (
    ProfessorID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT NOT NULL UNIQUE,
    PhotoPath VARCHAR(255),
    GenderID INT,
    Address VARCHAR(255),
    PostalCode VARCHAR(20),
    City VARCHAR(120),
    Contact VARCHAR(120),
    DateOfBirth DATE,

    InsertUsername VARCHAR(120) NOT NULL DEFAULT 'system',
    InsertDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ChangeUsername VARCHAR(120),
    ChangeDate DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (UserID) REFERENCES Tbl_Users(UserID),
    FOREIGN KEY (GenderID) REFERENCES Tref_Gender(GenderID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Tbl_Disciplines (
    DisciplineID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(120) NOT NULL,
    Code VARCHAR(50),

    InsertUsername VARCHAR(120) NOT NULL DEFAULT 'system',
    InsertDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ChangeUsername VARCHAR(120),
    ChangeDate DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE (Name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE trx_Discipline_CourseYear (
    DisciplineCourseYearID INT AUTO_INCREMENT PRIMARY KEY,
    DisciplineID INT NOT NULL,
    CourseID INT NOT NULL,
    SchoolYearID INT NOT NULL,
    CourseYearNumber INT NOT NULL,
    TotalMinutes INT NOT NULL,
    LessonDurationMinutes INT NOT NULL DEFAULT 60,
    IsPractical BOOLEAN NOT NULL DEFAULT FALSE,

    InsertUsername VARCHAR(120) NOT NULL DEFAULT 'system',
    InsertDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ChangeUsername VARCHAR(120),
    ChangeDate DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (DisciplineID) REFERENCES Tbl_Disciplines(DisciplineID),
    FOREIGN KEY (CourseID) REFERENCES Tbl_Courses(CourseID),
    FOREIGN KEY (SchoolYearID) REFERENCES Tref_SchoolYears(SchoolYearID),

    UNIQUE (DisciplineID, CourseID, SchoolYearID, CourseYearNumber),

    CHECK (CourseYearNumber > 0),
    CHECK (TotalMinutes > 0),
    CHECK (LessonDurationMinutes > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE trx_Professor_DisciplineCourseYear (
    ProfessorID INT NOT NULL,
    DisciplineCourseYearID INT NOT NULL,

    InsertUsername VARCHAR(120) NOT NULL DEFAULT 'system',
    InsertDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ChangeUsername VARCHAR(120),
    ChangeDate DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (ProfessorID, DisciplineCourseYearID),

    FOREIGN KEY (ProfessorID) REFERENCES Tbl_Professors(ProfessorID),
    FOREIGN KEY (DisciplineCourseYearID) REFERENCES trx_Discipline_CourseYear(DisciplineCourseYearID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Tbl_Rooms (
    RoomID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(80) NOT NULL,
    Capacity INT,
    IsPracticeRoom BOOLEAN NOT NULL DEFAULT FALSE,
    Location VARCHAR(120),

    InsertUsername VARCHAR(120) NOT NULL DEFAULT 'system',
    InsertDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ChangeUsername VARCHAR(120),
    ChangeDate DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    CHECK (Capacity IS NULL OR Capacity > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Tbl_SchoolCalendar (
    CalendarID INT AUTO_INCREMENT PRIMARY KEY,
    SchoolYearID INT NOT NULL,
    CalendarDate DATE NOT NULL UNIQUE,
    IsSchoolDay BOOLEAN NOT NULL DEFAULT TRUE,
    Description VARCHAR(255),

    InsertUsername VARCHAR(120) NOT NULL DEFAULT 'system',
    InsertDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ChangeUsername VARCHAR(120),
    ChangeDate DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (SchoolYearID) REFERENCES Tref_SchoolYears(SchoolYearID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Tbl_TeacherAvailability (
    TeacherAvailabilityID INT AUTO_INCREMENT PRIMARY KEY,
    ProfessorID INT NOT NULL,
    SchoolYearID INT NOT NULL,
    DayOfWeek ENUM('monday', 'tuesday', 'wednesday', 'thursday', 'friday') NOT NULL,
    StartTime TIME NOT NULL,
    EndTime TIME NOT NULL,

    InsertUsername VARCHAR(120) NOT NULL DEFAULT 'system',
    InsertDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ChangeUsername VARCHAR(120),
    ChangeDate DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (ProfessorID) REFERENCES Tbl_Professors(ProfessorID),
    FOREIGN KEY (SchoolYearID) REFERENCES Tref_SchoolYears(SchoolYearID),

    CHECK (EndTime > StartTime)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Tbl_GeneratedSchedule (
    ScheduleID INT AUTO_INCREMENT PRIMARY KEY,
    ClassID INT NOT NULL,
    DisciplineCourseYearID INT NOT NULL,
    ProfessorID INT NOT NULL,
    RoomID INT NOT NULL,
    CalendarID INT NOT NULL,
    StartTime TIME NOT NULL,
    EndTime TIME NOT NULL,
    Status ENUM('draft', 'approved', 'cancelled') DEFAULT 'draft',

    InsertUsername VARCHAR(120) NOT NULL DEFAULT 'system',
    InsertDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ChangeUsername VARCHAR(120),
    ChangeDate DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (ClassID) REFERENCES Tbl_Classes(ClassID),
    FOREIGN KEY (DisciplineCourseYearID) REFERENCES trx_Discipline_CourseYear(DisciplineCourseYearID),
    FOREIGN KEY (ProfessorID) REFERENCES Tbl_Professors(ProfessorID),
    FOREIGN KEY (RoomID) REFERENCES Tbl_Rooms(RoomID),
    FOREIGN KEY (CalendarID) REFERENCES Tbl_SchoolCalendar(CalendarID),

    UNIQUE (ClassID, CalendarID, StartTime, EndTime),
    UNIQUE (ProfessorID, CalendarID, StartTime, EndTime),
    UNIQUE (RoomID, CalendarID, StartTime, EndTime),

    CHECK (EndTime > StartTime)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE Tbl_AttendanceJustifications (
    JustificationID INT AUTO_INCREMENT PRIMARY KEY,
    StudentID INT NOT NULL,
    ScheduleID INT NULL,
    JustificationDate DATE NOT NULL,
    Reason TEXT NOT NULL,
    Status ENUM('pending', 'approved', 'rejected') NOT NULL DEFAULT 'pending',
    DocumentPath VARCHAR(255),
    ReviewedByUserID INT NULL,
    ReviewedAt DATETIME NULL,

    InsertUsername VARCHAR(120) NOT NULL DEFAULT 'system',
    InsertDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ChangeUsername VARCHAR(120),
    ChangeDate DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (StudentID) REFERENCES Tbl_Students(StudentID),
    FOREIGN KEY (ScheduleID) REFERENCES Tbl_GeneratedSchedule(ScheduleID),
    FOREIGN KEY (ReviewedByUserID) REFERENCES Tbl_Users(UserID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Tbl_AttendanceRecords (
    AttendanceRecordID INT AUTO_INCREMENT PRIMARY KEY,
    StudentID INT NOT NULL,
    ScheduleID INT,
    PunchType ENUM('in', 'out') NOT NULL,
    PunchMethod ENUM('nfc', 'rfid', 'qr', 'barcode', 'manual') NOT NULL,
    PunchTime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    IsSynced BOOLEAN NOT NULL DEFAULT TRUE,

    InsertUsername VARCHAR(120) NOT NULL DEFAULT 'system',
    InsertDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ChangeUsername VARCHAR(120),
    ChangeDate DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (StudentID) REFERENCES Tbl_Students(StudentID),
    FOREIGN KEY (ScheduleID) REFERENCES Tbl_GeneratedSchedule(ScheduleID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;