from fastapi import APIRouter, Depends, HTTPException
from mysql.connector import IntegrityError

from auth import require_roles
from db import get_db
from models import RoleCreate, RoleUpdate
from utils import get_audit_username, model_to_dict

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("")
def get_roles(
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin"]))
):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                RoleID AS id,
                Name AS name,
                InsertUsername AS insert_username,
                InsertDate AS insert_date,
                ChangeUsername AS change_username,
                ChangeDate AS change_date
            FROM Tref_UserRoles
            ORDER BY RoleID
        """)

        return cursor.fetchall()

    finally:
        cursor.close()


@router.get("/{role_id}")
def get_role(
    role_id: int,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin"]))
):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                RoleID AS id,
                Name AS name,
                InsertUsername AS insert_username,
                InsertDate AS insert_date,
                ChangeUsername AS change_username,
                ChangeDate AS change_date
            FROM Tref_UserRoles
            WHERE RoleID = %s
        """, (role_id,))

        role = cursor.fetchone()

        if role is None:
            raise HTTPException(status_code=404, detail="Role not found")

        return role

    finally:
        cursor.close()


@router.post("")
def create_role(
    role: RoleCreate,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin"]))
):
    cursor = connection.cursor(dictionary=True)

    audit_username = get_audit_username(current_user)

    try:
        cursor.execute("""
            INSERT INTO Tref_UserRoles (
                Name,
                InsertUsername
            )
            VALUES (%s, %s)
        """, (
            role.name,
            audit_username
        ))

        connection.commit()

        return {
            "message": "Role created successfully",
            "role_id": cursor.lastrowid
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        cursor.close()


@router.put("/{role_id}")
def update_role(
    role_id: int,
    role: RoleUpdate,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin"]))
):
    data = model_to_dict(role)

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

    values.append(role_id)

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(f"""
            UPDATE Tref_UserRoles
            SET {", ".join(set_clauses)}
            WHERE RoleID = %s
        """, tuple(values))

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Role not found")

        return {
            "message": "Role updated successfully",
            "role_id": role_id
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        cursor.close()


@router.delete("/{role_id}")
def delete_role(
    role_id: int,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin"]))
):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            DELETE FROM Tref_UserRoles
            WHERE RoleID = %s
        """, (role_id,))

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Role not found")

        return {
            "message": "Role deleted successfully",
            "role_id": role_id
        }

    except IntegrityError:
        connection.rollback()
        raise HTTPException(
            status_code=400,
            detail="Role cannot be deleted because it is being used by another record"
        )

    finally:
        cursor.close()
        