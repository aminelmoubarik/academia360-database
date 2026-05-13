# Academia360 API Documentation

This document describes the initial FastAPI backend created for the Academia360 project.

The API connects to the local MySQL database `academia360` and exposes the first endpoints needed to read, create, update and delete data from the system.

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

## Available endpoints

### GET `/`

Checks if the API is running.

This endpoint does not access the database. It only confirms that the FastAPI server is working.

Example response:

```json
{
  "message": "Academia360 API is running"
}
```

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

Protected endpoints require a Bearer token using the Swagger `Authorize` button.

Roles currently supported:

- admin
- director
- secretary
- professor

---

## Read endpoints

### GET `/students`

Returns the list of students stored in the database.

This endpoint reads data mainly from the `students` table and joins it with the `classes` table to show the class name and course name of each student.

Allowed roles:

- admin
- director
- secretary

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

### GET `/attendance`

Returns the attendance records.

This endpoint reads data from the `attendance_records` table and joins it with the `students` table.

Allowed roles:

- admin
- director
- secretary
- professor

---

## Attendance endpoints

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

---

## Student CRUD

The API includes basic CRUD operations for student management.

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

Validation:

- Returns `404 Class not found` if the class does not exist.
- Returns `409 Conflict` if the student number or card UID already exists.
- Returns `409 Conflict` if trying to delete a student with attendance records.
- Returns `403 Not enough permissions` if the user role is not allowed.
- Returns `401 Invalid authentication credentials` if the token is missing or invalid.

---

## Current status

The initial API is working locally and has been tested with the MySQL database.

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

## Next steps

- Refactor the backend into multiple files and routers
- Add CRUD endpoints for professors
- Add CRUD endpoints for rooms
- Add CRUD endpoints for disciplines
- Improve attendance registration logic
- Add schedule management endpoints
- Prepare the backend for future Flutter integration