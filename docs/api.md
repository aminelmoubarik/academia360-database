# Academia360 API Documentation

This document describes the main API endpoints available in the Academia360 backend.

Base URL during local development:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

## 1. Authentication

The API uses JWT authentication with role-based access control.

Login is handled with:

```text
POST /auth/login
```

Swagger uses OAuth2. In the Swagger login form, the field is called `username`, but the backend expects the user's email.

Example:

```text
username: admin@academia360.local
password: admin
```

After login, the API returns a JWT access token.

Example response:

```json
{
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

The token can be used in Swagger through the **Authorize** button.

---

## 2. Demo Login Users

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
| Professor | `miguel.ramos@academia360.local` | `professor` |
| Professor | `ines.duarte@academia360.local` | `professor` |
| Professor | `pedro.neves@academia360.local` | `professor` |

Recommended first login for testing:

```text
username: admin@academia360.local
password: admin
```

---

## 3. Health Check

### GET `/`

Checks if the API is running.

Response:

```json
{
  "message": "Academia360 API is running"
}
```

---

## 4. Authentication Endpoints

---

### POST `/auth/login`

Authenticates a user and returns a JWT token.

Request type:

```text
Form Data
```

Fields:

```text
username: user email
password: user password
```

Example:

```text
username: admin@academia360.local
password: admin
```

Response:

```json
{
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

---

### GET `/auth/me`

Basic authentication-related endpoint.

Current response:

```json
{
  "message": "Use the Authorize button with your token to access protected routes"
}
```

---

## 5. Roles

Roles are stored in:

```text
Tref_UserRoles
```

Available default roles:

```text
admin
director
secretary
professor
```

---

### GET `/roles`

Returns all roles.

Example response:

```json
[
  {
    "id": 1,
    "name": "admin",
    "insert_username": "seed",
    "insert_date": "2026-05-15T10:00:00",
    "change_username": null,
    "change_date": null
  }
]
```

---

### GET `/roles/{role_id}`

Returns one role by ID.

Example:

```text
GET /roles/1
```

---

### POST `/roles`

Creates a new role.

Request:

```json
{
  "name": "coordinator"
}
```

---

### PUT `/roles/{role_id}`

Updates an existing role.

Request:

```json
{
  "name": "academic_coordinator"
}
```

---

### DELETE `/roles/{role_id}`

Deletes a role.

A role cannot be deleted if it is being used by users.

---

## 6. Genders

Genders are stored in:

```text
Tref_Gender
```

Default values:

```text
Male
Female
Other
```

---

### GET `/genders`

Returns all genders.

---

### GET `/genders/{gender_id}`

Returns one gender by ID.

Example:

```text
GET /genders/1
```

---

### POST `/genders`

Creates a new gender value.

Request:

```json
{
  "name": "Male"
}
```

---

### PUT `/genders/{gender_id}`

Updates a gender value.

Request:

```json
{
  "name": "Female"
}
```

---

### DELETE `/genders/{gender_id}`

Deletes a gender value.

A gender cannot be deleted if it is being used by students or professors.

---

## 7. School Years

School years are stored in:

```text
Tref_SchoolYears
```

---

### GET `/school-years`

Returns all school years.

---

### GET `/school-years/{school_year_id}`

Returns one school year by ID.

Example:

```text
GET /school-years/1
```

---

### POST `/school-years`

Creates a new school year.

Request:

```json
{
  "name": "2027/2028",
  "start_date": "2027-09-01",
  "end_date": "2028-07-31"
}
```

Validation:

```text
end_date must be greater than start_date
```

---

### PUT `/school-years/{school_year_id}`

Updates a school year.

Request:

```json
{
  "name": "2027/2028",
  "start_date": "2027-09-01",
  "end_date": "2028-07-31"
}
```

---

### DELETE `/school-years/{school_year_id}`

Deletes a school year.

A school year cannot be deleted if it is being used by classes, calendar records, teacher availability or discipline configurations.

---

## 8. Courses

Courses are stored in:

```text
Tbl_Courses
```

Examples:

```text
TGEI
TGPSI
TCIB
```

---

### GET `/courses`

Returns all courses.

Example response:

```json
[
  {
    "id": 1,
    "code": "TGEI",
    "name": "Técnico de Gestão de Equipamentos Informáticos"
  }
]
```

---

### GET `/courses/{course_id}`

Returns one course by ID.

Example:

```text
GET /courses/1
```

---

### POST `/courses`

Creates a new course.

Request:

```json
{
  "code": "WEBDEV",
  "name": "Web Development Technician"
}
```

---

### PUT `/courses/{course_id}`

Updates a course.

Request:

```json
{
  "code": "WEBDEV",
  "name": "Web Development Technician Updated"
}
```

---

### DELETE `/courses/{course_id}`

Deletes a course.

A course cannot be deleted if it is being used by classes or discipline-course-year records.

---

## 9. Classes

Classes are stored in:

```text
Tbl_Classes
```

A class represents a specific student group inside a course and school year.

---

### GET `/classes`

Returns all classes with course and school year information.

---

### GET `/classes/{class_id}`

Returns one class by ID.

Example:

```text
GET /classes/1
```

---

### POST `/classes`

Creates a new class.

Request:

```json
{
  "name": "TGEI 1B",
  "course_id": 1,
  "school_year_id": 1,
  "course_year_number": 1
}
```

Validation:

```text
course_year_number must be greater than 0
```

---

### PUT `/classes/{class_id}`

Updates a class.

Request:

```json
{
  "name": "TGEI 1B",
  "course_id": 1,
  "school_year_id": 1,
  "course_year_number": 1
}
```

---

### DELETE `/classes/{class_id}`

Deletes a class.

A class cannot be deleted if it is being used by students or schedule records.

---

## 10. Users

Users are stored in:

```text
Tbl_Users
```

Users are linked to roles through:

```text
Tref_UserRoles
```

---

### GET `/users`

Returns all users with their roles.

Example response:

```json
[
  {
    "id": 1,
    "full_name": "System Administrator",
    "email": "admin@academia360.local",
    "role_id": 1,
    "role": "admin"
  }
]
```

---

### GET `/users/{user_id}`

Returns one user by ID.

Example:

```text
GET /users/1
```

---

### POST `/users`

Creates a new user.

Current request format:

```json
{
  "full_name": "Test User",
  "email": "test.user@academia360.local",
  "password_hash": null,
  "role_id": 3
}
```

Important note:

This endpoint should be improved later so the frontend sends `password` instead of `password_hash`.

Recommended future format:

```json
{
  "full_name": "Test User",
  "email": "test.user@academia360.local",
  "password": "test123",
  "role_id": 3
}
```

The backend should hash the password before saving it.

---

### PUT `/users/{user_id}`

Updates a user.

Request:

```json
{
  "full_name": "Test User Updated",
  "email": "test.user.updated@academia360.local",
  "role_id": 4
}
```

---

### DELETE `/users/{user_id}`

Deletes a user.

A user cannot be deleted if it is being used by a professor record.

---

## 11. Professors

Professors are stored in:

```text
Tbl_Professors
```

Professor name and email come from:

```text
Tbl_Users
```

---

### GET `/professors`

Returns all professors with user information.

---

### GET `/professors/{professor_id}`

Returns one professor by ID.

Example:

```text
GET /professors/1
```

---

### POST `/professors`

Creates a professor linked to an existing user.

Request:

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

Important:

The selected `user_id` should belong to a user with the `professor` role.

---

### PUT `/professors/{professor_id}`

Updates a professor.

Request:

```json
{
  "photo_path": null,
  "gender_id": 1,
  "address": "Rua Nova 20",
  "postal_code": "4590-111",
  "city": "Paços de Ferreira",
  "contact": "910000001",
  "date_of_birth": "1985-03-12"
}
```

---

### DELETE `/professors/{professor_id}`

Deletes a professor.

A professor cannot be deleted if used by schedules, teacher availability or discipline assignments.

---

## 12. Students

Students are stored in:

```text
Tbl_Students
```

Students are linked to classes through:

```text
ClassID
```

---

### GET `/students`

Returns all students with class, course, school year and gender information.

---

### GET `/students/{student_id}`

Returns one student by ID.

Example:

```text
GET /students/1
```

---

### POST `/students`

Creates a student.

Request:

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

Important fields:

```text
student_number must be unique
card_uid must be unique
```

---

### PUT `/students/{student_id}`

Updates a student.

Request:

```json
{
  "full_name": "Test Student Updated",
  "student_number": "STU999",
  "card_uid": "CARD999",
  "class_id": 1,
  "gender_id": 1,
  "city": "Paços de Ferreira"
}
```

---

### DELETE `/students/{student_id}`

Deletes a student.

A student cannot be deleted if used by attendance records.

---

## 13. Rooms

Rooms are stored in:

```text
Tbl_Rooms
```

---

### GET `/rooms`

Returns all rooms.

---

### GET `/rooms/{room_id}`

Returns one room by ID.

Example:

```text
GET /rooms/1
```

---

### POST `/rooms`

Creates a room.

Request:

```json
{
  "name": "Computer Lab 3",
  "capacity": 25,
  "is_practice_room": true,
  "location": "Main building - Third floor"
}
```

Validation:

```text
capacity must be null or greater than 0
```

---

### PUT `/rooms/{room_id}`

Updates a room.

Request:

```json
{
  "name": "Computer Lab 3",
  "capacity": 30,
  "is_practice_room": true,
  "location": "Main building - Third floor"
}
```

---

### DELETE `/rooms/{room_id}`

Deletes a room.

A room cannot be deleted if used by schedule records.

---

## 14. Disciplines

Disciplines are stored in:

```text
Tbl_Disciplines
```

This table stores only the general discipline catalogue.

---

### GET `/disciplines`

Returns all disciplines.

---

### GET `/disciplines/{discipline_id}`

Returns one discipline by ID.

Example:

```text
GET /disciplines/1
```

---

### POST `/disciplines`

Creates a discipline.

Request:

```json
{
  "name": "Cybersecurity",
  "code": "CYBER"
}
```

Important:

This endpoint does not store total hours, lesson duration or practical flag.

That information is stored in:

```text
/discipline-course-years
```

---

### PUT `/disciplines/{discipline_id}`

Updates a discipline.

Request:

```json
{
  "name": "Cybersecurity",
  "code": "CYBER"
}
```

---

### DELETE `/disciplines/{discipline_id}`

Deletes a discipline.

A discipline cannot be deleted if used by discipline-course-year records.

---

## 15. Discipline Course Years

Discipline course years are stored in:

```text
trx_Discipline_CourseYear
```

This table stores the workload of a discipline for a specific course and school year.

---

### GET `/discipline-course-years`

Returns all discipline-course-year records.

---

### GET `/discipline-course-years/{discipline_course_year_id}`

Returns one discipline-course-year record by ID.

Example:

```text
GET /discipline-course-years/1
```

---

### POST `/discipline-course-years`

Creates a discipline workload configuration.

Request:

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

Validation:

```text
course_year_number must be greater than 0
total_minutes must be greater than 0
lesson_duration_minutes must be greater than 0
```

---

### PUT `/discipline-course-years/{discipline_course_year_id}`

Updates a discipline workload configuration.

Request:

```json
{
  "total_minutes": 8000,
  "lesson_duration_minutes": 60,
  "is_practical": true
}
```

---

### DELETE `/discipline-course-years/{discipline_course_year_id}`

Deletes a discipline-course-year record.

It cannot be deleted if it is used by schedules or professor assignments.

---

## 16. Professor Discipline Course Years

Professor assignments are stored in:

```text
trx_Professor_DisciplineCourseYear
```

This table assigns professors to specific discipline-course-year configurations.

---

### GET `/professor-discipline-course-years`

Returns all professor assignments.

---

### GET `/professor-discipline-course-years/professor/{professor_id}`

Returns all discipline-course-year records assigned to one professor.

Example:

```text
GET /professor-discipline-course-years/professor/1
```

---

### GET `/professor-discipline-course-years/discipline-course-year/{discipline_course_year_id}`

Returns all professors assigned to one discipline-course-year record.

Example:

```text
GET /professor-discipline-course-years/discipline-course-year/1
```

---

### GET `/professor-discipline-course-years/{professor_id}/{discipline_course_year_id}`

Returns one professor assignment.

Example:

```text
GET /professor-discipline-course-years/1/1
```

---

### POST `/professor-discipline-course-years`

Assigns a professor to a discipline-course-year record.

Request:

```json
{
  "professor_id": 1,
  "discipline_course_year_id": 1
}
```

---

### DELETE `/professor-discipline-course-years/{professor_id}/{discipline_course_year_id}`

Deletes a professor assignment.

Example:

```text
DELETE /professor-discipline-course-years/1/1
```

---

## 17. Teacher Availability

Teacher availability records are stored in:

```text
Tbl_TeacherAvailability
```

---

### GET `/teacher-availability`

Returns all teacher availability records.

---

### GET `/teacher-availability/{availability_id}`

Returns one teacher availability record by ID.

Example:

```text
GET /teacher-availability/1
```

---

### GET `/teacher-availability/professor/{professor_id}`

Returns availability records for one professor.

Example:

```text
GET /teacher-availability/professor/1
```

---

### POST `/teacher-availability`

Creates a teacher availability record.

Request:

```json
{
  "professor_id": 1,
  "school_year_id": 1,
  "day_of_week": "monday",
  "start_time": "09:00:00",
  "end_time": "13:00:00"
}
```

Allowed `day_of_week` values:

```text
monday
tuesday
wednesday
thursday
friday
```

Validation:

```text
end_time must be greater than start_time
```

---

### PUT `/teacher-availability/{availability_id}`

Updates a teacher availability record.

Request:

```json
{
  "day_of_week": "tuesday",
  "start_time": "10:00:00",
  "end_time": "14:00:00"
}
```

---

### DELETE `/teacher-availability/{availability_id}`

Deletes a teacher availability record.

---

## 18. School Calendar

School calendar records are stored in:

```text
Tbl_SchoolCalendar
```

---

### GET `/school-calendar`

Returns all school calendar records.

---

### GET `/school-calendar/{calendar_id}`

Returns one calendar record by ID.

Example:

```text
GET /school-calendar/1
```

---

### GET `/school-calendar/school-year/{school_year_id}`

Returns calendar records for one school year.

Example:

```text
GET /school-calendar/school-year/1
```

---

### POST `/school-calendar`

Creates a school calendar record.

Request:

```json
{
  "school_year_id": 1,
  "calendar_date": "2026-05-18",
  "is_school_day": true,
  "description": "Test school day"
}
```

---

### PUT `/school-calendar/{calendar_id}`

Updates a school calendar record.

Request:

```json
{
  "is_school_day": false,
  "description": "Holiday"
}
```

---

### DELETE `/school-calendar/{calendar_id}`

Deletes a calendar record.

A calendar record cannot be deleted if used by schedule records.

---

## 19. Schedule

Schedule records are stored in:

```text
Tbl_GeneratedSchedule
```

The schedule uses:

```text
DisciplineCourseYearID
```

instead of:

```text
DisciplineID
```

This makes the schedule more precise.

---

### GET `/schedule`

Returns all schedule records.

---

### GET `/schedule/{schedule_id}`

Returns one schedule record by ID.

Example:

```text
GET /schedule/1
```

---

### GET `/schedule/class/{class_id}`

Returns schedule records for one class.

Example:

```text
GET /schedule/class/1
```

---

### GET `/schedule/professor/{professor_id}`

Returns schedule records for one professor.

Example:

```text
GET /schedule/professor/1
```

---

### GET `/schedule/room/{room_id}`

Returns schedule records for one room.

Example:

```text
GET /schedule/room/2
```

---

### POST `/schedule`

Creates a schedule record.

Request:

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

Allowed `status` values:

```text
draft
approved
cancelled
```

Schedule validation rules:

- The class must exist.
- The discipline course year record must exist.
- The professor must exist.
- The room must exist.
- The calendar date must exist.
- The calendar date must be a school day.
- The class course must match the discipline course.
- The class school year must match the discipline school year.
- The class course year number must match the discipline course year number.
- The professor must be assigned to the selected discipline course year.
- Practical disciplines must be scheduled in practice rooms.
- A class cannot have overlapping lessons.
- A professor cannot have overlapping lessons.
- A room cannot have overlapping lessons.

---

### PUT `/schedule/{schedule_id}`

Updates a schedule record.

Request:

```json
{
  "room_id": 3,
  "start_time": "11:00:00",
  "end_time": "12:00:00",
  "status": "approved"
}
```

The same schedule validations are applied when updating.

---

### DELETE `/schedule/{schedule_id}`

Deletes a schedule record.

A schedule record cannot be deleted if used by attendance records.

---

## 20. Attendance

Attendance records are stored in:

```text
Tbl_AttendanceRecords
```

---

### GET `/attendance`

Returns all attendance records.

---

### GET `/attendance/{attendance_id}`

Returns one attendance record by ID.

Example:

```text
GET /attendance/1
```

---

### GET `/attendance/student/{student_id}`

Returns attendance records for one student.

Example:

```text
GET /attendance/student/1
```

---

### GET `/attendance/schedule/{schedule_id}`

Returns attendance records for one schedule record.

Example:

```text
GET /attendance/schedule/1
```

---

### POST `/attendance`

Creates an attendance record.

Request:

```json
{
  "student_id": 1,
  "schedule_id": 1,
  "punch_type": "in",
  "punch_method": "nfc",
  "is_synced": true
}
```

Allowed `punch_type` values:

```text
in
out
```

Allowed `punch_method` values:

```text
nfc
rfid
qr
barcode
manual
```

---

### PUT `/attendance/{attendance_id}`

Updates an attendance record.

Request:

```json
{
  "punch_type": "out",
  "punch_method": "manual",
  "is_synced": true
}
```

---

### DELETE `/attendance/{attendance_id}`

Deletes an attendance record.

---

## 21. Recommended Swagger Test Order

Recommended order for testing in Swagger:

```text
GET /
POST /auth/login
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

## 22. Useful Test Payloads

---

### Create Course

```json
{
  "code": "WEBDEV",
  "name": "Web Development Technician"
}
```

---

### Create Class

```json
{
  "name": "TGEI 1B",
  "course_id": 1,
  "school_year_id": 1,
  "course_year_number": 1
}
```

---

### Create Student

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

---

### Create Room

```json
{
  "name": "Computer Lab Test",
  "capacity": 25,
  "is_practice_room": true,
  "location": "Test building"
}
```

---

### Create Discipline

```json
{
  "name": "Cybersecurity",
  "code": "CYBER"
}
```

---

### Create Discipline Course Year

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

---

### Assign Professor to Discipline Course Year

```json
{
  "professor_id": 1,
  "discipline_course_year_id": 1
}
```

---

### Create School Calendar Record

```json
{
  "school_year_id": 1,
  "calendar_date": "2026-05-18",
  "is_school_day": true,
  "description": "Test school day"
}
```

---

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

---

### Create Schedule Record

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

---

### Create Attendance Record

```json
{
  "student_id": 1,
  "schedule_id": 1,
  "punch_type": "in",
  "punch_method": "nfc",
  "is_synced": true
}
```

---

## 23. Known Limitations

The current API is functional, but still has some limitations:

- Large list endpoints do not have pagination yet.
- Some helper functions are duplicated across routers.
- `UserCreate` should be improved so the frontend sends `password` instead of `password_hash`.
- The automatic schedule generation algorithm is not implemented yet.
- The current schedule endpoint validates manual schedule creation but does not generate full schedules automatically.

---

## 24. Recommended Future Improvements

Recommended future API improvements:

1. Add pagination to large endpoints such as `/attendance`.
2. Move duplicated helper functions to `utils.py`.
3. Update user creation to accept a plain `password` and hash it in the backend.
4. Add dashboard endpoints for attendance summaries.
5. Add absence alert endpoints.
6. Add automatic schedule generation.
7. Define hard and soft constraints for scheduling.
8. Consider separating business logic into service files.
9. Consider using a database connection dependency or connection pool.