from fastapi import FastAPI

from routers import attendance
from routers import classes
from routers import courses
from routers import discipline_course_years
from routers import disciplines
from routers import genders
from routers import professor_discipline_course_years
from routers import professors
from routers import roles
from routers import rooms
from routers import schedule
from routers import school_calendar
from routers import school_years
from routers import students
from routers import teacher_availability
from routers import users
from routers import auth_routes

app = FastAPI(
    title="Academia360 API",
    description="Backend API for attendance, schedules, courses, rooms, professors and students.",
    version="1.0.0"
)


@app.get("/")
def health_check():
    return {
        "message": "Academia360 API is running"
    }


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
app.include_router(auth_routes.router)
