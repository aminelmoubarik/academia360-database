from fastapi import APIRouter, Depends, HTTPException
from mysql.connector import IntegrityError

from auth import require_roles
from db import get_connection
from models import ProfessorCreate, ProfessorUpdate
from utils import get_audit_username, model_to_dict

router = APIRouter(prefix="/professors", tags=["Professors"])


@router.get("")
def get_professors(
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                p.ProfessorID AS id,
                p.UserID AS user_id,
                u.FullName AS full_name,
                u.Email AS email,
                r.Name AS role,
                p.PhotoPath AS photo_path,
                p.GenderID AS gender_id,
                g.Name AS gender,
                p.Address AS address,
                p.PostalCode AS postal_code,
                p.City AS city,
                p.Contact AS contact,
                p.DateOfBirth AS date_of_birth,
                GROUP_CONCAT(
                    DISTINCT CONCAT(d.Name, ' - ', c.Code, ' - ', sy.Name)
                    SEPARATOR ', '
                ) AS disciplines,
                p.InsertUsername AS insert_username,
                p.InsertDate AS insert_date,
                p.ChangeUsername AS change_username,
                p.ChangeDate AS change_date
            FROM Tbl_Professors p
            JOIN Tbl_Users u ON p.UserID = u.UserID
            JOIN Tref_UserRoles r ON u.RoleID = r.RoleID
            LEFT JOIN Tref_Gender g ON p.GenderID = g.GenderID
            LEFT JOIN trx_Professor_DisciplineCourseYear pd 
                ON p.ProfessorID = pd.ProfessorID
            LEFT JOIN trx_Discipline_CourseYear dc 
                ON pd.DisciplineCourseYearID = dc.DisciplineCourseYearID
            LEFT JOIN Tbl_Disciplines d 
                ON dc.DisciplineID = d.DisciplineID
            LEFT JOIN Tbl_Courses c 
                ON dc.CourseID = c.CourseID
            LEFT JOIN Tref_SchoolYears sy 
                ON dc.SchoolYearID = sy.SchoolYearID
            GROUP BY
                p.ProfessorID,
                p.UserID,
                u.FullName,
                u.Email,
                r.Name,
                p.PhotoPath,
                p.GenderID,
                g.Name,
                p.Address,
                p.PostalCode,
                p.City,
                p.Contact,
                p.DateOfBirth,
                p.InsertUsername,
                p.InsertDate,
                p.ChangeUsername,
                p.ChangeDate
            ORDER BY p.ProfessorID
        """)

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


@router.get("/{professor_id}")
def get_professor(
    professor_id: int,
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                p.ProfessorID AS id,
                p.UserID AS user_id,
                u.FullName AS full_name,
                u.Email AS email,
                r.Name AS role,
                p.PhotoPath AS photo_path,
                p.GenderID AS gender_id,
                g.Name AS gender,
                p.Address AS address,
                p.PostalCode AS postal_code,
                p.City AS city,
                p.Contact AS contact,
                p.DateOfBirth AS date_of_birth,
                GROUP_CONCAT(
                    DISTINCT CONCAT(d.Name, ' - ', c.Code, ' - ', sy.Name)
                    SEPARATOR ', '
                ) AS disciplines,
                p.InsertUsername AS insert_username,
                p.InsertDate AS insert_date,
                p.ChangeUsername AS change_username,
                p.ChangeDate AS change_date
            FROM Tbl_Professors p
            JOIN Tbl_Users u ON p.UserID = u.UserID
            JOIN Tref_UserRoles r ON u.RoleID = r.RoleID
            LEFT JOIN Tref_Gender g ON p.GenderID = g.GenderID
            LEFT JOIN trx_Professor_DisciplineCourseYear pd 
                ON p.ProfessorID = pd.ProfessorID
            LEFT JOIN trx_Discipline_CourseYear dc 
                ON pd.DisciplineCourseYearID = dc.DisciplineCourseYearID
            LEFT JOIN Tbl_Disciplines d 
                ON dc.DisciplineID = d.DisciplineID
            LEFT JOIN Tbl_Courses c 
                ON dc.CourseID = c.CourseID
            LEFT JOIN Tref_SchoolYears sy 
                ON dc.SchoolYearID = sy.SchoolYearID
            WHERE p.ProfessorID = %s
            GROUP BY
                p.ProfessorID,
                p.UserID,
                u.FullName,
                u.Email,
                r.Name,
                p.PhotoPath,
                p.GenderID,
                g.Name,
                p.Address,
                p.PostalCode,
                p.City,
                p.Contact,
                p.DateOfBirth,
                p.InsertUsername,
                p.InsertDate,
                p.ChangeUsername,
                p.ChangeDate
        """, (professor_id,))

        professor = cursor.fetchone()

        if professor is None:
            raise HTTPException(status_code=404, detail="Professor not found")

        return professor

    finally:
        cursor.close()
        connection.close()


@router.post("")
def create_professor(
    professor: ProfessorCreate,
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    audit_username = get_audit_username(current_user)

    try:
        cursor.execute("""
            INSERT INTO Tbl_Professors (
                UserID,
                PhotoPath,
                GenderID,
                Address,
                PostalCode,
                City,
                Contact,
                DateOfBirth,
                InsertUsername
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            professor.user_id,
            professor.photo_path,
            professor.gender_id,
            professor.address,
            professor.postal_code,
            professor.city,
            professor.contact,
            professor.date_of_birth,
            audit_username
        ))

        connection.commit()

        return {
            "message": "Professor created successfully",
            "professor_id": cursor.lastrowid
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        cursor.close()
        connection.close()


@router.put("/{professor_id}")
def update_professor(
    professor_id: int,
    professor: ProfessorUpdate,
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    data = model_to_dict(professor)

    if not data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    field_map = {
        "user_id": "UserID",
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

    values.append(professor_id)

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(f"""
            UPDATE Tbl_Professors
            SET {", ".join(set_clauses)}
            WHERE ProfessorID = %s
        """, tuple(values))

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Professor not found")

        return {
            "message": "Professor updated successfully",
            "professor_id": professor_id
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        cursor.close()
        connection.close()


@router.delete("/{professor_id}")
def delete_professor(
    professor_id: int,
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            DELETE FROM Tbl_Professors
            WHERE ProfessorID = %s
        """, (professor_id,))

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Professor not found")

        return {
            "message": "Professor deleted successfully",
            "professor_id": professor_id
        }

    except IntegrityError:
        connection.rollback()
        raise HTTPException(
            status_code=400,
            detail="Professor cannot be deleted because it is being used by another record"
        )

    finally:
        cursor.close()
        connection.close()