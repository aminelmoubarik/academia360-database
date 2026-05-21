from fastapi import APIRouter, Depends, HTTPException
from mysql.connector import IntegrityError

from auth import require_roles
from db import get_db
from models import StudentCreate, StudentUpdate
from utils import get_audit_username, model_to_dict

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("")
def get_students(
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                s.StudentID AS id,
                s.FullName AS full_name,
                s.StudentNumber AS student_number,
                s.CardUID AS card_uid,
                s.ClassID AS class_id,
                cl.Name AS class_name,
                c.CourseID AS course_id,
                c.Code AS course_code,
                c.Name AS course_name,
                sy.SchoolYearID AS school_year_id,
                sy.Name AS school_year,
                s.PhotoPath AS photo_path,
                s.GenderID AS gender_id,
                g.Name AS gender,
                s.Address AS address,
                s.PostalCode AS postal_code,
                s.City AS city,
                s.Contact AS contact,
                s.DateOfBirth AS date_of_birth,
                s.InsertUsername AS insert_username,
                s.InsertDate AS insert_date,
                s.ChangeUsername AS change_username,
                s.ChangeDate AS change_date
            FROM Tbl_Students s
            LEFT JOIN Tbl_Classes cl ON s.ClassID = cl.ClassID
            LEFT JOIN Tbl_Courses c ON cl.CourseID = c.CourseID
            LEFT JOIN Tref_SchoolYears sy ON cl.SchoolYearID = sy.SchoolYearID
            LEFT JOIN Tref_Gender g ON s.GenderID = g.GenderID
            ORDER BY s.StudentID
        """)

        return cursor.fetchall()

    finally:
        cursor.close()


@router.get("/{student_id}")
def get_student(
    student_id: int,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                s.StudentID AS id,
                s.FullName AS full_name,
                s.StudentNumber AS student_number,
                s.CardUID AS card_uid,
                s.ClassID AS class_id,
                cl.Name AS class_name,
                c.CourseID AS course_id,
                c.Code AS course_code,
                c.Name AS course_name,
                sy.SchoolYearID AS school_year_id,
                sy.Name AS school_year,
                s.PhotoPath AS photo_path,
                s.GenderID AS gender_id,
                g.Name AS gender,
                s.Address AS address,
                s.PostalCode AS postal_code,
                s.City AS city,
                s.Contact AS contact,
                s.DateOfBirth AS date_of_birth,
                s.InsertUsername AS insert_username,
                s.InsertDate AS insert_date,
                s.ChangeUsername AS change_username,
                s.ChangeDate AS change_date
            FROM Tbl_Students s
            LEFT JOIN Tbl_Classes cl ON s.ClassID = cl.ClassID
            LEFT JOIN Tbl_Courses c ON cl.CourseID = c.CourseID
            LEFT JOIN Tref_SchoolYears sy ON cl.SchoolYearID = sy.SchoolYearID
            LEFT JOIN Tref_Gender g ON s.GenderID = g.GenderID
            WHERE s.StudentID = %s
        """, (student_id,))

        student = cursor.fetchone()

        if student is None:
            raise HTTPException(status_code=404, detail="Student not found")

        return student

    finally:
        cursor.close()


@router.post("")
def create_student(
    student: StudentCreate,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    cursor = connection.cursor(dictionary=True)

    audit_username = get_audit_username(current_user)

    try:
        cursor.execute("""
            INSERT INTO Tbl_Students (
                FullName,
                StudentNumber,
                CardUID,
                ClassID,
                PhotoPath,
                GenderID,
                Address,
                PostalCode,
                City,
                Contact,
                DateOfBirth,
                InsertUsername
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            student.full_name,
            student.student_number,
            student.card_uid,
            student.class_id,
            student.photo_path,
            student.gender_id,
            student.address,
            student.postal_code,
            student.city,
            student.contact,
            student.date_of_birth,
            audit_username
        ))

        connection.commit()

        return {
            "message": "Student created successfully",
            "student_id": cursor.lastrowid
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        cursor.close()


@router.put("/{student_id}")
def update_student(
    student_id: int,
    student: StudentUpdate,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    data = model_to_dict(student)

    if not data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    field_map = {
        "full_name": "FullName",
        "student_number": "StudentNumber",
        "card_uid": "CardUID",
        "class_id": "ClassID",
        "photo_path": "PhotoPath",
        "gender_id": "GenderID",
        "address": "Address",
        "postal_code": "PostalCode",
        "city": "City",
        "contact": "Contact",
        "date_of_birth": "DateOfBirth"
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

    values.append(student_id)

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(f"""
            UPDATE Tbl_Students
            SET {", ".join(set_clauses)}
            WHERE StudentID = %s
        """, tuple(values))

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Student not found")

        return {
            "message": "Student updated successfully",
            "student_id": student_id
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        cursor.close()


@router.delete("/{student_id}")
def delete_student(
    student_id: int,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            DELETE FROM Tbl_Students
            WHERE StudentID = %s
        """, (student_id,))

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Student not found")

        return {
            "message": "Student deleted successfully",
            "student_id": student_id
        }

    except IntegrityError:
        connection.rollback()
        raise HTTPException(
            status_code=400,
            detail="Student cannot be deleted because it is being used by another record"
        )

    finally:
        cursor.close()