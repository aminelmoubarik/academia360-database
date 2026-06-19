from fastapi import APIRouter, Depends, HTTPException
from mysql.connector import IntegrityError

from auth import get_password_hash, require_roles
from db import get_db
from services.audit_logger import log_audit
from models import UserCreate, UserUpdate
from utils import get_audit_username, model_to_dict

router = APIRouter(prefix="/users", tags=["Users"])


def validate_role_exists(cursor, role_id: int):
    cursor.execute("""
        SELECT RoleID
        FROM Tref_UserRoles
        WHERE RoleID = %s
    """, (role_id,))

    if cursor.fetchone() is None:
        raise HTTPException(status_code=404, detail="Perfil não encontrado")


def validate_password(password: str):
    if not password or len(password) < 6:
        raise HTTPException(
            status_code=400,
            detail="A palavra-passe deve ter pelo menos 6 caracteres"
        )


def format_integrity_error(error: IntegrityError) -> str:
    message = str(error)

    if "Duplicate entry" in message and ("Email" in message or "email" in message):
        return "Já existe um utilizador com este email."

    return message


@router.get("")
def get_users(
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin"]))
):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                u.UserID AS id,
                u.FullName AS full_name,
                u.Email AS email,
                u.RoleID AS role_id,
                r.Name AS role,
                CASE
                    WHEN u.PasswordHash IS NULL THEN 'SEM PALAVRA-PASSE'
                    ELSE 'PALAVRA-PASSE DEFINIDA'
                END AS password_status,
                u.InsertUsername AS insert_username,
                u.InsertDate AS insert_date,
                u.ChangeUsername AS change_username,
                u.ChangeDate AS change_date
            FROM Tbl_Users u
            JOIN Tref_UserRoles r
                ON u.RoleID = r.RoleID
            ORDER BY u.UserID
        """)

        return cursor.fetchall()

    finally:
        cursor.close()


@router.get("/{user_id}")
def get_user(
    user_id: int,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin"]))
):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                u.UserID AS id,
                u.FullName AS full_name,
                u.Email AS email,
                u.RoleID AS role_id,
                r.Name AS role,
                CASE
                    WHEN u.PasswordHash IS NULL THEN 'SEM PALAVRA-PASSE'
                    ELSE 'PALAVRA-PASSE DEFINIDA'
                END AS password_status,
                u.InsertUsername AS insert_username,
                u.InsertDate AS insert_date,
                u.ChangeUsername AS change_username,
                u.ChangeDate AS change_date
            FROM Tbl_Users u
            JOIN Tref_UserRoles r
                ON u.RoleID = r.RoleID
            WHERE u.UserID = %s
        """, (user_id,))

        user = cursor.fetchone()

        if user is None:
            raise HTTPException(status_code=404, detail="Utilizador não encontrado")

        return user

    finally:
        cursor.close()


@router.post("")
def create_user(
    user: UserCreate,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin"]))
):
    validate_password(user.password)

    cursor = connection.cursor(dictionary=True)

    audit_username = get_audit_username(current_user)
    password_hash = get_password_hash(user.password)

    try:
        validate_role_exists(cursor, user.role_id)

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
            password_hash,
            user.role_id,
            audit_username
        ))

        user_id = cursor.lastrowid
        log_audit(
            cursor,
            current_user=current_user,
            action="create",
            module="administration",
            entity_type="user",
            entity_id=user_id,
            summary=f"Utilizador criado: {user.email}",
            details={"email": user.email, "full_name": user.full_name, "role_id": user.role_id},
        )
        connection.commit()

        return {
            "message": "Utilizador criado com sucesso",
            "user_id": user_id
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=format_integrity_error(error))

    finally:
        cursor.close()


@router.put("/{user_id}")
def update_user(
    user_id: int,
    user: UserUpdate,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin"]))
):
    data = model_to_dict(user)

    if not data:
        raise HTTPException(status_code=400, detail="Nenhum campo enviado para atualização")

    cursor = connection.cursor(dictionary=True)

    audit_username = get_audit_username(current_user)

    try:
        cursor.execute("""
            SELECT UserID
            FROM Tbl_Users
            WHERE UserID = %s
        """, (user_id,))

        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Utilizador não encontrado")

        if "role_id" in data:
            validate_role_exists(cursor, data["role_id"])

        if "password" in data:
            validate_password(data["password"])
            data["password"] = get_password_hash(data["password"])

        field_map = {
            "full_name": "FullName",
            "email": "Email",
            "password": "PasswordHash",
            "role_id": "RoleID"
        }

        set_clauses = []
        values = []

        for api_field, db_field in field_map.items():
            if api_field in data:
                set_clauses.append(f"{db_field} = %s")
                values.append(data[api_field])

        if not set_clauses:
            raise HTTPException(status_code=400, detail="Nenhum campo válido enviado para atualização")

        set_clauses.append("ChangeUsername = %s")
        values.append(audit_username)

        values.append(user_id)

        cursor.execute(f"""
            UPDATE Tbl_Users
            SET {", ".join(set_clauses)}
            WHERE UserID = %s
        """, tuple(values))

        log_audit(
            cursor,
            current_user=current_user,
            action="update",
            module="administration",
            entity_type="user",
            entity_id=user_id,
            summary=f"Utilizador atualizado: {user_id}",
            details={"fields": sorted(data.keys())},
        )
        connection.commit()

        return {
            "message": "Utilizador atualizado com sucesso",
            "user_id": user_id
        }

    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=format_integrity_error(error))

    finally:
        cursor.close()


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    connection=Depends(get_db),
    current_user=Depends(require_roles(["admin"]))
):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                u.UserID AS id,
                u.Email AS email,
                r.Name AS role
            FROM Tbl_Users u
            JOIN Tref_UserRoles r ON u.RoleID = r.RoleID
            WHERE u.UserID = %s
        """, (user_id,))
        target = cursor.fetchone()

        if target is None:
            raise HTTPException(status_code=404, detail="Utilizador não encontrado")

        if current_user.get("user_id") == user_id:
            raise HTTPException(
                status_code=400,
                detail="Não pode eliminar a sua própria conta enquanto tem sessão iniciada."
            )

        if target["role"] == "admin" and current_user.get("role") != "admin":
            raise HTTPException(
                status_code=403,
                detail="Apenas um administrador pode eliminar outro administrador."
            )

        if target["role"] == "admin":
            cursor.execute("""
                SELECT COUNT(*) AS total_admins
                FROM Tbl_Users u
                JOIN Tref_UserRoles r ON u.RoleID = r.RoleID
                WHERE r.Name = 'admin'
            """)
            total_admins = cursor.fetchone()["total_admins"]
            if total_admins <= 1:
                raise HTTPException(
                    status_code=400,
                    detail="Não pode eliminar o último administrador do sistema."
                )

        cursor.execute("""
            DELETE FROM Tbl_Users
            WHERE UserID = %s
        """, (user_id,))

        log_audit(
            cursor,
            current_user=current_user,
            action="delete",
            module="administration",
            entity_type="user",
            entity_id=user_id,
            summary=f"Utilizador eliminado: {target['email']}",
            details={"email": target["email"], "role": target["role"]},
        )
        connection.commit()

        return {
            "message": "Utilizador eliminado com sucesso",
            "user_id": user_id
        }

    except IntegrityError:
        connection.rollback()
        raise HTTPException(
            status_code=400,
            detail="O utilizador não pode ser eliminado porque está associado a outros registos."
        )

    finally:
        cursor.close()
