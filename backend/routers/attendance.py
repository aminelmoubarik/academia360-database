from fastapi import APIRouter, HTTPException, Depends

from db import get_connection
from auth import require_roles
from models import AttendanceCreate


router = APIRouter(tags=["Attendance"])


@router.get("/attendance")
def get_attendance(
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
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


@router.post("/attendance")
def create_attendance(
    record: AttendanceCreate,
    current_user=Depends(require_roles(["admin", "secretary", "professor"]))
):
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