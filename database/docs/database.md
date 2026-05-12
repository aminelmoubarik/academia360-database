# Academia360 Database Documentation

## Overview

The Academia360 database is designed to support attendance registration and automatic timetable management.

The main objective is to store information about students, professors, classes, disciplines, rooms, teacher availability, school calendar, generated schedules and attendance records.

## Main entities

### users

Stores system users and their roles.

Available roles:

- admin
- director
- secretary
- professor

### classes

Stores school classes, school year and course name.

### students

Stores students and links each student to a class. It also stores the card UID used for NFC/RFID/QR/barcode attendance registration.

### professors

Stores professor information. A professor can optionally be linked to a system user.

### disciplines

Stores school subjects. Each discipline has total hours, lesson duration and information about whether it is practical.

### professor_disciplines

Relationship table between professors and disciplines.

A professor can teach multiple disciplines and a discipline can be taught by multiple professors.

### rooms

Stores school rooms, capacity, location and whether the room can be used for practical lessons.

### school_calendar

Stores school days, holidays and calendar exceptions.

### teacher_availability

Stores the weekly availability of professors.

### generated_schedule

Stores the generated timetable. Each schedule entry links a class, discipline, professor, room, date and time.

### attendance_records

Stores student attendance punches. Each record contains the student, schedule, punch type, punch method and timestamp.

## SQL files

- `database/schema.sql`: creates the database and tables
- `database/seed.sql`: inserts test data
- `database/queries.sql`: contains validation queries

## Execution order

1. Run `schema.sql`
2. Run `seed.sql`
3. Run `queries.sql`

## Current status

The initial database model has been created and tested locally using MySQL/XAMPP and VS Code.