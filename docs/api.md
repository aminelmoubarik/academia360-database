# Academia360 API Documentation

This document describes the FastAPI backend created for the Academia360 project.

The API connects to the local MySQL database `academia360` and exposes endpoints to read, create, update and delete data from the system.

The backend has been organized into routers to keep the code cleaner and easier to maintain.

## Technologies

- Python
- FastAPI
- Uvicorn
- MySQL
- mysql-connector-python
- XAMPP
- passlib
- bcrypt
- python-jose

## How to run the API locally

1. Start MySQL using XAMPP.

2. Open the project in VS Code.

3. Open a terminal.

4. Go to the backend folder:

   `cd backend`

5. Install dependencies:

   `py -m pip install -r requirements.txt`

6. Run the API:

   `py -m uvicorn app:app --reload`

7. Open the API documentation:

   `http://127.0.0.1:8000/docs`

## Backend structure

The backend is organized into separate routers.

Current router groups:

- Authentication
- Students
- Attendance
- Academic Data
- Health

Current backend structure:

```text
backend/
├── app.py
├── auth.py
├── create_demo_passwords.py
├── db.py
├── models.py
├── requirements.txt
└── routers/
    ├── __init__.py
    ├── academic.py
    ├── attendance.py
    ├── auth_routes.py
    └── students.py
```

### `app.py`

Main FastAPI application.

It creates the API, defines the health endpoint and includes the routers.

### `models.py`

Contains the Pydantic request models used by the API.

Current models:

- `LoginRequest`
- `AttendanceCreate`
- `StudentCreate`
- `StudentUpdate`

### `routers/auth_routes.py`

Contains authentication endpoints:

- `POST /login`
- `GET /me`

### `routers/students.py`

Contains student endpoints:

- `GET /students`
- `POST /students`
- `PUT /students/{student_id}`
- `DELETE /students/{student_id}`

### `routers/attendance.py`

Contains attendance endpoints:

- `GET /attendance`
- `POST /attendance`

### `routers/academic.py`

Contains academic data endpoints:

- `GET /professors`
- `GET /rooms`
- `GET /disciplines`
- `GET /schedule`

## Authentication

The API includes basic authentication using JWT tokens.

Users log in with email and password using:

```text
POST /login
```

If the credentials are valid, the API returns an access token.

Protected endpoints require a Bearer token using the Swagger `Authorize` button.

Current roles:

- admin
- director
- secretary
- professor

## Available endpoints

### Public endpoints

```text
GET /
POST /login
```

### Protected endpoints

```text
GET /me
GET /students
POST /students
PUT /students/{student_id}
DELETE /students/{student_id}
GET /professors
GET /rooms
GET /disciplines
GET /schedule
GET /attendance
POST /attendance
```

The API returns data in JSON format.

---

## Health endpoint

### GET `/`

Checks if the API is running.

This endpoint does not access the database. It only confirms that the FastAPI server is working.

Example response:

```json
{
  "message": "Academia360 API is running"
}
```

---

## Authentication endpoints

### POST `/login`

Authenticates a user with email and password and returns an access token.

Example request:

```json
{
  "email": "admin@academia360.pt",
  "password": "admin123"
}
```

Example response:

```json
{
  "access_token": "token",
  "token_type": "bearer"
}
```

### GET `/me`

Returns the currently authenticated user.

Allowed roles:

- admin
- director
- secretary
- professor

Example response:

```json
{
  "id": 1,
  "full_name": "Admin User",
  "email": "admin@academia360.pt",
  "role": "admin"
}
```

---

## Student endpoints

### GET `/students`

Returns the list of students stored in the database.

This endpoint reads data from the `students` table and joins it with the `classes` table to show the class name and course name of each student.

Allowed roles:

- admin
- director
- secretary

### POST `/students`

Creates a new student.

Allowed roles:

- admin
- secretary

Example request:

```json
{
  "full_name": "Test Student",
  "student_number": "STU010",
  "card_uid": "CARD010",
  "class_id": 1
}
```

Example response:

```json
{
  "message": "Student created successfully",
  "student_id": 4
}
```

### PUT `/students/{student_id}`

Updates an existing student.

Allowed roles:

- admin
- secretary

Example request:

```json
{
  "full_name": "Updated Test Student",
  "student_number": "STU010",
  "card_uid": "CARD010",
  "class_id": 1
}
```

Example response:

```json
{
  "message": "Student updated successfully",
  "student_id": 4
}
```

### DELETE `/students/{student_id}`

Deletes a student only if the student has no attendance records.

Allowed roles:

- admin
- secretary

Example response:

```json
{
  "message": "Student deleted successfully",
  "student_id": 4
}
```

Student validation:

- Returns `404 Class not found` if the class does not exist.
- Returns `409 Conflict` if the student number or card UID already exists.
- Returns `409 Conflict` if trying to delete a student with attendance records.
- Returns `403 Not enough permissions` if the user role is not allowed.
- Returns `401 Invalid authentication credentials` if the token is missing or invalid.

---

## Attendance endpoints

### GET `/attendance`

Returns the attendance records.

This endpoint reads data from the `attendance_records` table and joins it with the `students` table.

Allowed roles:

- admin
- director
- secretary
- professor

### POST `/attendance`

Creates a new attendance record.

This endpoint inserts a new row into the `attendance_records` table.

Used for:

- Registering student attendance
- Saving clock-in or clock-out actions
- Storing the punch method: NFC, RFID, QR, barcode or manual

Allowed roles:

- admin
- secretary
- professor

Example request:

```json
{
  "student_id": 1,
  "schedule_id": 1,
  "punch_type": "in",
  "punch_method": "nfc"
}
```

Example response:

```json
{
  "message": "Attendance record created successfully",
  "attendance_id": 3
}
```

Attendance validation:

- Returns `404 Student not found` if the student does not exist.
- Returns `404 Schedule not found` if the schedule does not exist.
- Returns `403 Not enough permissions` if the user role is not allowed.
- Returns `401 Invalid authentication credentials` if the token is missing or invalid.

---

## Academic data endpoints

### GET `/professors`

Returns the list of professors stored in the database.

This endpoint reads data from the `professors` table.

Allowed roles:

- admin
- director
- secretary

### GET `/rooms`

Returns the list of school rooms.

This endpoint reads data from the `rooms` table.

Allowed roles:

- admin
- director
- secretary
- professor

### GET `/disciplines`

Returns the list of disciplines or subjects.

This endpoint reads data from the `disciplines` table.

Allowed roles:

- admin
- director
- secretary
- professor

### GET `/schedule`

Returns the generated school schedule.

This endpoint reads data from the `generated_schedule` table and joins it with `classes`, `disciplines`, `professors` and `rooms`.

Allowed roles:

- admin
- director
- secretary
- professor

---

## Current status

The API is working locally and has been tested with the MySQL database.

Completed:

- Read endpoints
- Attendance registration endpoint
- Basic authentication
- JWT token generation
- Bearer token authorization
- Role-based endpoint protection
- Student CRUD endpoints
- Student creation, update and delete
- Class validation
- Duplicate student number/card UID validation
- Protection against deleting students with attendance records
- Backend refactored into routers
- API endpoints grouped by feature
- Authentication, students, attendance and academic data separated into modules

## Next steps

- Add CRUD endpoints for professors
- Add CRUD endpoints for rooms
- Add CRUD endpoints for disciplines
- Improve attendance registration logic
- Add schedule management endpoints
- Prepare the backend for future Flutter integration