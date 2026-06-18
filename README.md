# Academia360 Backend

FastAPI + MySQL backend for the Erasmus+ Academia360 project.

The backend provides authentication, academic data management, attendance punching and automatic timetable generation.

---

## Technology Stack

- Python
- FastAPI
- MySQL
- Pydantic
- JWT authentication
- Role-based access control

---

## Main Features

- JWT authentication.
- Role-based route protection.
- CRUD endpoints for academic entities.
- Relational database model for:
  - users,
  - roles,
  - students,
  - professors,
  - courses,
  - classes,
  - disciplines,
  - rooms,
  - school calendar,
  - teacher availability,
  - discipline workload,
  - generated schedules,
  - attendance records.
- Attendance punching endpoints.
- Offline attendance synchronization endpoint.
- Attendance dashboard endpoint.
- Automatic timetable generator.
- Timetable readiness diagnostics.
- Admin recovery and demo user generation script.

---

## Run Locally

```powershell
cd C:\Users\GU603\Documents\GitHub\DB\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python -m uvicorn app:app --reload
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Environment Variables

Create `backend/.env` from `.env.example` and configure your database credentials and secret key.

Never commit:

```text
.env
.venv/
```

---

## Demo Users and Admin Recovery

If the admin account was deleted, run:

```powershell
python create_demo_users_pt.py
```

This recreates or updates the demo users and their passwords.

Default admin login:

```text
admin@academia360.local / admin123
```

---

## Attendance Punching Endpoints

```text
POST /attendance/punch
POST /attendance/offline-sync
GET  /attendance/dashboard
GET  /attendance-justifications
POST /attendance-justifications
```

The backend supports punching by card UID or student number, punch type detection, manual/RFID/NFC/QR/barcode methods and offline synchronization.

---

## Timetable Generation Endpoints

```text
POST /schedule/generate
POST /schedule/check-readiness
GET  /schedule
GET  /schedule/class/{class_id}
GET  /schedule/professor/{professor_id}
GET  /schedule/room/{room_id}
```

The timetable generator considers:

- teacher availability,
- school calendar,
- room conflicts,
- teacher conflicts,
- class conflicts,
- room capacity,
- practical room requirements,
- discipline workload,
- lesson duration.

---

## Database Files

```text
DB/database/schema.sql
DB/database/seed.sql
DB/database/queries.sql
DB/docs/database.md
DB/docs/er-diagram.md
DB/docs/api.md
```
