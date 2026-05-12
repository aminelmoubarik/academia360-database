from fastapi import FastAPI
from db import get_connection

app = FastAPI(title="Academia360 API")


@app.get("/")
def home():
    return {"message": "Academia360 API is running"}


@app.get("/students")
def get_students():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            students.id,
            students.full_name,
            students.student_number,
            students.card_uid,
            classes.name AS class_name,
            classes.course_name
        FROM students
        LEFT JOIN classes ON students.class_id = classes.id
    """)

    data = cursor.fetchall()

    cursor.close()
    connection.close()

    return data


@app.get("/professors")
def get_professors():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            id,
            full_name,
            email
        FROM professors
    """)

    data = cursor.fetchall()

    cursor.close()
    connection.close()

    return data


@app.get("/rooms")
def get_rooms():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            id,
            name,
            capacity,
            is_practice_room,
            location
        FROM rooms
    """)

    data = cursor.fetchall()

    cursor.close()
    connection.close()

    return data


@app.get("/disciplines")
def get_disciplines():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            id,
            name,
            total_hours,
            lesson_duration_minutes,
            is_practical
        FROM disciplines
    """)

    data = cursor.fetchall()

    cursor.close()
    connection.close()

    return data


@app.get("/schedule")
def get_schedule():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            generated_schedule.id,
            generated_schedule.schedule_date,
            generated_schedule.start_time,
            generated_schedule.end_time,
            classes.name AS class_name,
            disciplines.name AS discipline,
            professors.full_name AS professor,
            rooms.name AS room,
            generated_schedule.status
        FROM generated_schedule
        JOIN classes ON generated_schedule.class_id = classes.id
        JOIN disciplines ON generated_schedule.discipline_id = disciplines.id
        JOIN professors ON generated_schedule.professor_id = professors.id
        JOIN rooms ON generated_schedule.room_id = rooms.id
    """)

    data = cursor.fetchall()

    for item in data:
        item["schedule_date"] = str(item["schedule_date"])
        item["start_time"] = str(item["start_time"])
        item["end_time"] = str(item["end_time"])

    cursor.close()
    connection.close()

    return data


@app.get("/attendance")
def get_attendance():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            attendance_records.id,
            students.full_name AS student,
            attendance_records.punch_type,
            attendance_records.punch_method,
            attendance_records.punch_time,
            attendance_records.is_synced
        FROM attendance_records
        JOIN students ON attendance_records.student_id = students.id
    """)

    data = cursor.fetchall()

    for item in data:
        item["punch_time"] = str(item["punch_time"])

    cursor.close()
    connection.close()

    return data