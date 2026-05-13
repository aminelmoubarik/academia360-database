from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from mysql.connector import IntegrityError

from db import get_connection
from auth import require_roles
from models import StudentCreate, StudentUpdate


router = APIRouter(prefix="/students", tags=["Students"])


def validate_class_exists(cursor, class_id: Optional[int]):
    if class_id is None:
        return

    cursor.execute(
        "SELECT id FROM classes WHERE id = %s",
        (class_id,)
    )

    class_data = cursor.fetchone()

    if class_data is None:
        raise HTTPException(status_code=404, detail="Class not found")


@router.get("")
def get_students(
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
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


@router.post("")
def create_student(
    student: StudentCreate,
    current_user=Depends(require_roles(["admin", "secretary"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        validate_class_exists(cursor, student.class_id)

        cursor.execute(
            """
            INSERT INTO students 
            (full_name, student_number, card_uid, class_id)
            VALUES (%s, %s, %s, %s)
            """,
            (
                student.full_name,
                student.student_number,
                student.card_uid,
                student.class_id
            )
        )

        connection.commit()
        new_id = cursor.lastrowid

    except IntegrityError:
        connection.rollback()
        raise HTTPException(
            status_code=409,
            detail="Student number or card UID already exists"
        )

    finally:
        cursor.close()
        connection.close()

    return {
        "message": "Student created successfully",
        "student_id": new_id
    }


@router.put("/{student_id}")
def update_student(
    student_id: int,
    student: StudentUpdate,
    current_user=Depends(require_roles(["admin", "secretary"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT id FROM students WHERE id = %s",
        (student_id,)
    )

    existing_student = cursor.fetchone()

    if existing_student is None:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=404, detail="Student not found")

    update_fields = []
    values = []

    if student.full_name is not None:
        update_fields.append("full_name = %s")
        values.append(student.full_name)

    if student.student_number is not None:
        update_fields.append("student_number = %s")
        values.append(student.student_number)

    if student.card_uid is not None:
        update_fields.append("card_uid = %s")
        values.append(student.card_uid)

    if student.class_id is not None:
        validate_class_exists(cursor, student.class_id)
        update_fields.append("class_id = %s")
        values.append(student.class_id)

    if not update_fields:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=400, detail="No fields to update")

    values.append(student_id)

    try:
        cursor.execute(
            f"""
            UPDATE students
            SET {", ".join(update_fields)}
            WHERE id = %s
            """,
            values
        )

        connection.commit()

    except IntegrityError:
        connection.rollback()
        raise HTTPException(
            status_code=409,
            detail="Student number or card UID already exists"
        )

    finally:
        cursor.close()
        connection.close()

    return {
        "message": "Student updated successfully",
        "student_id": student_id
    }


@router.delete("/{student_id}")
def delete_student(
    student_id: int,
    current_user=Depends(require_roles(["admin", "secretary"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT id FROM students WHERE id = %s",
        (student_id,)
    )

    student = cursor.fetchone()

    if student is None:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=404, detail="Student not found")

    cursor.execute(
        "SELECT id FROM attendance_records WHERE student_id = %s LIMIT 1",
        (student_id,)
    )

    attendance = cursor.fetchone()

    if attendance is not None:
        cursor.close()
        connection.close()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete student with attendance records"
        )

    cursor.execute(
        "DELETE FROM students WHERE id = %s",
        (student_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "message": "Student deleted successfully",
        "student_id": student_id
    }