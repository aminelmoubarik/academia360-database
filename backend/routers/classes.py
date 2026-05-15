from fastapi import APIRouter, Depends, HTTPException
from mysql.connector import IntegrityError

from auth import require_roles
from db import get_connection
from models import ClassCreate, ClassUpdate

router = APIRouter(prefix="/classes", tags=["Classes"])


def get_audit_username(current_user):
    if isinstance(current_user, dict):
        return (
            current_user.get("email")
            or current_user.get("Email")
            or current_user.get("full_name")
            or current_user.get("FullName")
            or "api"
        )
    return "api"


def model_to_dict(model):
    if hasattr(model, "model_dump"):
        return model.model_dump(exclude_unset=True)
    return model.dict(exclude_unset=True)


@router.get("")
def get_classes(
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                cl.ClassID AS id,
                cl.Name AS name,
                cl.CourseID AS course_id,
                c.Code AS course_code,
                c.Name AS course_name,
                cl.SchoolYearID AS school_year_id,
                sy.Name AS school_year,
                cl.CourseYearNumber AS course_year_number,
                cl.InsertUsername AS insert_username,
                cl.InsertDate AS insert_date,
                cl.ChangeUsername AS change_username,
                cl.ChangeDate AS change_date
            FROM Tbl_Classes cl
            JOIN Tbl_Courses c ON cl.CourseID = c.CourseID
            JOIN Tref_SchoolYears sy ON cl.SchoolYearID = sy.SchoolYearID
            ORDER BY cl.ClassID
        """)

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


@router.get("/{class_id}")
def get_class(
    class_id: int,
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                cl.ClassID AS id,
                cl.Name AS name,
                cl.CourseID AS course_id,
                c.Code AS course_code,
                c.Name AS course_name,
                cl.SchoolYearID AS school_year_id,
                sy.Name AS school_year,
                cl.CourseYearNumber AS course_year_number,
                cl.InsertUsername AS insert_username,
                cl.InsertDate AS insert_date,
                cl.ChangeUsername AS change_username,
                cl.ChangeDate AS change_date
            FROM Tbl_Classes cl
            JOIN Tbl_Courses c ON cl.CourseID = c.CourseID
            JOIN Tref_SchoolYears sy ON cl.SchoolYearID = sy.SchoolYearID
            WHERE cl.ClassID = %s
        """, (class_id,))

        class_record = cursor.fetchone()

        if class_record is None:
            raise HTTPException(status_code=404, detail="Class not found")

        return class_record

    finally:
        cursor.close()
        connection.close()


@router.post("")
def create_class(
    class_data: ClassCreate,
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    if class_data.course_year_number <= 0:
        raise HTTPException(
            status_code=400,
            detail="Course year number must be greater than 0"
        )

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    audit_username = get_audit_username(current_user)

    try:
        cursor.execute("""
            INSERT INTO Tbl_Classes (
                Name,
                CourseID,
                SchoolYearID,
                CourseYearNumber,
                InsertUsername
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            class_data.name,
            class_data.course_id,
            class_data.school_year_id,
            class_data.course_year_number,
            audit_username
        ))

        connection.commit()

        return {
            "message": "Class created successfully",
            "class_id": cursor.lastrowid
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        cursor.close()
        connection.close()


@router.put("/{class_id}")
def update_class(
    class_id: int,
    class_data: ClassUpdate,
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    data = model_to_dict(class_data)

    if not data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    if "course_year_number" in data and data["course_year_number"] <= 0:
        raise HTTPException(
            status_code=400,
            detail="Course year number must be greater than 0"
        )

    field_map = {
        "name": "Name",
        "course_id": "CourseID",
        "school_year_id": "SchoolYearID",
        "course_year_number": "CourseYearNumber"
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

    values.append(class_id)

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(f"""
            UPDATE Tbl_Classes
            SET {", ".join(set_clauses)}
            WHERE ClassID = %s
        """, tuple(values))

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Class not found")

        return {
            "message": "Class updated successfully",
            "class_id": class_id
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        cursor.close()
        connection.close()


@router.delete("/{class_id}")
def delete_class(
    class_id: int,
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            DELETE FROM Tbl_Classes
            WHERE ClassID = %s
        """, (class_id,))

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Class not found")

        return {
            "message": "Class deleted successfully",
            "class_id": class_id
        }

    except IntegrityError:
        connection.rollback()
        raise HTTPException(
            status_code=400,
            detail="Class cannot be deleted because it is being used by another record"
        )

    finally:
        cursor.close()
        connection.close()