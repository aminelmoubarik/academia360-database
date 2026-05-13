# Academia360 Database and API

Initial MySQL database model and FastAPI backend for the Academia360 project.

Academia360 is an integrated school management platform focused on attendance registration and automatic timetable management.

The project is designed to support attendance registration using NFC/RFID/QR/barcode and school schedule management using students, professors, classes, disciplines, rooms, teacher availability and school calendar data.

## Project objective

The objective of this first version is to design, test and document the initial database structure and create a basic backend API connected to MySQL.

The current version supports:

- Student management
- Professor management
- Classes
- Disciplines
- Rooms
- School calendar
- Teacher availability
- Generated schedules
- Attendance records using NFC/RFID/QR/barcode
- Basic API endpoints to read data from the database
- Attendance registration through the API
- Basic authentication
- JWT token generation
- Bearer token authorization
- Role-based endpoint protection
- Student CRUD endpoints

## Technologies used

- MySQL
- XAMPP
- Python
- FastAPI
- Uvicorn
- mysql-connector-python
- passlib
- bcrypt
- python-jose
- VS Code
- MySQL Shell for VS Code
- GitHub
- Plane

## Repository structure

```text
backend/
├── app.py
├── auth.py
├── create_demo_passwords.py
├── db.py
└── requirements.txt

database/
├── schema.sql
├── seed.sql
└── queries.sql

docs/
├── api.md
├── database.md
└── er-diagram.md

.gitignore
README.md
```

## Database files

### `database/schema.sql`

Creates the `academia360` database and all main tables with their relationships.

### `database/seed.sql`

Inserts test data into the database.

### `database/queries.sql`

Contains validation queries to check that the database structure and relationships work correctly.

## Backend files

### `backend/app.py`

Main FastAPI application.

It contains the API endpoints used to read, create, update and delete data from the MySQL database.

### `backend/auth.py`

Authentication and authorization logic.

It includes:

- Password hashing
- Password verification
- JWT token creation
- Bearer token authentication
- Role-based access control

### `backend/create_demo_passwords.py`

Development script used to generate password hashes for demo users.

Demo users include:

- `admin@academia360.pt`
- `director@academia360.pt`
- `secretary@academia360.pt`
- `afonso@academia360.pt`
- `joana@academia360.pt`

### `backend/db.py`

Database connection file.

It connects the FastAPI backend with the local MySQL database.

### `backend/requirements.txt`

Contains the Python dependencies needed to run the backend.

## Documentation files

### `docs/api.md`

Explains how to run the API and describes the available endpoints.

### `docs/database.md`

Explains the purpose of the main database tables and relationships.

### `docs/er-diagram.md`

Contains the Entity Relationship Diagram using Mermaid.

## Main database tables

- `users`
- `students`
- `professors`
- `classes`
- `disciplines`
- `professor_disciplines`
- `rooms`
- `school_calendar`
- `teacher_availability`
- `generated_schedule`
- `attendance_records`

## How to run the database locally

1. Start MySQL using XAMPP.

2. Open the project in VS Code.

3. Connect to MySQL using MySQL Shell for VS Code.

4. Execute the SQL files in this order:

```text
database/schema.sql
database/seed.sql
database/queries.sql
```

5. Go to the backend folder:

```powershell
cd backend
```

6. Generate demo user password hashes:

```powershell
py create_demo_passwords.py
```

## How to run the backend locally

1. Start MySQL using XAMPP.

2. Open the project in VS Code.

3. Open a terminal.

4. Go to the backend folder:

```powershell
cd backend
```

5. Install dependencies:

```powershell
py -m pip install -r requirements.txt
```

6. Run the API:

```powershell
py -m uvicorn app:app --reload
```

7. Open the API documentation:

```text
http://127.0.0.1:8000/docs
```

## Authentication

The API includes basic authentication using JWT tokens.

Users log in with email and password using:

```text
POST /login
```

If the credentials are valid, the API returns an access token.

Protected endpoints require a Bearer token using the Swagger `Authorize` button.

Current roles:

- `admin`
- `director`
- `secretary`
- `professor`

## Available API endpoints

### Public endpoints

```text
GET /
POST /login
```

### Authenticated endpoints

```text
GET /me
GET /students
GET /professors
GET /rooms
GET /disciplines
GET /schedule
GET /attendance
POST /attendance
```

### Student CRUD endpoints

```text
POST /students
PUT /students/{student_id}
DELETE /students/{student_id}
```

The API returns data in JSON format.

## Student CRUD

The API includes basic CRUD operations for student management.

### `POST /students`

Creates a new student.

Allowed roles:

- `admin`
- `secretary`

### `PUT /students/{student_id}`

Updates an existing student.

Allowed roles:

- `admin`
- `secretary`

### `DELETE /students/{student_id}`

Deletes a student only if the student has no attendance records.

Allowed roles:

- `admin`
- `secretary`

Validation included:

- Returns `404 Class not found` if the class does not exist.
- Returns `409 Conflict` if the student number or card UID already exists.
- Returns `409 Conflict` if trying to delete a student with attendance records.
- Returns `403 Not enough permissions` if the user role is not allowed.

## Current status

The initial database model and backend API have been created and tested locally.

Completed:

- MySQL schema
- Foreign key relationships
- Test data
- Validation queries
- Entity Relationship Diagram
- Database documentation
- Initial FastAPI backend
- MySQL database connection
- API documentation
- Read endpoints
- Attendance registration endpoint
- Basic authentication
- JWT token generation
- Bearer token authorization
- Role-based endpoint protection
- Student CRUD endpoints
- Student creation, update and delete
- Class validation when creating or updating students
- Protection against deleting students with attendance records


- Student CRUD endpoints
- Student creation, update and delete
- Class validation when creating or updating students
- Protection against deleting students with attendance records

## Next steps

- Refactor the backend into multiple files and routers
- Add CRUD endpoints for professors
- Add CRUD endpoints for rooms
- Add CRUD endpoints for disciplines
- Improve attendance registration logic
- Add schedule management endpoints
- Prepare the backend for future Flutter integration
- Add frontend/mobile interface
- Add reporting and dashboard features
