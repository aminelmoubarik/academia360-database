# Academia360 Database

Initial MySQL database model for the Academia360 project.

Academia360 is an integrated school management platform focused on attendance registration and automatic timetable management.

## Project objective

The objective of this first version is to design and test the initial MySQL database structure for the project.

The database supports:

- Student management
- Professor management
- Classes
- Disciplines
- Rooms
- School calendar
- Teacher availability
- Generated schedules
- Attendance records using NFC/RFID/QR/barcode


## Technologies used

- MySQL
- XAMPP
- VS Code
- MySQL Shell for VS Code
- GitHub
- Plane


## How to run the backend locally

1. Start MySQL using XAMPP.
2. Open the project in VS Code.
3. Go to the backend folder:

```powershell
cd backend

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
├── database.md
└── er-diagram.md

.gitignore
README.md
