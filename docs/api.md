# Academia360 API Documentation

This document describes the current API endpoints available in the Academia360 backend.

The backend is developed with FastAPI and uses JWT authentication with role-based access control.

---

## 1. Base URL

Local development URL:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

OpenAPI JSON:

```text
http://127.0.0.1:8000/openapi.json
```

---

## 2. Authentication

The API uses JWT authentication.

Authentication is handled through:

```text
POST /auth/login
```

Swagger also supports login through the **Authorize** button.

In Swagger, the login field is called `username`, but the backend expects the user's email.

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

After a successful login, Swagger stores the Bearer token automatically and sends it in protected requests.

---

## 3. Demo Login Users

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

---

## 4. Authentication Endpoints

### POST `/auth/login`

Logs in a user and returns a JWT access token.

Swagger uses `application/x-www-form-urlencoded` for this endpoint.

Example Swagger values:

```text
username: admin@academia360.local
password: admin
```

Response example:

```json
{
  "access_token": "jwt-token-here",
  "token_type": "bearer"
}
```

---

### GET `/auth/me`

Returns the currently authenticated user.

This endpoint is useful to confirm that the token is working correctly.

Response example:

```json
{
  "user_id": 1,
  "full_name": "System Administrator",
  "email": "admin@academia360.local",
  "role": "admin"
}
```

If no token is provided, the endpoint should return:

```json
{
  "detail": "Not authenticated"
}
```

---

## 5. Role-Based Access Control

The backend uses role-based access control.

Current roles:

```text
admin
director
secretary
professor
```

General rule:

- `admin` has full access.
- `director` has high-level management access.
- `secretary` can manage most operational records.
- `professor` mainly has read access and limited attendance-related access.

---

## 6. Health Check

### GET `/`

Checks that the API is running.

Response example:

```json
{
  "message": "Academia360 API is running"
}
```

---

# 7. API Endpoints

---

## Roles

### GET `/roles`

Returns all user roles.

Allowed roles:

```text
admin
director
secretary
```

---

### GET `/roles/{role_id}`

Returns one role by ID.

---

### POST `/roles`

Creates a new role.

Allowed roles:

```text
admin
director
```

Request example:

```json
{
  "name": "coordinator"
}
```

---

### PUT `/roles/{role_id}`

Updates a role.

Request example:

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

## Genders

### GET `/genders`

Returns all gender reference values.

Allowed roles:

```text
admin
director
secretary
professor
```

---

### GET `/genders/{gender_id}`

Returns one gender by ID.

---

### POST `/genders`

Creates a gender reference value.

Request example:

```json
{
  "name": "Other"
}
```

---

### PUT `/genders/{gender_id}`

Updates a gender reference value.

Request example:

```json
{
  "name": "Not specified"
}
```

---

### DELETE `/genders/{gender_id}`

Deletes a gender reference value.

A gender cannot be deleted if it is being used by students or professors.

---

## School Years

### GET `/school-years`

Returns all school years.

---

### GET `/school-years/{school_year_id}`

Returns one school year by ID.

---

### POST `/school-years`

Creates a school year.

Request example:

```json
{
  "name": "2026/2027",
  "start_date": "2026-09-01",
  "end_date": "2027-07-31"
}
```

Validation:

```text
end_date must be greater than start_date
```

---

### PUT `/school-years/{school_year_id}`

Updates a school year.

Request example:

```json
{
  "name": "2026/2027 Updated"
}
```

---

### DELETE `/school-years/{school_year_id}`

Deletes a school year.

A school year cannot be deleted if it is being used by another record.

---

## Courses

### GET `/courses`

Returns all courses.

---

### GET `/courses/{course_id}`

Returns one course by ID.

---

### POST `/courses`

Creates a course.

Request example:

```json
{
  "code": "WEBDEV",
  "name": "Web Development Technician"
}
```

---

### PUT `/courses/{course_id}`

Updates a course.

Request example:

```json
{
  "name": "Updated Web Development Technician"
}
```

---

### DELETE `/courses/{course_id}`

Deletes a course.

A course cannot be deleted if it is being used by classes or discipline workload records.

---

## Classes

### GET `/classes`

Returns all classes with course and school year information.

---

### GET `/classes/{class_id}`

Returns one class by ID.

---

### POST `/classes`

Creates a class.

Request example:

```json
{
  "name": "TGEI 1A",
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

Request example:

```json
{
  "name": "TGEI 1B"
}
```

---

### DELETE `/classes/{class_id}`

Deletes a class.

A class cannot be deleted if it is being used by students or schedule records.

---

## Users

### GET `/users`

Returns all users.

Allowed roles:

```text
admin
director
secretary
```

---

### GET `/users/{user_id}`

Returns one user by ID.

---

### POST `/users`

Creates a user.

Current request example:

```json
{
  "full_name": "Test User",
  "email": "test.user@academia360.local",
  "password_hash": null,
  "role_id": 3
}
```

Current limitation:

```text
UserCreate currently accepts password_hash.
A future improvement should make this endpoint accept password instead,
then hash it in the backend before storing it.
```

---

### PUT `/users/{user_id}`

Updates a user.

Request example:

```json
{
  "full_name": "Updated User",
  "email": "updated.user@academia360.local",
  "role_id": 3
}
```

---

### DELETE `/users/{user_id}`

Deletes a user.

Allowed roles:

```text
admin
director
```

A user cannot be deleted if it is being used by another record.

---

## Professors

### GET `/professors`

Returns all professors with user, role, gender and assigned discipline information.

---

### GET `/professors/{professor_id}`

Returns one professor by ID.

---

### POST `/professors`

Creates a professor profile linked to an existing user.

Request example:

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

```text
Professor name and email are stored in Tbl_Users.
Tbl_Professors only stores professor-specific data.
```

---

### PUT `/professors/{professor_id}`

Updates professor-specific data.

Request example:

```json
{
  "city": "Porto",
  "contact": "919999999"
}
```

---

### DELETE `/professors/{professor_id}`

Deletes a professor.

A professor cannot be deleted if it is being used by schedules, availability or professor assignment records.

---

## Students

### GET `/students`

Returns all students with class, course, school year and gender information.

---

### GET `/students/{student_id}`

Returns one student by ID.

---

### POST `/students`

Creates a student.

Request example:

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

### PUT `/students/{student_id}`

Updates a student.

Request example:

```json
{
  "full_name": "Updated Student",
  "city": "Porto",
  "contact": "928888888"
}
```

---

### DELETE `/students/{student_id}`

Deletes a student.

A student cannot be deleted if it is being used by attendance records.

---

## Rooms

### GET `/rooms`

Returns all rooms.

---

### GET `/rooms/{room_id}`

Returns one room by ID.

---

### POST `/rooms`

Creates a room.

Request example:

```json
{
  "name": "Computer Lab 3",
  "capacity": 25,
  "is_practice_room": true,
  "location": "Main building - Third floor"
}
```

---

### PUT `/rooms/{room_id}`

Updates a room.

Request example:

```json
{
  "capacity": 30,
  "location": "Updated building"
}
```

---

### DELETE `/rooms/{room_id}`

Deletes a room.

A room cannot be deleted if it is being used by schedule records.

---

## Disciplines

### GET `/disciplines`

Returns all disciplines.

---

### GET `/disciplines/{discipline_id}`

Returns one discipline by ID.

---

### POST `/disciplines`

Creates a discipline.

Request example:

```json
{
  "name": "Cybersecurity",
  "code": "CYBER"
}
```

---

### PUT `/disciplines/{discipline_id}`

Updates a discipline.

Request example:

```json
{
  "name": "Advanced Cybersecurity"
}
```

---

### DELETE `/disciplines/{discipline_id}`

Deletes a discipline.

A discipline cannot be deleted if it is being used by discipline workload records.

---

## Discipline Course Years

### GET `/discipline-course-years`

Returns all discipline workload configurations.

---

### GET `/discipline-course-years/{discipline_course_year_id}`

Returns one discipline workload configuration by ID.

---

### POST `/discipline-course-years`

Creates a discipline workload configuration.

Request example:

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

Request example:

```json
{
  "total_minutes": 7800,
  "lesson_duration_minutes": 60
}
```

---

### DELETE `/discipline-course-years/{discipline_course_year_id}`

Deletes a discipline workload configuration.

A discipline workload configuration cannot be deleted if it is being used by schedule or professor assignment records.

---

## Professor Discipline Course Years

### GET `/professor-discipline-course-years`

Returns all professor assignments.

---

### GET `/professor-discipline-course-years/professor/{professor_id}`

Returns all discipline course year assignments for a specific professor.

---

### GET `/professor-discipline-course-years/discipline-course-year/{discipline_course_year_id}`

Returns all professors assigned to a specific discipline course year.

---

### GET `/professor-discipline-course-years/{professor_id}/{discipline_course_year_id}`

Returns one professor assignment.

---

### POST `/professor-discipline-course-years`

Assigns a professor to a discipline course year.

Request example:

```json
{
  "professor_id": 1,
  "discipline_course_year_id": 1
}
```

---

### DELETE `/professor-discipline-course-years/{professor_id}/{discipline_course_year_id}`

Deletes a professor assignment.

---

## Teacher Availability

### GET `/teacher-availability`

Returns all teacher availability records.

---

### GET `/teacher-availability/professor/{professor_id}`

Returns availability records for a specific professor.

---

### GET `/teacher-availability/{availability_id}`

Returns one availability record by ID.

---

### POST `/teacher-availability`

Creates a teacher availability record.

Request example:

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

Validation:

```text
end_time must be greater than start_time
```

---

### PUT `/teacher-availability/{availability_id}`

Updates a teacher availability record.

Request example:

```json
{
  "start_time": "10:00:00",
  "end_time": "14:00:00"
}
```

---

### DELETE `/teacher-availability/{availability_id}`

Deletes a teacher availability record.

---

## School Calendar

### GET `/school-calendar`

Returns all school calendar records.

---

### GET `/school-calendar/school-year/{school_year_id}`

Returns calendar records for a specific school year.

---

### GET `/school-calendar/{calendar_id}`

Returns one calendar record by ID.

---

### POST `/school-calendar`

Creates a school calendar record.

Request example:

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

Request example:

```json
{
  "is_school_day": false,
  "description": "Holiday"
}
```

---

### DELETE `/school-calendar/{calendar_id}`

Deletes a school calendar record.

A school calendar record cannot be deleted if it is being used by schedule records.

---

## Schedule

### GET `/schedule`

Returns all schedule records.

---

### GET `/schedule/class/{class_id}`

Returns schedule records for a specific class.

---

### GET `/schedule/professor/{professor_id}`

Returns schedule records for a specific professor.

---

### GET `/schedule/room/{room_id}`

Returns schedule records for a specific room.

---

### GET `/schedule/{schedule_id}`

Returns one schedule record by ID.

---

### POST `/schedule`

Creates a schedule record.

Request example:

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

Validation rules:

- The class must exist.
- The discipline course year must exist.
- The professor must exist.
- The room must exist.
- The calendar date must exist.
- The calendar date must be a school day.
- The class and discipline must belong to the same course.
- The class and discipline must belong to the same school year.
- The class and discipline must have the same course year number.
- The professor must be assigned to the selected discipline course year.
- Practical disciplines must be scheduled in practice rooms.
- A class cannot have overlapping lessons.
- A professor cannot have overlapping lessons.
- A room cannot have overlapping lessons.

---

### PUT `/schedule/{schedule_id}`

Updates a schedule record.

Request example:

```json
{
  "start_time": "11:00:00",
  "end_time": "12:00:00",
  "status": "approved"
}
```

The same validation rules used in `POST /schedule` are also applied when updating a schedule record.

---

### DELETE `/schedule/{schedule_id}`

Deletes a schedule record.

A schedule record cannot be deleted if it is being used by attendance records.

---

## Attendance

### GET `/attendance`

Returns all attendance records.

---

### GET `/attendance/student/{student_id}`

Returns attendance records for a specific student.

---

### GET `/attendance/schedule/{schedule_id}`

Returns attendance records for a specific schedule record.

---

### GET `/attendance/{attendance_id}`

Returns one attendance record by ID.

---

### POST `/attendance`

Creates an attendance record.

Request example:

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

### PUT `/attendance/{attendance_id}`

Updates an attendance record.

Request example:

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

## 8. Recommended Swagger Test Order

Recommended test order:

```text
1. GET /
2. Authorize with admin user
3. GET /auth/me
4. GET /roles
5. GET /genders
6. GET /school-years
7. GET /courses
8. GET /classes
9. GET /users
10. GET /professors
11. GET /students
12. GET /rooms
13. GET /disciplines
14. GET /discipline-course-years
15. GET /professor-discipline-course-years
16. GET /teacher-availability
17. GET /school-calendar
18. GET /schedule
19. GET /attendance
```

Recommended creation flow:

```text
1. POST /courses
2. POST /classes
3. POST /students
4. POST /rooms
5. POST /disciplines
6. POST /discipline-course-years
7. POST /professor-discipline-course-years
8. POST /school-calendar
9. POST /teacher-availability
10. POST /schedule
11. POST /attendance
```

---

## 9. Known Limitations

Current limitations:

- Large list endpoints do not have pagination yet.
- `UserCreate` currently accepts `password_hash` instead of `password`.
- Password hashing should be handled inside the backend when creating or updating users.
- The automatic schedule generation algorithm is not implemented yet.
- The schedule endpoint validates manual schedule creation but does not generate complete schedules automatically.
- Demo credentials are only intended for local development and testing.

---

## 10. Recent Backend Refactor

A shared `utils.py` file was added to reduce duplicated code across routers.

The following helper functions are now centralized:

```python
get_audit_username(current_user)
model_to_dict(model)
```

This improves maintainability because common logic no longer needs to be repeated in every router.