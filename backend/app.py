from fastapi import FastAPI

from routers import auth_routes, students, attendance, academic, professors, rooms

app = FastAPI(title="Academia360 API")


@app.get("/", tags=["Health"])
def home():
    return {"message": "Academia360 API is running"}


app.include_router(auth_routes.router)
app.include_router(students.router)
app.include_router(professors.router)
app.include_router(attendance.router)
app.include_router(academic.router)
app.include_router(rooms.router)