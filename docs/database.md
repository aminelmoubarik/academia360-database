# Academia360 Database Documentation

This document explains the current MySQL database model used by the Academia360 backend.

The database was refactored to support a more complete school management system with attendance, schedules, courses, classes, rooms, students, professors, teacher availability and role-based access control.

---

## 1. Database Overview

The database supports the following main areas:

- Authentication and roles
- Students
- Professors
- Courses
- Classes
- School years
- Disciplines
- Discipline workload by course and school year
- Professor assignment to disciplines
- Rooms
- School calendar
- Teacher availability
- Generated schedules
- Attendance records

The database name is:

```text
academia360
```

---

## 2. Naming Convention

The database uses prefixes to make table purposes easier to identify.

| Prefix | Meaning | Example |
|---|---|---|
| `Tbl_` | Main data table | `Tbl_Students` |
| `Tref_` | Reference table / fixed list | `Tref_UserRoles` |
| `trx_` | Relationship table | `trx_Discipline_CourseYear` |

---

## 3. Audit Columns

All tables include audit columns.

```sql
InsertUsername VARCHAR(120) NOT NULL DEFAULT 'system',
InsertDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
ChangeUsername VARCHAR(120),
ChangeDate DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP
```

These columns allow the system to track:

- Who inserted the record
- When the record was inserted
- Who last modified the record
- When the record was last modified

---

## 4. Reference Tables

Reference tables store controlled values used by other tables.

---

### 4.1. `Tref_UserRoles`

Stores the available user roles.

```text
Tref_UserRoles
├── RoleID PK
├── Name
├── InsertUsername
├── InsertDate
├── ChangeUsername
└── ChangeDate
```

Example values:

```text
admin
director
secretary
professor
```

Relationship:

```text
Tref_UserRoles 1 ─── N Tbl_Users
```

Purpose:

This table avoids storing role names directly inside `Tbl_Users`. Instead, each user references a role using `RoleID`.

---

### 4.2. `Tref_Gender`

Stores gender reference values.

```text
Tref_Gender
├── GenderID PK
├── Name
├── InsertUsername
├── InsertDate
├── ChangeUsername
└── ChangeDate
```

Example values:

```text
Male
Female
Other
```

Relationships:

```text
Tref_Gender 1 ─── N Tbl_Students
Tref_Gender 1 ─── N Tbl_Professors
```

Purpose:

This table keeps gender values consistent instead of allowing free text in students and professors.

---

### 4.3. `Tref_SchoolYears`

Stores school years.

```text
Tref_SchoolYears
├── SchoolYearID PK
├── Name
├── StartDate
├── EndDate
├── InsertUsername
├── InsertDate
├── ChangeUsername
└── ChangeDate
```

Example values:

```text
2025/2026
2026/2027
```

Relationships:

```text
Tref_SchoolYears 1 ─── N Tbl_Classes
Tref_SchoolYears 1 ─── N Tbl_SchoolCalendar
Tref_SchoolYears 1 ─── N Tbl_TeacherAvailability
Tref_SchoolYears 1 ─── N trx_Discipline_CourseYear
```

Purpose:

This table makes it possible to manage data by academic year.

---

## 5. Main Data Tables

---

### 5.1. `Tbl_Users`

Stores users who can authenticate into the system.

```text
Tbl_Users
├── UserID PK
├── FullName
├── Email
├── PasswordHash
├── RoleID FK
├── InsertUsername
├── InsertDate
├── ChangeUsername
└── ChangeDate
```

Relationships:

```text
Tref_UserRoles 1 ─── N Tbl_Users
Tbl_Users 1 ─── 0..1 Tbl_Professors
```

Purpose:

This table stores login and identity information.

Important note:

Professor name and email are stored in `Tbl_Users`, not in `Tbl_Professors`. This avoids duplicating the same data in two places.

Example users:

```text
System Administrator
Laura Mendes
Rita Almeida
Miguel Ramos
Inês Duarte
Pedro Neves
```

---

### 5.2. `Tbl_Courses`

Stores training programmes.

```text
Tbl_Courses
├── CourseID PK
├── Code
├── Name
├── InsertUsername
├── InsertDate
├── ChangeUsername
└── ChangeDate
```

Example values:

```text
TGEI
TGPSI
TCIB
```

Relationships:

```text
Tbl_Courses 1 ─── N Tbl_Classes
Tbl_Courses 1 ─── N trx_Discipline_CourseYear
```

Purpose:

A course represents the general academic programme, not a specific student group.

---

### 5.3. `Tbl_Classes`

Stores student groups for a specific course and school year.

```text
Tbl_Classes
├── ClassID PK
├── Name
├── CourseID FK
├── SchoolYearID FK
├── CourseYearNumber
├── InsertUsername
├── InsertDate
├── ChangeUsername
└── ChangeDate
```

Example values:

```text
TGEI 1A
TGEI 2A
TGPSI 1A
TCIB 2A
```

Relationships:

```text
Tbl_Courses 1 ─── N Tbl_Classes
Tref_SchoolYears 1 ─── N Tbl_Classes
Tbl_Classes 1 ─── N Tbl_Students
Tbl_Classes 1 ─── N Tbl_GeneratedSchedule
```

Purpose:

A class represents a specific group of students in a course and school year.

Example:

```text
Class: TGEI 1A
Course: TGEI
School year: 2025/2026
Course year number: 1
```

---

### 5.4. `Tbl_Students`

Stores student information.

```text
Tbl_Students
├── StudentID PK
├── FullName
├── StudentNumber
├── CardUID
├── ClassID FK
├── PhotoPath
├── GenderID FK
├── Address
├── PostalCode
├── City
├── Contact
├── DateOfBirth
├── InsertUsername
├── InsertDate
├── ChangeUsername
└── ChangeDate
```

Relationships:

```text
Tbl_Classes 1 ─── N Tbl_Students
Tref_Gender 1 ─── N Tbl_Students
Tbl_Students 1 ─── N Tbl_AttendanceRecords
```

Purpose:

This table stores student personal and school-related data.

Important fields:

- `StudentNumber`: student identifier
- `CardUID`: NFC/RFID card identifier
- `ClassID`: links the student to a class
- `GenderID`: links the student to the gender reference table

---

### 5.5. `Tbl_Professors`

Stores professor-specific information.

```text
Tbl_Professors
├── ProfessorID PK
├── UserID FK
├── PhotoPath
├── GenderID FK
├── Address
├── PostalCode
├── City
├── Contact
├── DateOfBirth
├── InsertUsername
├── InsertDate
├── ChangeUsername
└── ChangeDate
```

Relationships:

```text
Tbl_Users 1 ─── 0..1 Tbl_Professors
Tref_Gender 1 ─── N Tbl_Professors
Tbl_Professors 1 ─── N Tbl_TeacherAvailability
Tbl_Professors 1 ─── N Tbl_GeneratedSchedule
Tbl_Professors N ─── N trx_Discipline_CourseYear through trx_Professor_DisciplineCourseYear
```

Purpose:

This table stores professor-specific data.

Important note:

`Tbl_Professors` does not store `FullName` or `Email`. Those fields come from `Tbl_Users`.

This avoids redundancy.

---

### 5.6. `Tbl_Disciplines`

Stores the general discipline catalogue.

```text
Tbl_Disciplines
├── DisciplineID PK
├── Name
├── Code
├── InsertUsername
├── InsertDate
├── ChangeUsername
└── ChangeDate
```

Example values:

```text
Programming
Networks
Databases
Operating Systems
Mathematics
```

Relationship:

```text
Tbl_Disciplines 1 ─── N trx_Discipline_CourseYear
```

Purpose:

This table stores only the general discipline information.

Important note:

This table does not store:

- Total hours
- Lesson duration
- Practical flag

Those values are stored in `trx_Discipline_CourseYear`, because they can change depending on course and school year.

---

### 5.7. `Tbl_Rooms`

Stores school rooms.

```text
Tbl_Rooms
├── RoomID PK
├── Name
├── Capacity
├── IsPracticeRoom
├── Location
├── InsertUsername
├── InsertDate
├── ChangeUsername
└── ChangeDate
```

Relationships:

```text
Tbl_Rooms 1 ─── N Tbl_GeneratedSchedule
```

Purpose:

This table stores rooms that can be used in the schedule.

Important fields:

- `Capacity`: maximum number of students
- `IsPracticeRoom`: indicates whether the room can be used for practical disciplines
- `Location`: physical location of the room

---

### 5.8. `Tbl_SchoolCalendar`

Stores school calendar dates.

```text
Tbl_SchoolCalendar
├── CalendarID PK
├── SchoolYearID FK
├── CalendarDate
├── IsSchoolDay
├── Description
├── InsertUsername
├── InsertDate
├── ChangeUsername
└── ChangeDate
```

Example values:

```text
2025-09-15 | School day
2025-12-25 | Christmas holiday
2026-01-01 | New year holiday
```

Relationships:

```text
Tref_SchoolYears 1 ─── N Tbl_SchoolCalendar
Tbl_SchoolCalendar 1 ─── N Tbl_GeneratedSchedule
```

Purpose:

This table allows the system to know whether a date is a school day or not.

This is important for schedule validation.

---

### 5.9. `Tbl_TeacherAvailability`

Stores teacher availability by school year.

```text
Tbl_TeacherAvailability
├── TeacherAvailabilityID PK
├── ProfessorID FK
├── SchoolYearID FK
├── DayOfWeek
├── StartTime
├── EndTime
├── InsertUsername
├── InsertDate
├── ChangeUsername
└── ChangeDate
```

Relationships:

```text
Tbl_Professors 1 ─── N Tbl_TeacherAvailability
Tref_SchoolYears 1 ─── N Tbl_TeacherAvailability
```

Purpose:

This table stores when each professor is available during a school year.

Allowed `DayOfWeek` values:

```text
monday
tuesday
wednesday
thursday
friday
```

---

### 5.10. `Tbl_GeneratedSchedule`

Stores generated or manually created schedule records.

```text
Tbl_GeneratedSchedule
├── ScheduleID PK
├── ClassID FK
├── DisciplineCourseYearID FK
├── ProfessorID FK
├── RoomID FK
├── CalendarID FK
├── StartTime
├── EndTime
├── Status
├── InsertUsername
├── InsertDate
├── ChangeUsername
└── ChangeDate
```

Relationships:

```text
Tbl_Classes 1 ─── N Tbl_GeneratedSchedule
trx_Discipline_CourseYear 1 ─── N Tbl_GeneratedSchedule
Tbl_Professors 1 ─── N Tbl_GeneratedSchedule
Tbl_Rooms 1 ─── N Tbl_GeneratedSchedule
Tbl_SchoolCalendar 1 ─── N Tbl_GeneratedSchedule
Tbl_GeneratedSchedule 1 ─── N Tbl_AttendanceRecords
```

Purpose:

This table stores schedule records.

Important note:

`Tbl_GeneratedSchedule` uses `DisciplineCourseYearID`, not `DisciplineID`.

This means each schedule record points to a discipline configured for a specific course, school year and course year.

Allowed `Status` values:

```text
draft
approved
cancelled
```

---

### 5.11. `Tbl_AttendanceRecords`

Stores student attendance punches.

```text
Tbl_AttendanceRecords
├── AttendanceRecordID PK
├── StudentID FK
├── ScheduleID FK
├── PunchType
├── PunchMethod
├── PunchTime
├── IsSynced
├── InsertUsername
├── InsertDate
├── ChangeUsername
└── ChangeDate
```

Relationships:

```text
Tbl_Students 1 ─── N Tbl_AttendanceRecords
Tbl_GeneratedSchedule 1 ─── N Tbl_AttendanceRecords
```

Purpose:

This table stores attendance registrations for students.

Allowed `PunchType` values:

```text
in
out
```

Allowed `PunchMethod` values:

```text
nfc
rfid
qr
barcode
manual
```

---

## 6. Relationship Tables

---

### 6.1. `trx_Discipline_CourseYear`

Stores the workload configuration of a discipline for a specific course and school year.

```text
trx_Discipline_CourseYear
├── DisciplineCourseYearID PK
├── DisciplineID FK
├── CourseID FK
├── SchoolYearID FK
├── CourseYearNumber
├── TotalMinutes
├── LessonDurationMinutes
├── IsPractical
├── InsertUsername
├── InsertDate
├── ChangeUsername
└── ChangeDate
```

Example:

```text
Programming
Course: TGEI
School year: 2025/2026
Course year number: 1
Total minutes: 7200
Lesson duration: 60
Practical: true
```

Relationships:

```text
Tbl_Disciplines 1 ─── N trx_Discipline_CourseYear
Tbl_Courses 1 ─── N trx_Discipline_CourseYear
Tref_SchoolYears 1 ─── N trx_Discipline_CourseYear
trx_Discipline_CourseYear 1 ─── N Tbl_GeneratedSchedule
trx_Discipline_CourseYear N ─── N Tbl_Professors through trx_Professor_DisciplineCourseYear
```

Purpose:

This table is one of the most important parts of the model.

It allows the same discipline to have different workloads depending on:

- Course
- School year
- Course year number

Example:

```text
Programming in TGEI Year 1 may have 7200 minutes.
Programming in TGPSI Year 1 may have 8400 minutes.
```

---

### 6.2. `trx_Professor_DisciplineCourseYear`

Assigns professors to specific discipline-course-year records.

```text
trx_Professor_DisciplineCourseYear
├── ProfessorID PK FK
├── DisciplineCourseYearID PK FK
├── InsertUsername
├── InsertDate
├── ChangeUsername
└── ChangeDate
```

Example:

```text
Professor: Miguel Ramos
Discipline configuration: Programming - TGEI - 2025/2026 - Year 1
```

Relationships:

```text
Tbl_Professors 1 ─── N trx_Professor_DisciplineCourseYear
trx_Discipline_CourseYear 1 ─── N trx_Professor_DisciplineCourseYear
```

Purpose:

This table allows the system to know which professor can teach which discipline configuration.

This is more precise than only saying:

```text
Professor teaches Programming
```

The new model says:

```text
Professor teaches Programming for TGEI in 2025/2026, Year 1
```

---

## 7. Schedule Validation Rules

Before creating or updating a schedule record, the backend validates several business rules.

The schedule validation checks that:

- The class exists.
- The discipline course year record exists.
- The professor exists.
- The room exists.
- The calendar record exists.
- The calendar date is a school day.
- The class course matches the discipline course.
- The class school year matches the discipline school year.
- The class course year number matches the discipline course year number.
- The professor is assigned to the selected discipline course year.
- Practical disciplines are scheduled in practice rooms.
- A class cannot have overlapping lessons.
- A professor cannot have overlapping lessons.
- A room cannot have overlapping lessons.

These validations are implemented in the schedule router.

---

## 8. Attendance Model

Attendance records are linked to:

- A student
- An optional schedule record
- A punch type
- A punch method
- A punch time

Example attendance record:

```text
Student: João Pereira
Schedule: Programming - 2025-09-15 - 09:00
Punch type: in
Punch method: nfc
Punch time: 2025-09-15 08:58:00
```

The `ScheduleID` field can be nullable, which allows manual or general attendance records if needed.

---

## 9. Demo Data

The `seed.sql` file inserts demo data for:

- User roles
- Genders
- School years
- Courses
- Classes
- Users
- Professors
- Students
- Disciplines
- Discipline workload configurations
- Professor assignments
- Rooms
- School calendar
- Teacher availability
- Schedule records
- Attendance records

Demo users are inserted without passwords in `seed.sql`.

Passwords are generated later by running:

```bash
python create_demo_passwords.py
```

---

## 10. Demo Login Users

After running `create_demo_passwords.py`, these demo users can be used:

| Role | Email | Password |
|---|---|---|
| Admin | `admin@academia360.local` | `admin` |
| Director | `laura.mendes@academia360.local` | `director` |
| Secretary | `rita.almeida@academia360.local` | `secretary` |
| Professor | `miguel.ramos@academia360.local` | `professor` |
| Professor | `ines.duarte@academia360.local` | `professor` |
| Professor | `pedro.neves@academia360.local` | `professor` |

---

## 11. Current Limitations

The current database and backend are functional, but there are still improvements to be made:

- Large list endpoints do not have pagination yet.
- Some helper functions are duplicated across routers.
- `UserCreate` should be improved so the frontend sends `password` instead of `password_hash`.
- The automatic schedule generation algorithm is not implemented yet.
- The current schedule endpoint validates manual schedule creation but does not generate complete schedules automatically.
- More indexes may be needed later for performance.

---

## 12. Recommended Future Improvements

Recommended next database/backend improvements:

1. Add pagination to large endpoints such as `/attendance`.
2. Add indexes for frequently queried fields.
3. Refactor repeated helper functions into `utils.py`.
4. Improve user creation so passwords are hashed automatically.
5. Add automatic schedule generation.
6. Define hard and soft constraints for schedule generation.
7. Add more reporting queries for attendance and absences.
8. Add dashboard-oriented endpoints.

---

## 13. Final Summary

The current database model provides a solid foundation for Academia360.

It supports:

- Role-based users
- Professors linked to users
- Students linked to classes
- Classes linked to courses and school years
- Disciplines separated from workload configuration
- Professors assigned to specific discipline-course-year records
- Rooms with practical-room support
- School calendar with school-day validation
- Teacher availability by school year
- Schedule records with conflict validation
- Attendance records linked to students and schedules

The next major technical challenge is the automatic schedule generation algorithm.