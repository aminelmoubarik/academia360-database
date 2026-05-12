from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Literal
from db import get_connection

app = FastAPI(title="Academia360 API")

class AttendanceCreate(BaseModel):
    student_id: int
    schedule_id: Optional[int] = None
    punch_type: Literal["in", "out"]
    punch_method: Literal["nfc", "rfid", "qr", "barcode", "manual"]


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

@app.post("/attendance")
def create_attendance(record: AttendanceCreate):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT id FROM students WHERE id = %s",
        (record.student_id,)
    )
    student = cursor.fetchone()

    if student is None:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=404, detail="Student not found")

    if record.schedule_id is not None:
        cursor.execute(
            "SELECT id FROM generated_schedule WHERE id = %s",
            (record.schedule_id,)
        )
        schedule = cursor.fetchone()

        if schedule is None:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="Schedule not found")

    cursor.execute(
        """
        INSERT INTO attendance_records 
        (student_id, schedule_id, punch_type, punch_method)
        VALUES (%s, %s, %s, %s)
        """,
        (
            record.student_id,
            record.schedule_id,
            record.punch_type,
            record.punch_method
        )
    )

    connection.commit()
    new_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return {
        "message": "Attendance record created successfully",
        "attendance_id": new_id
    }