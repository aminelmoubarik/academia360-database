from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    {
        "name": "Authentication",
        "description": "Login and authentication endpoints."
    },
    {
        "name": "Health Check",
        "description": "API status check."
    },
    {
        "name": "Roles",
        "description": "User role management."
    },
    {
        "name": "Genders",
        "description": "Gender reference values."
    },
    {
        "name": "School Years",
        "description": "School year management."
    },
    {
        "name": "Courses",
        "description": "Course management."
    },
    {
        "name": "Classes",
        "description": "Class management."
    },
    {
        "name": "Users",
        "description": "User management."
    },
    {
        "name": "Professors",
        "description": "Professor management."
    },
    {
        "name": "Students",
        "description": "Student management."
    },
    {
        "name": "Rooms",
        "description": "Room management."
    },
    {
        "name": "Disciplines",
        "description": "Discipline catalogue management."
    },
    {
        "name": "Discipline Course Years",
        "description": "Discipline workload configuration by course and school year."
    },
    {
        "name": "Professor Discipline Course Years",
        "description": "Professor assignment to discipline course year records."
    },
    {
        "name": "Teacher Availability",
        "description": "Teacher availability management."
    },
    {
        "name": "School Calendar",
        "description": "School calendar management."
    },
    {
        "name": "Schedule",
        "description": "Schedule management and validation."
    },
    {
        "name": "Attendance",
        "description": "Attendance record management."
    }
]


app = FastAPI(
    title="Academia360 API",
    description="Backend API for attendance, schedules, courses, rooms, professors and students.",
    version="1.0.0",
    openapi_tags=tags_metadata
)


# CORS configuration
# In development we allow all origins so the Flutter web client (and others)
# can call the API from a different port. Restrict this in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health Check"])
def health_check():
    return {
        "message": "Academia360 API is running"
    }


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