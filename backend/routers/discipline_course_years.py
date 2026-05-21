from fastapi import APIRouter, Depends, HTTPException
from mysql.connector import IntegrityError

from auth import require_roles
from db import get_db
from models import DisciplineCourseYearCreate, DisciplineCourseYearUpdate
from utils import get_audit_username, model_to_dict

router = APIRouter(prefix="/discipline-course-years", tags=["Discipline Course Years"])


def validate_positive_values(data):
    if "course_year_number" in data and data["course_year_number"] is not None:
        if data["course_year_number"] <= 0:
            raise HTTPException(
                status_code=400,
                detail="Course year number must be greater than 0"
            )

    if "total_minutes" in data and data["total_minutes"] is not None:
        if data["total_minutes"] <= 0:
            raise HTTPException(
                status_code=400,
                detail="Total minutes must be greater than 0"
            )

    if "lesson_duration_minutes" in data and data["lesson_duration_minutes"] is not None:
        if data["lesson_duration_minutes"] <= 0:
            raise HTTPException(
                status_code=400,
                detail="Lesson duration minutes must be greater than 0"
            )


@router.get("")
def get_discipline_course_years(
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                dc.DisciplineCourseYearID AS id,
                dc.DisciplineID AS discipline_id,
                d.Name AS discipline_name,
                d.Code AS discipline_code,
                dc.CourseID AS course_id,
                c.Code AS course_code,
                c.Name AS course_name,
                dc.SchoolYearID AS school_year_id,
                sy.Name AS school_year,
                dc.CourseYearNumber AS course_year_number,
                dc.TotalMinutes AS total_minutes,
                ROUND(dc.TotalMinutes / 60, 2) AS total_hours,
                dc.LessonDurationMinutes AS lesson_duration_minutes,
                dc.IsPractical AS is_practical,
                dc.InsertUsername AS insert_username,
                dc.InsertDate AS insert_date,
                dc.ChangeUsername AS change_username,
                dc.ChangeDate AS change_date
            FROM trx_Discipline_CourseYear dc
            JOIN Tbl_Disciplines d ON dc.DisciplineID = d.DisciplineID
            JOIN Tbl_Courses c ON dc.CourseID = c.CourseID
            JOIN Tref_SchoolYears sy ON dc.SchoolYearID = sy.SchoolYearID
            ORDER BY dc.DisciplineCourseYearID
        """)

        return cursor.fetchall()

    finally:
        cursor.close()


@router.get("/{discipline_course_year_id}")
def get_discipline_course_year(
    discipline_course_year_id: int,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                dc.DisciplineCourseYearID AS id,
                dc.DisciplineID AS discipline_id,
                d.Name AS discipline_name,
                d.Code AS discipline_code,
                dc.CourseID AS course_id,
                c.Code AS course_code,
                c.Name AS course_name,
                dc.SchoolYearID AS school_year_id,
                sy.Name AS school_year,
                dc.CourseYearNumber AS course_year_number,
                dc.TotalMinutes AS total_minutes,
                ROUND(dc.TotalMinutes / 60, 2) AS total_hours,
                dc.LessonDurationMinutes AS lesson_duration_minutes,
                dc.IsPractical AS is_practical,
                dc.InsertUsername AS insert_username,
                dc.InsertDate AS insert_date,
                dc.ChangeUsername AS change_username,
                dc.ChangeDate AS change_date
            FROM trx_Discipline_CourseYear dc
            JOIN Tbl_Disciplines d ON dc.DisciplineID = d.DisciplineID
            JOIN Tbl_Courses c ON dc.CourseID = c.CourseID
            JOIN Tref_SchoolYears sy ON dc.SchoolYearID = sy.SchoolYearID
            WHERE dc.DisciplineCourseYearID = %s
        """, (discipline_course_year_id,))

        record = cursor.fetchone()

        if record is None:
            raise HTTPException(
                status_code=404,
                detail="Discipline course year record not found"
            )

        return record

    finally:
        cursor.close()


@router.post("")
def create_discipline_course_year(
    discipline_course_year: DisciplineCourseYearCreate,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    data = model_to_dict(discipline_course_year)
    validate_positive_values(data)

    cursor = connection.cursor(dictionary=True)

    audit_username = get_audit_username(current_user)

    try:
        cursor.execute("""
            INSERT INTO trx_Discipline_CourseYear (
                DisciplineID,
                CourseID,
                SchoolYearID,
                CourseYearNumber,
                TotalMinutes,
                LessonDurationMinutes,
                IsPractical,
                InsertUsername
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            discipline_course_year.discipline_id,
            discipline_course_year.course_id,
            discipline_course_year.school_year_id,
            discipline_course_year.course_year_number,
            discipline_course_year.total_minutes,
            discipline_course_year.lesson_duration_minutes,
            discipline_course_year.is_practical,
            audit_username
        ))

        connection.commit()

        return {
            "message": "Discipline course year record created successfully",
            "discipline_course_year_id": cursor.lastrowid
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        cursor.close()


@router.put("/{discipline_course_year_id}")
def update_discipline_course_year(
    discipline_course_year_id: int,
    discipline_course_year: DisciplineCourseYearUpdate,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    data = model_to_dict(discipline_course_year)

    if not data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    validate_positive_values(data)

    field_map = {
        "discipline_id": "DisciplineID",
        "course_id": "CourseID",
        "school_year_id": "SchoolYearID",
        "course_year_number": "CourseYearNumber",
        "total_minutes": "TotalMinutes",
        "lesson_duration_minutes": "LessonDurationMinutes",
        "is_practical": "IsPractical"
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

    values.append(discipline_course_year_id)

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(f"""
            UPDATE trx_Discipline_CourseYear
            SET {", ".join(set_clauses)}
            WHERE DisciplineCourseYearID = %s
        """, tuple(values))

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Discipline course year record not found"
            )

        return {
            "message": "Discipline course year record updated successfully",
            "discipline_course_year_id": discipline_course_year_id
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        cursor.close()


@router.delete("/{discipline_course_year_id}")
def delete_discipline_course_year(
    discipline_course_year_id: int,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            DELETE FROM trx_Discipline_CourseYear
            WHERE DisciplineCourseYearID = %s
        """, (discipline_course_year_id,))

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Discipline course year record not found"
            )

        return {
            "message": "Discipline course year record deleted successfully",
            "discipline_course_year_id": discipline_course_year_id
        }

    except IntegrityError:
        connection.rollback()
        raise HTTPException(
            status_code=400,
            detail="Discipline course year record cannot be deleted because it is being used by another record"
        )

    finally:
        cursor.close()