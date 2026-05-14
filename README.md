# Academia360 Database and API

Initial MySQL database model and FastAPI backend for the Academia360 project.

Academia360 is an integrated school management platform focused on attendance registration and automatic timetable management.

The project is designed to support attendance registration using NFC/RFID/QR/barcode and school schedule management using students, professors, classes, disciplines, rooms, teacher availability and school calendar data.

## Project objective

The objective of this first version is to design, test and document the initial database structure and create a backend API connected to MySQL.

The current version supports:

- Student management
- Professor management
- Room management
- Classes
- Disciplines
- School calendar
- Teacher availability
- Generated schedules
- Attendance records using NFC/RFID/QR/barcode
- API endpoints to read data from the database
- Attendance registration through the API
- Basic authentication
- JWT token generation
- Bearer token authorization
- Role-based endpoint protection
- Student CRUD endpoints
- Professor CRUD endpoints
- Room CRUD endpoints
- Backend structure organized into routers
- Environment-based configuration for secrets and database settings

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
- python-dotenv
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
├── models.py
├── requirements.txt
├── .env.example
└── routers/
    ├── __init__.py
    ├── academic.py
    ├── attendance.py
    ├── auth_routes.py
    ├── professors.py
    ├── rooms.py
    └── students.py

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

It creates the FastAPI app, defines the health endpoint and includes the different routers.

### `backend/auth.py`

Authentication and authorization logic.

It includes:

- Password hashing
- Password verification
- JWT token creation
- Bearer token authentication
- Role-based access control
- Environment-based secret key configuration

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

It connects the FastAPI backend with the local MySQL database using environment variables.

### `backend/models.py`

Contains the Pydantic request models used by the API.

Current models include:

- `LoginRequest`
- `AttendanceCreate`
- `StudentCreate`
- `StudentUpdate`
- `ProfessorCreate`
- `ProfessorUpdate`
- `RoomCreate`
- `RoomUpdate`

### `backend/routers/`

Contains the API routers grouped by feature.

Current routers:

- `auth_routes.py`: login and current user endpoints
- `students.py`: student read and CRUD endpoints
- `professors.py`: professor read and CRUD endpoints
- `rooms.py`: room read and CRUD endpoints
- `attendance.py`: attendance read and creation endpoints
- `academic.py`: disciplines and schedule endpoints

### `backend/requirements.txt`

Contains the Python dependencies needed to run the backend.

### `backend/.env.example`

Example environment configuration file.

It shows which variables must be created locally in `backend/.env`.

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

## Environment variables

The backend uses environment variables for sensitive and local configuration.

Create a `.env` file inside the `backend/` folder using `.env.example` as reference.

Example:

```text
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=60

DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=academia360
```

The `.env` file is ignored by Git and must not be uploaded to GitHub.

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

3. Create the local `.env` file inside `backend/`.

4. Open a terminal.

5. Go to the backend folder:

```powershell
cd backend
```

6. Install dependencies:

```powershell
py -m pip install -r requirements.txt
```

7. Run the API:

```powershell
py -m uvicorn app:app --reload
```

8. Open the API documentation:

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

### Authentication endpoints

```text
GET /me
```

### Student endpoints

```text
GET /students
POST /students
PUT /students/{student_id}
DELETE /students/{student_id}
```

### Professor endpoints

```text
GET /professors
POST /professors
PUT /professors/{professor_id}
DELETE /professors/{professor_id}
```

### Room endpoints

```text
GET /rooms
POST /rooms
PUT /rooms/{room_id}
DELETE /rooms/{room_id}
```

### Attendance endpoints

```text
GET /attendance
POST /attendance
```

### Academic data endpoints

```text
GET /disciplines
GET /schedule
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
- Returns `401 Invalid authentication credentials` if the token is missing or invalid.

## Professor CRUD

The API includes basic CRUD operations for professor management.

### `POST /professors`

Creates a new professor.

Allowed roles:

- `admin`
- `secretary`

### `PUT /professors/{professor_id}`

Updates an existing professor.

Allowed roles:

- `admin`
- `secretary`

### `DELETE /professors/{professor_id}`

Deletes a professor only if the professor has no related schedules, availability records or discipline assignments.

Allowed roles:

- `admin`
- `secretary`

Validation included:

- Returns `404 User not found` if the assigned user does not exist.
- Returns `404 Professor not found` if the professor does not exist.
- Returns `409 Conflict` if the professor email or user already exists.
- Returns `409 Conflict` if trying to delete a professor with related records.
- Returns `403 Not enough permissions` if the user role is not allowed.

## Room CRUD

The API includes basic CRUD operations for room management.

### `POST /rooms`

Creates a new room.

Allowed roles:

- `admin`
- `secretary`

### `PUT /rooms/{room_id}`

Updates an existing room.

Allowed roles:

- `admin`
- `secretary`

### `DELETE /rooms/{room_id}`

Deletes a room only if the room is not used in generated schedules.

Allowed roles:

- `admin`
- `secretary`

Validation included:

- Returns `400 Room capacity must be greater than 0` if the capacity is invalid.
- Returns `404 Room not found` if the room does not exist.
- Returns `409 Conflict` if trying to delete a room with generated schedules.
- Returns `403 Not enough permissions` if the user role is not allowed.

## Backend structure

The backend has been refactored into routers to keep the code organized.

Current router groups:

- Authentication
- Students
- Professors
- Rooms
- Attendance
- Academic Data
- Health

This makes the project easier to maintain and prepares it for future features such as discipline CRUD, schedule management and frontend integration.

## Current status

The initial database model and backend API have been created and tested locally.

Completed:

- MySQL schema
- Foreign key relationships
- Test data
- Validation queries
- Entity Relationship Diagram
- Database documentation
- API documentation
- Initial FastAPI backend
- MySQL database connection
- Environment-based configuration
- Read endpoints
- Attendance registration endpoint
- Basic authentication
- JWT token generation
- Bearer token authorization
- Role-based endpoint protection
- Student CRUD endpoints
- Student creation, update and delete
- Professor CRUD endpoints
- Professor creation, update and delete
- Room CRUD endpoints
- Room creation, update and delete
- Class validation when creating or updating students
- Duplicate student number/card UID validation
- Protection against deleting students with attendance records
- Protection against deleting professors with related records
- Protection against deleting rooms with generated schedules
- Backend refactored into routers
- API endpoints grouped by feature

## Next steps

- Add CRUD endpoints for disciplines
- Improve attendance registration logic
- Add schedule management endpoints
- Prepare the backend for future Flutter integration
- Add frontend/mobile interface
- Add reporting and dashboard features