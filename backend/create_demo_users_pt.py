"""Create or repair Academia360 demo users with Portuguese names.

Run this file from DB/backend so it can import db.py and auth.py:

    cd C:\\Users\\GU603\\Documents\\GitHub\\DB\\backend
    .\\.venv\\Scripts\\Activate.ps1
    python create_demo_users_pt.py

It is safe to run multiple times. Existing users are updated, missing users
are recreated, and professor profiles are created when needed.
"""

from __future__ import annotations

from dataclasses import dataclass

from auth import get_password_hash
from db import get_connection


@dataclass(frozen=True)
class DemoUser:
    full_name: str
    email: str
    role: str
    password: str
    professor_profile: bool = False


DEMO_USERS: list[DemoUser] = [
    DemoUser(
        full_name="Administração Academia360",
        email="admin@academia360.local",
        role="admin",
        password="admin123",
    ),
    DemoUser(
        full_name="Direção Pedagógica",
        email="direcao@academia360.local",
        role="director",
        password="direcao123",
    ),
    DemoUser(
        full_name="Secretaria Académica",
        email="secretaria@academia360.local",
        role="secretary",
        password="secretaria123",
    ),
    DemoUser(
        full_name="Professor Afonso Silva",
        email="afonso.silva@academia360.local",
        role="professor",
        password="afonso123",
        professor_profile=True,
    ),
    DemoUser(
        full_name="Professora Joana Ferreira",
        email="joana.ferreira@academia360.local",
        role="professor",
        password="joana123",
        professor_profile=True,
    ),
    DemoUser(
        full_name="Professor Miguel Santos",
        email="miguel.santos@academia360.local",
        role="professor",
        password="miguel123",
        professor_profile=True,
    ),
]


REQUIRED_ROLES = ["admin", "director", "secretary", "professor"]


def ensure_role(cursor, role_name: str) -> int:
    cursor.execute(
        """
        SELECT RoleID
        FROM Tref_UserRoles
        WHERE Name = %s
        """,
        (role_name,),
    )
    row = cursor.fetchone()

    if row:
        return row["RoleID"]

    cursor.execute(
        """
        INSERT INTO Tref_UserRoles (Name, InsertUsername)
        VALUES (%s, 'create_demo_users_pt')
        """,
        (role_name,),
    )
    return cursor.lastrowid


def upsert_user(cursor, user: DemoUser, role_id: int) -> int:
    password_hash = get_password_hash(user.password)

    cursor.execute(
        """
        SELECT UserID
        FROM Tbl_Users
        WHERE Email = %s
        """,
        (user.email,),
    )
    row = cursor.fetchone()

    if row:
        user_id = row["UserID"]
        cursor.execute(
            """
            UPDATE Tbl_Users
            SET FullName = %s,
                PasswordHash = %s,
                RoleID = %s,
                ChangeUsername = 'create_demo_users_pt'
            WHERE UserID = %s
            """,
            (user.full_name, password_hash, role_id, user_id),
        )
        print(f"Updated: {user.email}")
        return user_id

    cursor.execute(
        """
        INSERT INTO Tbl_Users (
            FullName,
            Email,
            PasswordHash,
            RoleID,
            InsertUsername
        )
        VALUES (%s, %s, %s, %s, 'create_demo_users_pt')
        """,
        (user.full_name, user.email, password_hash, role_id),
    )
    user_id = cursor.lastrowid
    print(f"Created: {user.email}")
    return user_id


def ensure_professor_profile(cursor, user_id: int, full_name: str) -> None:
    cursor.execute(
        """
        SELECT ProfessorID
        FROM Tbl_Professors
        WHERE UserID = %s
        """,
        (user_id,),
    )
    row = cursor.fetchone()

    if row:
        print(f"Professor profile already exists: {full_name}")
        return

    cursor.execute(
        """
        INSERT INTO Tbl_Professors (
            UserID,
            InsertUsername
        )
        VALUES (%s, 'create_demo_users_pt')
        """,
        (user_id,),
    )
    print(f"Created professor profile: {full_name}")


def main() -> None:
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        role_ids = {role_name: ensure_role(cursor, role_name) for role_name in REQUIRED_ROLES}

        for user in DEMO_USERS:
            user_id = upsert_user(cursor, user, role_ids[user.role])

            if user.professor_profile:
                ensure_professor_profile(cursor, user_id, user.full_name)

        connection.commit()

        print("\nDemo users are ready.\n")
        print("Logins:")
        for user in DEMO_USERS:
            print(f"{user.email} / {user.password}  ({user.role})")

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()
