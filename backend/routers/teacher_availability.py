from fastapi import APIRouter, Depends, HTTPException
from mysql.connector import IntegrityError

from auth import require_roles
from db import get_connection
from models import TeacherAvailabilityCreate, TeacherAvailabilityUpdate

router = APIRouter(prefix="/teacher-availability", tags=["Teacher Availability"])


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


def validate_time_range(start_time, end_time):
    if start_time is not None and end_time is not None:
        if end_time <= start_time:
            raise HTTPException(
                status_code=400,
                detail="End time must be greater than start time"
            )


@router.get("")
def get_teacher_availability(
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                ta.TeacherAvailabilityID AS id,
                ta.ProfessorID AS professor_id,
                u.FullName AS professor_name,
                u.Email AS professor_email,
                ta.SchoolYearID AS school_year_id,
                sy.Name AS school_year,
                ta.DayOfWeek AS day_of_week,
                ta.StartTime AS start_time,
                ta.EndTime AS end_time,
                ta.InsertUsername AS insert_username,
                ta.InsertDate AS insert_date,
                ta.ChangeUsername AS change_username,
                ta.ChangeDate AS change_date
            FROM Tbl_TeacherAvailability ta
            JOIN Tbl_Professors p ON ta.ProfessorID = p.ProfessorID
            JOIN Tbl_Users u ON p.UserID = u.UserID
            JOIN Tref_SchoolYears sy ON ta.SchoolYearID = sy.SchoolYearID
            ORDER BY ta.ProfessorID, ta.DayOfWeek, ta.StartTime
        """)

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


@router.get("/{availability_id}")
def get_teacher_availability_record(
    availability_id: int,
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                ta.TeacherAvailabilityID AS id,
                ta.ProfessorID AS professor_id,
                u.FullName AS professor_name,
                u.Email AS professor_email,
                ta.SchoolYearID AS school_year_id,
                sy.Name AS school_year,
                ta.DayOfWeek AS day_of_week,
                ta.StartTime AS start_time,
                ta.EndTime AS end_time,
                ta.InsertUsername AS insert_username,
                ta.InsertDate AS insert_date,
                ta.ChangeUsername AS change_username,
                ta.ChangeDate AS change_date
            FROM Tbl_TeacherAvailability ta
            JOIN Tbl_Professors p ON ta.ProfessorID = p.ProfessorID
            JOIN Tbl_Users u ON p.UserID = u.UserID
            JOIN Tref_SchoolYears sy ON ta.SchoolYearID = sy.SchoolYearID
            WHERE ta.TeacherAvailabilityID = %s
        """, (availability_id,))

        record = cursor.fetchone()

        if record is None:
            raise HTTPException(
                status_code=404,
                detail="Teacher availability record not found"
            )

        return record

    finally:
        cursor.close()
        connection.close()


@router.get("/professor/{professor_id}")
def get_availability_by_professor(
    professor_id: int,
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                ta.TeacherAvailabilityID AS id,
                ta.ProfessorID AS professor_id,
                u.FullName AS professor_name,
                ta.SchoolYearID AS school_year_id,
                sy.Name AS school_year,
                ta.DayOfWeek AS day_of_week,
                ta.StartTime AS start_time,
                ta.EndTime AS end_time
            FROM Tbl_TeacherAvailability ta
            JOIN Tbl_Professors p ON ta.ProfessorID = p.ProfessorID
            JOIN Tbl_Users u ON p.UserID = u.UserID
            JOIN Tref_SchoolYears sy ON ta.SchoolYearID = sy.SchoolYearID
            WHERE ta.ProfessorID = %s
            ORDER BY ta.DayOfWeek, ta.StartTime
        """, (professor_id,))

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


@router.post("")
def create_teacher_availability(
    availability: TeacherAvailabilityCreate,
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    validate_time_range(availability.start_time, availability.end_time)

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    audit_username = get_audit_username(current_user)

    try:
        cursor.execute("""
            INSERT INTO Tbl_TeacherAvailability (
                ProfessorID,
                SchoolYearID,
                DayOfWeek,
                StartTime,
                EndTime,
                InsertUsername
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            availability.professor_id,
            availability.school_year_id,
            availability.day_of_week,
            availability.start_time,
            availability.end_time,
            audit_username
        ))

        connection.commit()

        return {
            "message": "Teacher availability created successfully",
            "availability_id": cursor.lastrowid
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        cursor.close()
        connection.close()


@router.put("/{availability_id}")
def update_teacher_availability(
    availability_id: int,
    availability: TeacherAvailabilityUpdate,
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    data = model_to_dict(availability)

    if not data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    if "start_time" in data and "end_time" in data:
        validate_time_range(data["start_time"], data["end_time"])

    field_map = {
        "professor_id": "ProfessorID",
        "school_year_id": "SchoolYearID",
        "day_of_week": "DayOfWeek",
        "start_time": "StartTime",
        "end_time": "EndTime"
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

    values.append(availability_id)

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(f"""
            UPDATE Tbl_TeacherAvailability
            SET {", ".join(set_clauses)}
            WHERE TeacherAvailabilityID = %s
        """, tuple(values))

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Teacher availability record not found"
            )

        return {
            "message": "Teacher availability updated successfully",
            "availability_id": availability_id
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        cursor.close()
        connection.close()


@router.delete("/{availability_id}")
def delete_teacher_availability(
    availability_id: int,
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            DELETE FROM Tbl_TeacherAvailability
            WHERE TeacherAvailabilityID = %s
        """, (availability_id,))

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Teacher availability record not found"
            )

        return {
            "message": "Teacher availability deleted successfully",
            "availability_id": availability_id
        }

    except IntegrityError:
        connection.rollback()
        raise HTTPException(
            status_code=400,
            detail="Teacher availability cannot be deleted because it is being used by another record"
        )

    finally:
        cursor.close()
        connection.close()