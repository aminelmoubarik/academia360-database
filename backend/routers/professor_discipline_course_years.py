from fastapi import APIRouter, Depends, HTTPException
from mysql.connector import IntegrityError

from auth import require_roles
from db import get_connection
from models import ProfessorDisciplineCourseYearCreate

router = APIRouter(
    prefix="/professor-discipline-course-years",
    tags=["Professor Discipline Course Years"]
)


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


@router.get("")
def get_professor_discipline_course_years(
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                pd.ProfessorID AS professor_id,
                u.FullName AS professor_name,
                u.Email AS professor_email,
                pd.DisciplineCourseYearID AS discipline_course_year_id,
                d.DisciplineID AS discipline_id,
                d.Name AS discipline_name,
                d.Code AS discipline_code,
                c.CourseID AS course_id,
                c.Code AS course_code,
                c.Name AS course_name,
                sy.SchoolYearID AS school_year_id,
                sy.Name AS school_year,
                dc.CourseYearNumber AS course_year_number,
                dc.TotalMinutes AS total_minutes,
                ROUND(dc.TotalMinutes / 60, 2) AS total_hours,
                dc.LessonDurationMinutes AS lesson_duration_minutes,
                dc.IsPractical AS is_practical,
                pd.InsertUsername AS insert_username,
                pd.InsertDate AS insert_date,
                pd.ChangeUsername AS change_username,
                pd.ChangeDate AS change_date
            FROM trx_Professor_DisciplineCourseYear pd
            JOIN Tbl_Professors p 
                ON pd.ProfessorID = p.ProfessorID
            JOIN Tbl_Users u 
                ON p.UserID = u.UserID
            JOIN trx_Discipline_CourseYear dc 
                ON pd.DisciplineCourseYearID = dc.DisciplineCourseYearID
            JOIN Tbl_Disciplines d 
                ON dc.DisciplineID = d.DisciplineID
            JOIN Tbl_Courses c 
                ON dc.CourseID = c.CourseID
            JOIN Tref_SchoolYears sy 
                ON dc.SchoolYearID = sy.SchoolYearID
            ORDER BY pd.ProfessorID, pd.DisciplineCourseYearID
        """)

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()



@router.get("/professor/{professor_id}")
def get_disciplines_by_professor(
    professor_id: int,
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                pd.ProfessorID AS professor_id,
                u.FullName AS professor_name,
                pd.DisciplineCourseYearID AS discipline_course_year_id,
                d.DisciplineID AS discipline_id,
                d.Name AS discipline_name,
                d.Code AS discipline_code,
                c.CourseID AS course_id,
                c.Code AS course_code,
                c.Name AS course_name,
                sy.SchoolYearID AS school_year_id,
                sy.Name AS school_year,
                dc.CourseYearNumber AS course_year_number,
                dc.TotalMinutes AS total_minutes,
                ROUND(dc.TotalMinutes / 60, 2) AS total_hours,
                dc.LessonDurationMinutes AS lesson_duration_minutes,
                dc.IsPractical AS is_practical
            FROM trx_Professor_DisciplineCourseYear pd
            JOIN Tbl_Professors p 
                ON pd.ProfessorID = p.ProfessorID
            JOIN Tbl_Users u 
                ON p.UserID = u.UserID
            JOIN trx_Discipline_CourseYear dc 
                ON pd.DisciplineCourseYearID = dc.DisciplineCourseYearID
            JOIN Tbl_Disciplines d 
                ON dc.DisciplineID = d.DisciplineID
            JOIN Tbl_Courses c 
                ON dc.CourseID = c.CourseID
            JOIN Tref_SchoolYears sy 
                ON dc.SchoolYearID = sy.SchoolYearID
            WHERE pd.ProfessorID = %s
            ORDER BY d.Name, c.Code, sy.Name
        """, (professor_id,))

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


@router.get("/discipline-course-year/{discipline_course_year_id}")
def get_professors_by_discipline_course_year(
    discipline_course_year_id: int,
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                pd.DisciplineCourseYearID AS discipline_course_year_id,
                pd.ProfessorID AS professor_id,
                u.FullName AS professor_name,
                u.Email AS professor_email,
                d.Name AS discipline_name,
                c.Code AS course_code,
                sy.Name AS school_year,
                dc.CourseYearNumber AS course_year_number
            FROM trx_Professor_DisciplineCourseYear pd
            JOIN Tbl_Professors p 
                ON pd.ProfessorID = p.ProfessorID
            JOIN Tbl_Users u 
                ON p.UserID = u.UserID
            JOIN trx_Discipline_CourseYear dc 
                ON pd.DisciplineCourseYearID = dc.DisciplineCourseYearID
            JOIN Tbl_Disciplines d 
                ON dc.DisciplineID = d.DisciplineID
            JOIN Tbl_Courses c 
                ON dc.CourseID = c.CourseID
            JOIN Tref_SchoolYears sy 
                ON dc.SchoolYearID = sy.SchoolYearID
            WHERE pd.DisciplineCourseYearID = %s
            ORDER BY u.FullName
        """, (discipline_course_year_id,))

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


@router.get("/{professor_id}/{discipline_course_year_id}")
def get_professor_discipline_course_year(
    professor_id: int,
    discipline_course_year_id: int,
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                pd.ProfessorID AS professor_id,
                u.FullName AS professor_name,
                u.Email AS professor_email,
                pd.DisciplineCourseYearID AS discipline_course_year_id,
                d.DisciplineID AS discipline_id,
                d.Name AS discipline_name,
                d.Code AS discipline_code,
                c.CourseID AS course_id,
                c.Code AS course_code,
                c.Name AS course_name,
                sy.SchoolYearID AS school_year_id,
                sy.Name AS school_year,
                dc.CourseYearNumber AS course_year_number,
                dc.TotalMinutes AS total_minutes,
                ROUND(dc.TotalMinutes / 60, 2) AS total_hours,
                dc.LessonDurationMinutes AS lesson_duration_minutes,
                dc.IsPractical AS is_practical,
                pd.InsertUsername AS insert_username,
                pd.InsertDate AS insert_date,
                pd.ChangeUsername AS change_username,
                pd.ChangeDate AS change_date
            FROM trx_Professor_DisciplineCourseYear pd
            JOIN Tbl_Professors p 
                ON pd.ProfessorID = p.ProfessorID
            JOIN Tbl_Users u 
                ON p.UserID = u.UserID
            JOIN trx_Discipline_CourseYear dc 
                ON pd.DisciplineCourseYearID = dc.DisciplineCourseYearID
            JOIN Tbl_Disciplines d 
                ON dc.DisciplineID = d.DisciplineID
            JOIN Tbl_Courses c 
                ON dc.CourseID = c.CourseID
            JOIN Tref_SchoolYears sy 
                ON dc.SchoolYearID = sy.SchoolYearID
            WHERE pd.ProfessorID = %s
              AND pd.DisciplineCourseYearID = %s
        """, (
            professor_id,
            discipline_course_year_id
        ))

        record = cursor.fetchone()

        if record is None:
            raise HTTPException(
                status_code=404,
                detail="Professor discipline course year record not found"
            )

        return record

    finally:
        cursor.close()
        connection.close()

@router.post("")
def create_professor_discipline_course_year(
    relation: ProfessorDisciplineCourseYearCreate,
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    audit_username = get_audit_username(current_user)

    try:
        cursor.execute("""
            INSERT INTO trx_Professor_DisciplineCourseYear (
                ProfessorID,
                DisciplineCourseYearID,
                InsertUsername
            )
            VALUES (%s, %s, %s)
        """, (
            relation.professor_id,
            relation.discipline_course_year_id,
            audit_username
        ))

        connection.commit()

        return {
            "message": "Professor assigned to discipline course year successfully",
            "professor_id": relation.professor_id,
            "discipline_course_year_id": relation.discipline_course_year_id
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        cursor.close()
        connection.close()


@router.delete("/{professor_id}/{discipline_course_year_id}")
def delete_professor_discipline_course_year(
    professor_id: int,
    discipline_course_year_id: int,
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            DELETE FROM trx_Professor_DisciplineCourseYear
            WHERE ProfessorID = %s
              AND DisciplineCourseYearID = %s
        """, (
            professor_id,
            discipline_course_year_id
        ))

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Professor discipline course year record not found"
            )

        return {
            "message": "Professor assignment deleted successfully",
            "professor_id": professor_id,
            "discipline_course_year_id": discipline_course_year_id
        }

    except IntegrityError:
        connection.rollback()
        raise HTTPException(
            status_code=400,
            detail="Professor assignment cannot be deleted because it is being used by another record"
        )

    finally:
        cursor.close()
        connection.close()