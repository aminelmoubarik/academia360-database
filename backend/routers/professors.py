from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from mysql.connector import IntegrityError

from db import get_connection
from auth import require_roles
from models import ProfessorCreate, ProfessorUpdate


router = APIRouter(prefix="/professors", tags=["Professors"])


def validate_user_exists(cursor, user_id: Optional[int]):
    if user_id is None:
        return

    cursor.execute(
        "SELECT id FROM users WHERE id = %s",
        (user_id,)
    )

    user = cursor.fetchone()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")


@router.get("")
def get_professors(
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            id,
            user_id,
            full_name,
            email
        FROM professors
    """)

    data = cursor.fetchall()

    cursor.close()
    connection.close()

    return data


@router.post("")
def create_professor(
    professor: ProfessorCreate,
    current_user=Depends(require_roles(["admin", "secretary"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        validate_user_exists(cursor, professor.user_id)

        cursor.execute(
            """
            INSERT INTO professors
            (user_id, full_name, email)
            VALUES (%s, %s, %s)
            """,
            (
                professor.user_id,
                professor.full_name,
                professor.email
            )
        )

        connection.commit()
        new_id = cursor.lastrowid

    except IntegrityError:
        connection.rollback()
        raise HTTPException(
            status_code=409,
            detail="Professor email or user already exists"
        )

    finally:
        cursor.close()
        connection.close()

    return {
        "message": "Professor created successfully",
        "professor_id": new_id
    }


@router.put("/{professor_id}")
def update_professor(
    professor_id: int,
    professor: ProfessorUpdate,
    current_user=Depends(require_roles(["admin", "secretary"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT id FROM professors WHERE id = %s",
        (professor_id,)
    )

    existing_professor = cursor.fetchone()

    if existing_professor is None:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=404, detail="Professor not found")

    update_fields = []
    values = []

    if professor.user_id is not None:
        validate_user_exists(cursor, professor.user_id)
        update_fields.append("user_id = %s")
        values.append(professor.user_id)

    if professor.full_name is not None:
        update_fields.append("full_name = %s")
        values.append(professor.full_name)

    if professor.email is not None:
        update_fields.append("email = %s")
        values.append(professor.email)

    if not update_fields:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=400, detail="No fields to update")

    values.append(professor_id)

    try:
        cursor.execute(
            f"""
            UPDATE professors
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
            detail="Professor email or user already exists"
        )

    finally:
        cursor.close()
        connection.close()

    return {
        "message": "Professor updated successfully",
        "professor_id": professor_id
    }


@router.delete("/{professor_id}")
def delete_professor(
    professor_id: int,
    current_user=Depends(require_roles(["admin", "secretary"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT id FROM professors WHERE id = %s",
        (professor_id,)
    )

    professor = cursor.fetchone()

    if professor is None:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=404, detail="Professor not found")

    related_checks = [
        ("generated_schedule", "Professor has generated schedules"),
        ("teacher_availability", "Professor has availability records"),
        ("professor_disciplines", "Professor has discipline assignments")
    ]

    for table_name, error_message in related_checks:
        cursor.execute(
            f"SELECT professor_id FROM {table_name} WHERE professor_id = %s LIMIT 1",
            (professor_id,)
        )

        related_record = cursor.fetchone()

        if related_record is not None:
            cursor.close()
            connection.close()
            raise HTTPException(
                status_code=409,
                detail=error_message
            )

    cursor.execute(
        "DELETE FROM professors WHERE id = %s",
        (professor_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "message": "Professor deleted successfully",
        "professor_id": professor_id
    }