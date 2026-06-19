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
- Attendance dashboard endpoint with class/discipline breakdowns.
- Automatic timetable generator.
- Timetable readiness diagnostics.
- Timetable export endpoints for PDF and Excel.
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


## Backend Permissions

FastAPI routers use `require_roles(...)` to enforce role-based access. The current policy follows the Work Statement:

- Admin: complete backend access.
- Director: read reports/timetables/attendance and review justifications.
- Secretary: manage students, classes, attendance and justifications.
- Professor: view timetable/attendance data and register manual attendance.

Administrative configuration, users, catalogue data and timetable generation are restricted to admin users.

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
GET  /attendance/alerts
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
GET  /schedule/export/pdf
GET  /schedule/export/excel
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


## Step 8 - Absenteeism Alerts

The attendance module now exposes `/attendance/alerts`, which returns daily absentees, recurrent absences over a configurable recent period and class-level absenteeism summaries. This supports the project requirement for absenteeism alerts and attendance dashboards by class/subject.

## Step 9 - Partial Offline Sync

The `/attendance/offline-sync` endpoint now commits valid records even when some queued records fail. The API returns both `synced` and `failed` lists so the frontend can remove synchronized punches and keep only the records that need attention.
