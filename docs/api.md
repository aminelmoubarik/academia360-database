# Academia360 API Documentation

This document describes the initial FastAPI backend created for the Academia360 project.

The API connects to the local MySQL database `academia360` and exposes the first endpoints needed to read and create data from the system.

## Technologies

- Python
- FastAPI
- Uvicorn
- MySQL
- mysql-connector-python
- XAMPP

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

### GET `/students`

Returns the list of students stored in the database.

This endpoint reads data mainly from the `students` table and joins it with the `classes` table to show the class name and course name of each student.

### GET `/professors`

Returns the list of professors stored in the database.

This endpoint reads data from the `professors` table.

### GET `/rooms`

Returns the list of school rooms.

This endpoint reads data from the `rooms` table.

### GET `/disciplines`

Returns the list of disciplines or subjects.

This endpoint reads data from the `disciplines` table.

### GET `/schedule`

Returns the generated school schedule.

This endpoint reads data from the `generated_schedule` table and joins it with `classes`, `disciplines`, `professors` and `rooms`.

### GET `/attendance`

Returns the attendance records.

This endpoint reads data from the `attendance_records` table and joins it with the `students` table.

### POST `/attendance`

Creates a new attendance record.

This endpoint inserts a new row into the `attendance_records` table.

Used for:

- Registering student attendance
- Saving clock-in or clock-out actions
- Storing the punch method: NFC, RFID, QR, barcode or manual

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

## Current status

The initial API is working locally and has been tested with the MySQL database.

The API currently supports:

- Reading students
- Reading professors
- Reading rooms
- Reading disciplines
- Reading generated schedules
- Reading attendance records
- Creating attendance records

## Next steps

- Add authentication
- Add role-based access control
- Protect endpoints depending on user role
- Prepare the API for future Flutter integration