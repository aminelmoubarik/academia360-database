from fastapi import APIRouter, Depends, HTTPException
from mysql.connector import IntegrityError

from auth import require_roles
from db import get_connection
from models import UserCreate, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


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
def get_users(
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                u.UserID AS id,
                u.FullName AS full_name,
                u.Email AS email,
                u.RoleID AS role_id,
                r.Name AS role,
                u.InsertUsername AS insert_username,
                u.InsertDate AS insert_date,
                u.ChangeUsername AS change_username,
                u.ChangeDate AS change_date
            FROM Tbl_Users u
            JOIN Tref_UserRoles r ON u.RoleID = r.RoleID
            ORDER BY u.UserID
        """)

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


@router.get("/{user_id}")
def get_user(
    user_id: int,
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                u.UserID AS id,
                u.FullName AS full_name,
                u.Email AS email,
                u.RoleID AS role_id,
                r.Name AS role,
                u.InsertUsername AS insert_username,
                u.InsertDate AS insert_date,
                u.ChangeUsername AS change_username,
                u.ChangeDate AS change_date
            FROM Tbl_Users u
            JOIN Tref_UserRoles r ON u.RoleID = r.RoleID
            WHERE u.UserID = %s
        """, (user_id,))

        user = cursor.fetchone()

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    finally:
        cursor.close()
        connection.close()


@router.post("")
def create_user(
    user: UserCreate,
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    audit_username = get_audit_username(current_user)

    try:
        cursor.execute("""
            INSERT INTO Tbl_Users (
                FullName,
                Email,
                PasswordHash,
                RoleID,
                InsertUsername
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            user.full_name,
            user.email,
            user.password_hash,
            user.role_id,
            audit_username
        ))

        connection.commit()

        return {
            "message": "User created successfully",
            "user_id": cursor.lastrowid
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        cursor.close()
        connection.close()


@router.put("/{user_id}")
def update_user(
    user_id: int,
    user: UserUpdate,
    current_user=Depends(require_roles(["admin", "director", "secretary"]))
):
    data = model_to_dict(user)

    if not data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    field_map = {
        "full_name": "FullName",
        "email": "Email",
        "password_hash": "PasswordHash",
        "role_id": "RoleID"
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

    values.append(user_id)

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(f"""
            UPDATE Tbl_Users
            SET {", ".join(set_clauses)}
            WHERE UserID = %s
        """, tuple(values))

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "message": "User updated successfully",
            "user_id": user_id
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        cursor.close()
        connection.close()


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user=Depends(require_roles(["admin", "director"]))
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            DELETE FROM Tbl_Users
            WHERE UserID = %s
        """, (user_id,))

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "message": "User deleted successfully",
            "user_id": user_id
        }

    except IntegrityError:
        connection.rollback()
        raise HTTPException(
            status_code=400,
            detail="User cannot be deleted because it is being used by another record"
        )

    finally:
        cursor.close()
        connection.close()