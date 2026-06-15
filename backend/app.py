import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import logging
import time as _time
from fastapi import Request

from routers import auth_routes
from routers import roles
from routers import genders
from routers import school_years
from routers import courses
from routers import classes
from routers import users
from routers import professors
from routers import students
from routers import rooms
from routers import disciplines
from routers import discipline_course_years
from routers import professor_discipline_course_years
from routers import teacher_availability
from routers import school_calendar
from routers import schedule
from routers import attendance


tags_metadata = [
    {"name": "Authentication", "description": "Login and authentication endpoints."},
    {"name": "Health Check", "description": "API status check."},
    {"name": "Roles", "description": "User role management."},
    {"name": "Genders", "description": "Gender reference values."},
    {"name": "School Years", "description": "School year management."},
    {"name": "Courses", "description": "Course management."},
    {"name": "Classes", "description": "Class management."},
    {"name": "Users", "description": "User management."},
    {"name": "Professors", "description": "Professor management."},
    {"name": "Students", "description": "Student management."},
    {"name": "Rooms", "description": "Room management."},
    {"name": "Disciplines", "description": "Discipline management."},
    {"name": "Discipline Course Years", "description": "Discipline workload per course year."},
    {"name": "Professor Discipline Course Years", "description": "Professor assignment to discipline course year records."},
    {"name": "Teacher Availability", "description": "Teacher availability management."},
    {"name": "School Calendar", "description": "School calendar management."},
    {"name": "Schedule", "description": "Schedule management and validation."},
    {"name": "Attendance", "description": "Attendance record management."},
]


app = FastAPI(
    title="Academia360 API",
    description="Backend API for attendance, schedules, courses, rooms, professors and students.",
    version="1.0.0",
    openapi_tags=tags_metadata,
)

# CORS: en producción define ALLOWED_ORIGINS="https://tu-frontend.netlify.app"
# (varios separados por coma). Sin definirla, permite todo (modo desarrollo).
_origins = os.getenv("ALLOWED_ORIGINS", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _origins.split(",")],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compresion gzip: respuestas JSON grandes (listas de alumnos, horarios)
# viajan ~80% mas pequenas. Estandar en APIs de produccion.
app.add_middleware(GZipMiddleware, minimum_size=1000)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
)
_logger = logging.getLogger("academia360")


@app.middleware("http")
async def security_and_timing(request: Request, call_next):
    """Anade cabeceras de seguridad estandar y mide el tiempo de cada
    peticion (visible en la cabecera X-Process-Time y en los logs)."""
    start = _time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (_time.perf_counter() - start) * 1000

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Process-Time"] = f"{elapsed_ms:.1f}ms"

    if elapsed_ms > 1000:
        _logger.warning("SLOW %s %s took %.0fms",
                        request.method, request.url.path, elapsed_ms)
    return response



@app.get("/", tags=["Health Check"])
def root():
    return {"message": "Academia360 API is running"}


@app.get("/health", tags=["Health Check"])
def health():
    """Health check completo: comprueba también la conexión a la base de datos.
    Útil para diagnosticar despliegues (Render muestra el error real aquí)."""
    db_status = "ok"
    try:
        from db import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
    except Exception as exc:  # noqa: BLE001 - queremos el mensaje real
        db_status = f"error: {exc}"
    return {"api": "ok", "database": db_status}


app.include_router(auth_routes.router)
app.include_router(roles.router)
app.include_router(genders.router)
app.include_router(school_years.router)
app.include_router(courses.router)
app.include_router(classes.router)
app.include_router(users.router)
app.include_router(professors.router)
app.include_router(students.router)
app.include_router(rooms.router)
app.include_router(disciplines.router)
app.include_router(discipline_course_years.router)
app.include_router(professor_discipline_course_years.router)
app.include_router(teacher_availability.router)
app.include_router(school_calendar.router)
app.include_router(schedule.router)
app.include_router(attendance.router)
