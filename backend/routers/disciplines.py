from fastapi import APIRouter, Depends, HTTPException
from mysql.connector import IntegrityError

from auth import require_roles
from db import get_connection
from models import DisciplineCreate, DisciplineUpdate

router = APIRouter(prefix="/disciplines", tags=["Disciplines"])


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
def get_disciplines(
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                DisciplineID AS id,
                Name AS name,
                Code AS code,
                InsertUsername AS insert_username,
                InsertDate AS insert_date,
                ChangeUsername AS change_username,
                ChangeDate AS change_date
            FROM Tbl_Disciplines
            ORDER BY DisciplineID
        """)

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


@router.get("/{discipline_id}")
def get_discipline(
    discipline_id: int,
    current_user=Depends(require_roles(["admin", "director", "secretary", "professor"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                DisciplineID AS id,
                Name AS name,
                Code AS code,
                InsertUsername AS insert_username,
                InsertDate AS insert_date,
                ChangeUsername AS change_username,
                ChangeDate AS change_date
            FROM Tbl_Disciplines
            WHERE DisciplineID = %s
        """, (discipline_id,))

        discipline = cursor.fetchone()

        if discipline is None:
            raise HTTPException(status_code=404, detail="Discipline not found")

        return discipline

    finally:
        cursor.close()
        connection.close()


@router.post("")
def create_discipline(
    discipline: DisciplineCreate,
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    audit_username = get_audit_username(current_user)

    try:
        cursor.execute("""
            INSERT INTO Tbl_Disciplines (
                Name,
                Code,
                InsertUsername
            )
            VALUES (%s, %s, %s)
        """, (
            discipline.name,
            discipline.code,
            audit_username
        ))

        connection.commit()

        return {
            "message": "Discipline created successfully",
            "discipline_id": cursor.lastrowid
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        cursor.close()
        connection.close()


@router.put("/{discipline_id}")
def update_discipline(
    discipline_id: int,
    discipline: DisciplineUpdate,
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    data = model_to_dict(discipline)

    if not data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    field_map = {
        "name": "Name",
        "code": "Code"
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

    values.append(discipline_id)

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(f"""
            UPDATE Tbl_Disciplines
            SET {", ".join(set_clauses)}
            WHERE DisciplineID = %s
        """, tuple(values))

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Discipline not found")

        return {
            "message": "Discipline updated successfully",
            "discipline_id": discipline_id
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        cursor.close()
        connection.close()


@router.delete("/{discipline_id}")
def delete_discipline(
    discipline_id: int,
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            DELETE FROM Tbl_Disciplines
            WHERE DisciplineID = %s
        """, (discipline_id,))

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Discipline not found")

        return {
            "message": "Discipline deleted successfully",
            "discipline_id": discipline_id
        }

    except IntegrityError:
        connection.rollback()
        raise HTTPException(
            status_code=400,
            detail="Discipline cannot be deleted because it is being used by another record"
        )

    finally:
        cursor.close()
        connection.close()