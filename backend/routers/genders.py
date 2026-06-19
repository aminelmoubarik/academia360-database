from fastapi import APIRouter, Depends, HTTPException
from mysql.connector import IntegrityError

from auth import require_roles
from db import get_db
from models import GenderCreate, GenderUpdate
from utils import get_audit_username, model_to_dict

router = APIRouter(prefix="/genders", tags=["Genders"])


@router.get("")
def get_genders(
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                GenderID AS id,
                Name AS name,
                InsertUsername AS insert_username,
                InsertDate AS insert_date,
                ChangeUsername AS change_username,
                ChangeDate AS change_date
            FROM Tref_Gender
            ORDER BY GenderID
        """)

        return cursor.fetchall()

    finally:
        cursor.close()


@router.get("/{gender_id}")
def get_gender(
    gender_id: int,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                GenderID AS id,
                Name AS name,
                InsertUsername AS insert_username,
                InsertDate AS insert_date,
                ChangeUsername AS change_username,
                ChangeDate AS change_date
            FROM Tref_Gender
            WHERE GenderID = %s
        """, (gender_id,))

        gender = cursor.fetchone()

        if gender is None:
            raise HTTPException(status_code=404, detail="Gender not found")

        return gender

    finally:
        cursor.close()


@router.post("")
def create_gender(
    gender: GenderCreate,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin"]))
):
    cursor = connection.cursor(dictionary=True)

    audit_username = get_audit_username(current_user)

    try:
        cursor.execute("""
            INSERT INTO Tref_Gender (
                Name,
                InsertUsername
            )
            VALUES (%s, %s)
        """, (
            gender.name,
            audit_username
        ))

        connection.commit()

        return {
            "message": "Gender created successfully",
            "gender_id": cursor.lastrowid
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        cursor.close()


@router.put("/{gender_id}")
def update_gender(
    gender_id: int,
    gender: GenderUpdate,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin"]))
):
    data = model_to_dict(gender)

    if not data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    field_map = {
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

    values.append(gender_id)

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(f"""
            UPDATE Tref_Gender
            SET {", ".join(set_clauses)}
            WHERE GenderID = %s
        """, tuple(values))

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Gender not found")

        return {
            "message": "Gender updated successfully",
            "gender_id": gender_id
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        cursor.close()


@router.delete("/{gender_id}")
def delete_gender(
    gender_id: int,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin"]))
):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            DELETE FROM Tref_Gender
            WHERE GenderID = %s
        """, (gender_id,))

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Gender not found")

        return {
            "message": "Gender deleted successfully",
            "gender_id": gender_id
        }

    except IntegrityError:
        connection.rollback()
        raise HTTPException(
            status_code=400,
            detail="Gender cannot be deleted because it is being used by another record"
        )

    finally:
        cursor.close()