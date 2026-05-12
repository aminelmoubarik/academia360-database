CREATE DATABASE IF NOT EXISTS academia360;
USE academia360;

DROP TABLE IF EXISTS attendance_records;
DROP TABLE IF EXISTS generated_schedule;
DROP TABLE IF EXISTS teacher_availability;
DROP TABLE IF EXISTS school_calendar;
DROP TABLE IF EXISTS professor_disciplines;
DROP TABLE IF EXISTS disciplines;
DROP TABLE IF EXISTS professors;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS classes;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255),
    role ENUM('admin', 'director', 'secretary', 'professor') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE classes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    school_year VARCHAR(20) NOT NULL,
    course_name VARCHAR(120),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    student_number VARCHAR(50) UNIQUE,
    card_uid VARCHAR(100) UNIQUE,
    class_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (class_id) REFERENCES classes(id)
);

CREATE TABLE professors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(120) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE disciplines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    total_hours INT NOT NULL,
    lesson_duration_minutes INT NOT NULL DEFAULT 60,
    is_practical BOOLEAN NOT NULL DEFAULT FALSE,

    CHECK (total_hours > 0),
    CHECK (lesson_duration_minutes > 0)
);

CREATE TABLE professor_disciplines (
    professor_id INT NOT NULL,
    discipline_id INT NOT NULL,

    PRIMARY KEY (professor_id, discipline_id),

    FOREIGN KEY (professor_id) REFERENCES professors(id),
    FOREIGN KEY (discipline_id) REFERENCES disciplines(id)
);

CREATE TABLE rooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(80) NOT NULL,
    capacity INT,
    is_practice_room BOOLEAN NOT NULL DEFAULT FALSE,
    location VARCHAR(120),

    CHECK (capacity IS NULL OR capacity > 0)
);

CREATE TABLE school_calendar (
    id INT AUTO_INCREMENT PRIMARY KEY,
    calendar_date DATE NOT NULL UNIQUE,
    is_school_day BOOLEAN NOT NULL DEFAULT TRUE,
    description VARCHAR(255)
);

CREATE TABLE teacher_availability (
    id INT AUTO_INCREMENT PRIMARY KEY,
    professor_id INT NOT NULL,
    day_of_week ENUM('monday', 'tuesday', 'wednesday', 'thursday', 'friday') NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,

    FOREIGN KEY (professor_id) REFERENCES professors(id),

    CHECK (end_time > start_time)
);

CREATE TABLE generated_schedule (
    id INT AUTO_INCREMENT PRIMARY KEY,
    class_id INT NOT NULL,
    discipline_id INT NOT NULL,
    professor_id INT NOT NULL,
    room_id INT NOT NULL,
    schedule_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    status ENUM('draft', 'approved', 'cancelled') DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (discipline_id) REFERENCES disciplines(id),
    FOREIGN KEY (professor_id) REFERENCES professors(id),
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    FOREIGN KEY (schedule_date) REFERENCES school_calendar(calendar_date),

    UNIQUE (class_id, schedule_date, start_time, end_time),
    UNIQUE (professor_id, schedule_date, start_time, end_time),
    UNIQUE (room_id, schedule_date, start_time, end_time),

    CHECK (end_time > start_time)
);

CREATE TABLE attendance_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    schedule_id INT,
    punch_type ENUM('in', 'out') NOT NULL,
    punch_method ENUM('nfc', 'rfid', 'qr', 'barcode', 'manual') NOT NULL,
    punch_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_synced BOOLEAN NOT NULL DEFAULT TRUE,

    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (schedule_id) REFERENCES generated_schedule(id)
);