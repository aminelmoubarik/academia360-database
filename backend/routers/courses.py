from fastapi import APIRouter, Depends, HTTPException
from mysql.connector import IntegrityError

from auth import require_roles
from db import get_db
from models import CourseCreate, CourseUpdate
from utils import get_audit_username, model_to_dict

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.get("")
def get_courses(
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                CourseID AS id,
                Code AS code,
                Name AS name,
                InsertUsername AS insert_username,
                InsertDate AS insert_date,
                ChangeUsername AS change_username,
                ChangeDate AS change_date
            FROM Tbl_Courses
            ORDER BY CourseID
        """)

        return cursor.fetchall()

    finally:
        cursor.close()


@router.get("/{course_id}")
def get_course(
    course_id: int,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                CourseID AS id,
                Code AS code,
                Name AS name,
                InsertUsername AS insert_username,
                InsertDate AS insert_date,
                ChangeUsername AS change_username,
                ChangeDate AS change_date
            FROM Tbl_Courses
            WHERE CourseID = %s
        """, (course_id,))

        course = cursor.fetchone()

        if course is None:
            raise HTTPException(status_code=404, detail="Course not found")

        return course

    finally:
        cursor.close()


@router.post("")
def create_course(
    course: CourseCreate,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    cursor = connection.cursor(dictionary=True)

    audit_username = get_audit_username(current_user)

    try:
        cursor.execute("""
            INSERT INTO Tbl_Courses (
                Code,
                Name,
                InsertUsername
            )
            VALUES (%s, %s, %s)
        """, (
            course.code,
            course.name,
            audit_username
        ))

        connection.commit()

        return {
            "message": "Course created successfully",
            "course_id": cursor.lastrowid
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        cursor.close()


@router.put("/{course_id}")
def update_course(
    course_id: int,
    course: CourseUpdate,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    data = model_to_dict(course)

    if not data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    field_map = {
        "code": "Code",
        "name": "Name"
    }

    set_clauses = []
    values = []

    for api_field, db_field in field_map.items():
        if api_field in data:
            set_clauses.append(f"{db_field} = %s")
            values.append(data[api_field])

    if not set_clauses:
        raise HTTPException(status_code=400, detail="No valid fields provided for update")

    audit_username = get_audit_username(current_user)

    set_clauses.append("ChangeUsername = %s")
    values.append(audit_username)

    values.append(course_id)

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(f"""
            UPDATE Tbl_Courses
            SET {", ".join(set_clauses)}
            WHERE CourseID = %s
        """, tuple(values))

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Course not found")

        return {
            "message": "Course updated successfully",
            "course_id": course_id
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        cursor.close()


@router.delete("/{course_id}")
def delete_course(
    course_id: int,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            DELETE FROM Tbl_Courses
            WHERE CourseID = %s
        """, (course_id,))

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Course not found")

        return {
            "message": "Course deleted successfully",
            "course_id": course_id
        }

    except IntegrityError:
        connection.rollback()
        raise HTTPException(
            status_code=400,
            detail="Course cannot be deleted because it is being used by another record"
        )

    finally:
        cursor.close()