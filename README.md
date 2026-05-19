# Academia360 API

Academia360 is a backend API developed with FastAPI and MySQL for managing school attendance, schedules, courses, classes, rooms, students, professors and teacher availability.

This project is part of the Academia360 Erasmus+ internship work.

---

## Technologies Used

- Python
- FastAPI
- MySQL
- mysql-connector-python
- Uvicorn
- Pydantic
- JWT authentication
- python-jose
- passlib
- python-dotenv

---

## Project Objective

The objective of Academia360 is to provide a backend foundation for a school management platform focused on:

- Student attendance registration
- NFC/RFID/QR/barcode/manual attendance punching
- School schedule management
- Teacher availability management
- Course and class management
- Room management
- Discipline workload configuration
- School calendar management
- Role-based access control

---

## Current Features

The current backend includes:

- Normalized MySQL database schema
- Table naming convention using `Tbl_`, `Tref_` and `trx_`
- Audit columns in all tables
- Demo seed data
- SQL test queries
- CRUD routers for the main entities
- JWT authentication
- Role-based route protection
- Swagger API documentation
- `/auth/me` endpoint to verify the authenticated user
- Shared utility functions in `utils.py`
- Schedule validation logic
- Attendance registration logic

---

## Authentication

The API uses JWT authentication.

Login endpoint:

```text
POST /auth/login
```

Swagger uses OAuth2. In Swagger, the recommended login method is to use the **Authorize** button at the top of the page.

In the Swagger login form, the field is called `username`, but the backend expects the user's email.

Example:

```text
username: admin@academia360.local
password: admin
```

Leave these fields empty:

```text
client_id
client_secret
```

After login, Swagger stores the Bearer token automatically and uses it to access protected endpoints.

---

## Demo Login Users

After running:

```bash
python create_demo_passwords.py
```

these demo users can be used for testing:

| Role | Email | Password |
|---|---|---|
| Admin | `admin@academia360.local` | `admin` |
| Director | `laura.mendes@academia360.local` | `director` |
| Secretary | `rita.almeida@academia360.local` | `secretary` |
| Professor | `daniel.martins@academia360.local` | `professor` |
| Professor | `ana.costa@academia360.local` | `professor` |
| Professor | `carlos.ferreira@academia360.local` | `professor` |

Recommended first login for testing:

```text
username: admin@academia360.local
password: admin
```

---

## Authentication Test

After logging in through Swagger, the authenticated user can be checked with:

```text
GET /auth/me
```

Expected response example:

```json
{
  "user_id": 1,
  "full_name": "System Administrator",
  "email": "admin@academia360.local",
  "role": "admin"
}
```

If the request is made without a valid token, protected routes should return:

```json
{
  "detail": "Not authenticated"
}
```

---

## Database Naming Convention

The database uses prefixes to quickly identify the purpose of each table.

| Prefix | Meaning | Example |
|---|---|---|
| `Tbl_` | Main data table | `Tbl_Students` |
| `Tref_` | Reference table / fixed list | `Tref_UserRoles` |
| `trx_` | Relationship table | `trx_Discipline_CourseYear` |

---

## Audit Columns

All tables include audit columns:

```text
InsertUsername
InsertDate
ChangeUsername
ChangeDate
```

These fields store:

- The user who inserted the record
- The insertion date
- The user who last modified the record
- The last modification date

---

## Main Database Tables

### Reference Tables

```text
Tref_UserRoles
Tref_Gender
Tref_SchoolYears
```

### Main Data Tables

```text
Tbl_Users
Tbl_Courses
Tbl_Classes
Tbl_Students
Tbl_Professors
Tbl_Disciplines
Tbl_Rooms
Tbl_SchoolCalendar
Tbl_TeacherAvailability
Tbl_GeneratedSchedule
Tbl_AttendanceRecords
```

### Relationship Tables

```text
trx_Discipline_CourseYear
trx_Professor_DisciplineCourseYear
```

---

## Important Database Design Decisions

### Users and Professors

Professor name and email are stored in `Tbl_Users`.

`Tbl_Professors` only stores professor-specific information such as:

```text
UserID
PhotoPath
GenderID
Address
PostalCode
City
Contact
DateOfBirth
```

This avoids duplicating name and email in both `Tbl_Users` and `Tbl_Professors`.

---

### Courses, Classes and School Years

Courses and classes are separated.

A course represents the general training programme, for example:

```text
TGEI
TGPSI
TCIB
```

A class represents a student group inside a course and school year, for example:

```text
TGEI 1A
TGEI 2A
TGPSI 1A
TCIB 2A
```

---

### Disciplines and Workload

Disciplines are stored as a general catalogue in `Tbl_Disciplines`.

Examples:

```text
Programming
Networks
Databases
Operating Systems
Mathematics
```

The workload of a discipline is not stored directly in `Tbl_Disciplines` because it can change depending on:

- Course
- School year
- Course year number

For that reason, the table `trx_Discipline_CourseYear` stores the workload configuration.

Example:

```text
Programming
Course: TGEI
School year: 2025/2026
Course year number: 1
Total minutes: 7200
Lesson duration: 60 minutes
Practical: true
```

---

### Schedule Model

The schedule table does not point directly to `Tbl_Disciplines`.

Instead, `Tbl_GeneratedSchedule` points to `trx_Discipline_CourseYear`.

This allows each schedule record to know the exact course, school year, course year number, workload and practical configuration of the discipline.

---

## Schedule Validation Rules

Before creating or updating a schedule record, the backend validates:

- The class exists.
- The discipline course year record exists.
- The professor exists.
- The room exists.
- The calendar date exists.
- The calendar date is a school day.
- The class and discipline belong to the same course.
- The class and discipline belong to the same school year.
- The class and discipline have the same course year number.
- The professor is assigned to the selected discipline course year.
- Practical disciplines are scheduled in practice rooms.
- There are no overlapping schedule records for the class.
- There are no overlapping schedule records for the professor.
- There are no overlapping schedule records for the room.

---

## Backend Structure

```text
backend/
├── app.py
├── auth.py
├── db.py
├── models.py
├── utils.py
├── requirements.txt
├── create_demo_passwords.py
│
└── routers/
    ├── __init__.py
    ├── auth_routes.py
    ├── attendance.py
    ├── classes.py
    ├── courses.py
    ├── discipline_course_years.py
    ├── disciplines.py
    ├── genders.py
    ├── professor_discipline_course_years.py
    ├── professors.py
    ├── roles.py
    ├── rooms.py
    ├── schedule.py
    ├── school_calendar.py
    ├── school_years.py
    ├── students.py
    ├── teacher_availability.py
    └── users.py
```

---

## Shared Utilities

The backend includes a shared `utils.py` file.

This file centralizes helper functions that were previously duplicated across routers.

Current shared helpers:

```python
get_audit_username(current_user)
model_to_dict(model)
```

This improves maintainability because common logic is now defined in one place instead of being repeated in multiple router files.

---

## Database Files

The database files are located in the `database` folder.

```text
database/
├── schema.sql
├── seed.sql
└── queries.sql
```

---

### schema.sql

Creates the database structure.

It includes:

- Database creation
- Table creation
- Foreign keys
- Constraints
- Audit columns
- Table prefixes

---

### seed.sql

Inserts demo data for testing.

It includes:

- Roles
- Genders
- School years
- Courses
- Classes
- Users
- Professors
- Students
- Rooms
- Disciplines
- Discipline workload configurations
- Professor assignments
- Teacher availability
- School calendar records
- Generated schedules
- Attendance records

---

### queries.sql

Contains useful SQL queries to test and inspect the database.

It includes queries for:

- Users
- Students
- Professors
- Courses
- Classes
- Rooms
- Disciplines
- Schedule records
- Attendance records
- Room occupation
- Attendance summaries
- Schedule conflicts
- Audit fields
- Foreign key relationships

---

## Available API Endpoints

### Health Check

```text
GET /
```

### Authentication

```text
POST /auth/login
GET  /auth/me
```

### Roles

```text
GET    /roles
GET    /roles/{role_id}
POST   /roles
PUT    /roles/{role_id}
DELETE /roles/{role_id}
```

### Genders

```text
GET    /genders
GET    /genders/{gender_id}
POST   /genders
PUT    /genders/{gender_id}
DELETE /genders/{gender_id}
```

### School Years

```text
GET    /school-years
GET    /school-years/{school_year_id}
POST   /school-years
PUT    /school-years/{school_year_id}
DELETE /school-years/{school_year_id}
```

### Courses

```text
GET    /courses
GET    /courses/{course_id}
POST   /courses
PUT    /courses/{course_id}
DELETE /courses/{course_id}
```

### Classes

```text
GET    /classes
GET    /classes/{class_id}
POST   /classes
PUT    /classes/{class_id}
DELETE /classes/{class_id}
```

### Users

```text
GET    /users
GET    /users/{user_id}
POST   /users
PUT    /users/{user_id}
DELETE /users/{user_id}
```

### Professors

```text
GET    /professors
GET    /professors/{professor_id}
POST   /professors
PUT    /professors/{professor_id}
DELETE /professors/{professor_id}
```

### Students

```text
GET    /students
GET    /students/{student_id}
POST   /students
PUT    /students/{student_id}
DELETE /students/{student_id}
```

### Rooms

```text
GET    /rooms
GET    /rooms/{room_id}
POST   /rooms
PUT    /rooms/{room_id}
DELETE /rooms/{room_id}
```

### Disciplines

```text
GET    /disciplines
GET    /disciplines/{discipline_id}
POST   /disciplines
PUT    /disciplines/{discipline_id}
DELETE /disciplines/{discipline_id}
```

### Discipline Course Years

```text
GET    /discipline-course-years
GET    /discipline-course-years/{discipline_course_year_id}
POST   /discipline-course-years
PUT    /discipline-course-years/{discipline_course_year_id}
DELETE /discipline-course-years/{discipline_course_year_id}
```

### Professor Discipline Course Years

```text
GET    /professor-discipline-course-years
GET    /professor-discipline-course-years/professor/{professor_id}
GET    /professor-discipline-course-years/discipline-course-year/{discipline_course_year_id}
GET    /professor-discipline-course-years/{professor_id}/{discipline_course_year_id}
POST   /professor-discipline-course-years
DELETE /professor-discipline-course-years/{professor_id}/{discipline_course_year_id}
```

### Teacher Availability

```text
GET    /teacher-availability
GET    /teacher-availability/{availability_id}
GET    /teacher-availability/professor/{professor_id}
POST   /teacher-availability
PUT    /teacher-availability/{availability_id}
DELETE /teacher-availability/{availability_id}
```

### School Calendar

```text
GET    /school-calendar
GET    /school-calendar/{calendar_id}
GET    /school-calendar/school-year/{school_year_id}
POST   /school-calendar
PUT    /school-calendar/{calendar_id}
DELETE /school-calendar/{calendar_id}
```

### Schedule

```text
GET    /schedule
GET    /schedule/{schedule_id}
GET    /schedule/class/{class_id}
GET    /schedule/professor/{professor_id}
GET    /schedule/room/{room_id}
POST   /schedule
PUT    /schedule/{schedule_id}
DELETE /schedule/{schedule_id}
```

### Attendance

```text
GET    /attendance
GET    /attendance/{attendance_id}
GET    /attendance/student/{student_id}
GET    /attendance/schedule/{schedule_id}
POST   /attendance
PUT    /attendance/{attendance_id}
DELETE /attendance/{attendance_id}
```

---

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Go to the backend folder

```bash
cd backend
```

### 3. Create a virtual environment

```bash
py -m venv .venv
```

### 4. Activate the virtual environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Windows CMD:

```cmd
.venv\Scripts\activate
```

### 5. Install dependencies

```bash
python -m pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file inside the `backend` folder.

Example:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=academia360
DB_PORT=3306
SECRET_KEY=academia360-dev-secret-key
```

There is also a `.env.example` file that can be used as a template.

Important:

```text
.env must not be committed to GitHub.
```

---

## Database Setup

### 1. Start MySQL

Start MySQL using XAMPP or your local MySQL installation.

### 2. Create the database schema

Import or execute:

```text
database/schema.sql
```

### 3. Insert demo data

Import or execute:

```text
database/seed.sql
```

### 4. Generate demo passwords

From the backend folder, run:

```bash
python create_demo_passwords.py
```

This will generate hashed passwords for the demo users.

### 5. Optional: test database queries

Import or execute:

```text
database/queries.sql
```

This file helps verify that the database structure and relationships are working correctly.

---

## Running the API

From inside the backend folder, run:

```bash
python -m uvicorn app:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation will be available at:

```text
http://127.0.0.1:8000/docs
```

---

## Swagger Login Flow

Open Swagger:

```text
http://127.0.0.1:8000/docs
```

Click the **Authorize** button.

Use one of the demo users.

Example:

```text
username: admin@academia360.local
password: admin
```

Leave empty:

```text
client_id
client_secret
```

Click **Authorize** and then **Close**.

Then test protected endpoints.

---

## Recommended Swagger Test Order

Recommended order for testing:

```text
GET /
Authorize with admin user
GET /auth/me
GET /roles
GET /genders
GET /school-years
GET /courses
GET /classes
GET /users
GET /professors
GET /students
GET /rooms
GET /disciplines
GET /discipline-course-years
GET /professor-discipline-course-years
GET /teacher-availability
GET /school-calendar
GET /schedule
GET /attendance
```

---

## Example Requests

### Create a Course

```json
{
  "code": "WEBDEV",
  "name": "Web Development Technician"
}
```

### Create a Class

```json
{
  "name": "TGEI 1B",
  "course_id": 1,
  "school_year_id": 1,
  "course_year_number": 1
}
```

### Create a Student

```json
{
  "full_name": "Test Student",
  "student_number": "STU999",
  "card_uid": "CARD999",
  "class_id": 1,
  "photo_path": null,
  "gender_id": 1,
  "address": "Rua Teste 99",
  "postal_code": "4590-999",
  "city": "Paços de Ferreira",
  "contact": "929999999",
  "date_of_birth": "2008-01-10"
}
```

### Create a Professor

```json
{
  "user_id": 4,
  "photo_path": null,
  "gender_id": 1,
  "address": "Rua das Flores 12",
  "postal_code": "4590-111",
  "city": "Paços de Ferreira",
  "contact": "910000001",
  "date_of_birth": "1985-03-12"
}
```

### Create a Discipline

```json
{
  "name": "Cybersecurity",
  "code": "CYBER"
}
```

### Create a Discipline Course Year

```json
{
  "discipline_id": 1,
  "course_id": 1,
  "school_year_id": 1,
  "course_year_number": 1,
  "total_minutes": 7200,
  "lesson_duration_minutes": 60,
  "is_practical": true
}
```

### Assign a Professor to a Discipline Course Year

```json
{
  "professor_id": 1,
  "discipline_course_year_id": 1
}
```

### Create a Room

```json
{
  "name": "Computer Lab 3",
  "capacity": 25,
  "is_practice_room": true,
  "location": "Main building - Third floor"
}
```

### Create a School Calendar Record

```json
{
  "school_year_id": 1,
  "calendar_date": "2026-05-18",
  "is_school_day": true,
  "description": "Test school day"
}
```

### Create Teacher Availability

```json
{
  "professor_id": 1,
  "school_year_id": 1,
  "day_of_week": "monday",
  "start_time": "09:00:00",
  "end_time": "13:00:00"
}
```

Allowed values for `day_of_week`:

```text
monday
tuesday
wednesday
thursday
friday
```

### Create a Schedule Record

```json
{
  "class_id": 1,
  "discipline_course_year_id": 1,
  "professor_id": 1,
  "room_id": 2,
  "calendar_id": 2,
  "start_time": "10:00:00",
  "end_time": "11:00:00",
  "status": "approved"
}
```

Allowed values for `status`:

```text
draft
approved
cancelled
```

### Create an Attendance Record

```json
{
  "student_id": 1,
  "schedule_id": 1,
  "punch_type": "in",
  "punch_method": "nfc",
  "is_synced": true
}
```

Allowed values for `punch_type`:

```text
in
out
```

Allowed values for `punch_method`:

```text
nfc
rfid
qr
barcode
manual
```

---

## Current Limitations

The current version still has some limitations:

- Large list endpoints do not have pagination yet.
- `UserCreate` should be improved so the frontend sends `password` instead of `password_hash`.
- The automatic schedule generation algorithm is not implemented yet.
- The current schedule endpoint validates manual schedule creation but does not generate complete schedules automatically.
- Current credentials are demo credentials and are only suitable for local development/testing.

---

## Recommended Next Steps

Recommended next development steps:

1. Test all endpoints in Swagger.
2. Update `UserCreate` to accept `password` instead of `password_hash`.
3. Hash user passwords inside the backend when creating or updating users.
4. Add pagination to large list endpoints such as `/attendance`.
5. Update the database documentation if the schema changes again.
6. Update the ER diagram if new relationships are added.
7. Start designing the automatic schedule generation algorithm.
8. Define hard and soft constraints for schedule generation.

---

## Git Ignore Recommendation

The following files and folders should not be pushed to GitHub:

```text
.venv/
backend/.venv/
.env
backend/.env
__pycache__/
*.pyc
```

---

## Notes

This backend is currently focused on creating a solid database and API foundation before developing the frontend and the automatic schedule generation algorithm.

The current authentication system uses JWT tokens and hashed passwords for demo users. This is suitable for local development and testing, but production deployment would require stronger credentials, a secure `SECRET_KEY`, HTTPS and a final review of user creation and role permissions.