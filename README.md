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

## Technologies used

- MySQL
- XAMPP
- Python
- FastAPI
- Uvicorn
- mysql-connector-python
- VS Code
- MySQL Shell for VS Code
- GitHub
- Plane

## Repository structure

```text
backend/
├── app.py
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

It contains the API endpoints used to read data from the MySQL database.

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

## Available API endpoints

- `GET /`
- `GET /students`
- `GET /professors`
- `GET /rooms`
- `GET /disciplines`
- `GET /schedule`
- `GET /attendance`

The API returns data in JSON format.

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
- Read-only API endpoints
- API documentation
- - Basic authentication
- JWT token generation
- Bearer token authorization
- Role-based endpoint protection

## Next steps

- Add endpoint to register attendance
- Add authentication
- Add role-based access control
- Protect endpoints depending on user role
- Prepare the backend for future Flutter integration
