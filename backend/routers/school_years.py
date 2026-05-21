from fastapi import APIRouter, Depends, HTTPException
from mysql.connector import IntegrityError

from auth import require_roles
from db import get_db
from models import SchoolYearCreate, SchoolYearUpdate
from utils import get_audit_username, model_to_dict

router = APIRouter(prefix="/school-years", tags=["School Years"])


@router.get("")
def get_school_years(
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                SchoolYearID AS id,
                Name AS name,
                StartDate AS start_date,
                EndDate AS end_date,
                InsertUsername AS insert_username,
                InsertDate AS insert_date,
                ChangeUsername AS change_username,
                ChangeDate AS change_date
            FROM Tref_SchoolYears
            ORDER BY StartDate
        """)

        return cursor.fetchall()

    finally:
        cursor.close()


@router.get("/{school_year_id}")
def get_school_year(
    school_year_id: int,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                SchoolYearID AS id,
                Name AS name,
                StartDate AS start_date,
                EndDate AS end_date,
                InsertUsername AS insert_username,
                InsertDate AS insert_date,
                ChangeUsername AS change_username,
                ChangeDate AS change_date
            FROM Tref_SchoolYears
            WHERE SchoolYearID = %s
        """, (school_year_id,))

        school_year = cursor.fetchone()

        if school_year is None:
            raise HTTPException(status_code=404, detail="School year not found")

        return school_year

    finally:
        cursor.close()


@router.post("")
def create_school_year(
    school_year: SchoolYearCreate,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    if school_year.end_date <= school_year.start_date:
        raise HTTPException(
            status_code=400,
            detail="End date must be greater than start date"
        )

    cursor = connection.cursor(dictionary=True)

    audit_username = get_audit_username(current_user)

    try:
        cursor.execute("""
            INSERT INTO Tref_SchoolYears (
                Name,
                StartDate,
                EndDate,
                InsertUsername
            )
            VALUES (%s, %s, %s, %s)
        """, (
            school_year.name,
            school_year.start_date,
            school_year.end_date,
            audit_username
        ))

        connection.commit()

        return {
            "message": "School year created successfully",
            "school_year_id": cursor.lastrowid
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        cursor.close()


@router.put("/{school_year_id}")
def update_school_year(
    school_year_id: int,
    school_year: SchoolYearUpdate,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    data = model_to_dict(school_year)

    if not data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    field_map = {
        "name": "Name",
        "start_date": "StartDate",
        "end_date": "EndDate"
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

    values.append(school_year_id)

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(f"""
            UPDATE Tref_SchoolYears
            SET {", ".join(set_clauses)}
            WHERE SchoolYearID = %s
        """, tuple(values))

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="School year not found")

        return {
            "message": "School year updated successfully",
            "school_year_id": school_year_id
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        cursor.close()


@router.delete("/{school_year_id}")
def delete_school_year(
    school_year_id: int,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            DELETE FROM Tref_SchoolYears
            WHERE SchoolYearID = %s
        """, (school_year_id,))

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="School year not found")

        return {
            "message": "School year deleted successfully",
            "school_year_id": school_year_id
        }

    except IntegrityError:
        connection.rollback()
        raise HTTPException(
            status_code=400,
            detail="School year cannot be deleted because it is being used by another record"
        )

    finally:
        cursor.close()