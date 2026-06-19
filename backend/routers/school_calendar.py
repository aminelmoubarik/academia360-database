from fastapi import APIRouter, Depends, HTTPException
from mysql.connector import IntegrityError

from auth import require_roles
from db import get_db
from models import SchoolCalendarCreate, SchoolCalendarUpdate
from utils import get_audit_username, model_to_dict

router = APIRouter(prefix="/school-calendar", tags=["School Calendar"])


@router.get("")
def get_school_calendar(
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                sc.CalendarID AS id,
                sc.SchoolYearID AS school_year_id,
                sy.Name AS school_year,
                sc.CalendarDate AS calendar_date,
                sc.IsSchoolDay AS is_school_day,
                sc.Description AS description,
                sc.InsertUsername AS insert_username,
                sc.InsertDate AS insert_date,
                sc.ChangeUsername AS change_username,
                sc.ChangeDate AS change_date
            FROM Tbl_SchoolCalendar sc
            JOIN Tref_SchoolYears sy ON sc.SchoolYearID = sy.SchoolYearID
            ORDER BY sc.CalendarDate
        """)

        return cursor.fetchall()

    finally:
        cursor.close()


@router.get("/school-year/{school_year_id}")
def get_school_calendar_by_school_year(
    school_year_id: int,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                sc.CalendarID AS id,
                sc.SchoolYearID AS school_year_id,
                sy.Name AS school_year,
                sc.CalendarDate AS calendar_date,
                sc.IsSchoolDay AS is_school_day,
                sc.Description AS description
            FROM Tbl_SchoolCalendar sc
            JOIN Tref_SchoolYears sy ON sc.SchoolYearID = sy.SchoolYearID
            WHERE sc.SchoolYearID = %s
            ORDER BY sc.CalendarDate
        """, (school_year_id,))

        return cursor.fetchall()

    finally:
        cursor.close()


@router.get("/{calendar_id}")
def get_school_calendar_record(
    calendar_id: int,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                sc.CalendarID AS id,
                sc.SchoolYearID AS school_year_id,
                sy.Name AS school_year,
                sc.CalendarDate AS calendar_date,
                sc.IsSchoolDay AS is_school_day,
                sc.Description AS description,
                sc.InsertUsername AS insert_username,
                sc.InsertDate AS insert_date,
                sc.ChangeUsername AS change_username,
                sc.ChangeDate AS change_date
            FROM Tbl_SchoolCalendar sc
            JOIN Tref_SchoolYears sy ON sc.SchoolYearID = sy.SchoolYearID
            WHERE sc.CalendarID = %s
        """, (calendar_id,))

        record = cursor.fetchone()

        if record is None:
            raise HTTPException(
                status_code=404,
                detail="School calendar record not found"
            )

        return record

    finally:
        cursor.close()


@router.post("")
def create_school_calendar_record(
    calendar: SchoolCalendarCreate,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin"]))
):
    cursor = connection.cursor(dictionary=True)

    audit_username = get_audit_username(current_user)

    try:
        cursor.execute("""
            INSERT INTO Tbl_SchoolCalendar (
                SchoolYearID,
                CalendarDate,
                IsSchoolDay,
                Description,
                InsertUsername
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            calendar.school_year_id,
            calendar.calendar_date,
            calendar.is_school_day,
            calendar.description,
            audit_username
        ))

        connection.commit()

        return {
            "message": "School calendar record created successfully",
            "calendar_id": cursor.lastrowid
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        cursor.close()


@router.put("/{calendar_id}")
def update_school_calendar_record(
    calendar_id: int,
    calendar: SchoolCalendarUpdate,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin"]))
):
    data = model_to_dict(calendar)

    if not data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    field_map = {
        "school_year_id": "SchoolYearID",
        "calendar_date": "CalendarDate",
        "is_school_day": "IsSchoolDay",
        "description": "Description"
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

    values.append(calendar_id)

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(f"""
            UPDATE Tbl_SchoolCalendar
            SET {", ".join(set_clauses)}
            WHERE CalendarID = %s
        """, tuple(values))

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="School calendar record not found"
            )

        return {
            "message": "School calendar record updated successfully",
            "calendar_id": calendar_id
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        cursor.close()


@router.delete("/{calendar_id}")
def delete_school_calendar_record(
    calendar_id: int,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin"]))
):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            DELETE FROM Tbl_SchoolCalendar
            WHERE CalendarID = %s
        """, (calendar_id,))

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="School calendar record not found"
            )

        return {
            "message": "School calendar record deleted successfully",
            "calendar_id": calendar_id
        }

    except IntegrityError:
        connection.rollback()
        raise HTTPException(
            status_code=400,
            detail="School calendar record cannot be deleted because it is being used by another record"
        )

    finally:
        cursor.close()