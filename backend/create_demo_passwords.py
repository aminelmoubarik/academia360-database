from db import get_connection
from auth import get_password_hash


DEMO_USERS = [
    {
        "full_name": "Admin User",
        "email": "admin@academia360.local",
        "role": "admin",
        "password": "admin123",
    },
    {
        "full_name": "Director User",
        "email": "director@academia360.local",
        "role": "director",
        "password": "director123",
    },
    {
        "full_name": "Secretary User",
        "email": "secretary@academia360.local",
        "role": "secretary",
        "password": "secretary123",
    },
    {
        "full_name": "Daniel Martins",
        "email": "daniel.martins@academia360.local",
        "role": "professor",
        "password": "professor123",
    },
    {
        "full_name": "Ana Costa",
        "email": "ana.costa@academia360.local",
        "role": "professor",
        "password": "professor123",
    },
    {
        "full_name": "Carlos Ferreira",
        "email": "carlos.ferreira@academia360.local",
        "role": "professor",
        "password": "professor123",
    },
]


def ensure_role(cursor, role_name: str) -> int:
    cursor.execute("""
        SELECT RoleID
        FROM Tref_UserRoles
        WHERE Name = %s
    """, (role_name,))
    row = cursor.fetchone()

    if row:
        return row[0]

    cursor.execute("""
        INSERT INTO Tref_UserRoles (Name, InsertUsername)
        VALUES (%s, 'create_demo_passwords')
    """, (role_name,))
    return cursor.lastrowid


def upsert_user(cursor, full_name: str, email: str, role_id: int, password: str):
    password_hash = get_password_hash(password)

    cursor.execute("""
        SELECT UserID
        FROM Tbl_Users
        WHERE Email = %s
    """, (email,))
    row = cursor.fetchone()

    if row:
        cursor.execute("""
            UPDATE Tbl_Users
            SET FullName = %s,
                PasswordHash = %s,
                RoleID = %s,
                ChangeUsername = 'create_demo_passwords'
            WHERE Email = %s
        """, (
            full_name,
            password_hash,
            role_id,
            email,
        ))
        print(f"Updated demo login: {email}")
        return

    cursor.execute("""
        INSERT INTO Tbl_Users (
            FullName,
            Email,
            PasswordHash,
            RoleID,
            InsertUsername
        )
        VALUES (%s, %s, %s, %s, 'create_demo_passwords')
    """, (
        full_name,
        email,
        password_hash,
        role_id,
    ))
    print(f"Created missing demo login: {email}")


def main():
    connection = get_connection()
    cursor = connection.cursor()

    try:
        role_ids = {}
        for role_name in ["admin", "director", "secretary", "professor"]:
            role_ids[role_name] = ensure_role(cursor, role_name)

        for user in DEMO_USERS:
            upsert_user(
                cursor=cursor,
                full_name=user["full_name"],
                email=user["email"],
                role_id=role_ids[user["role"]],
                password=user["password"],
            )

        connection.commit()

        print("")
        print("Demo users and passwords are ready.")
        print("")
        print("Login users:")
        for user in DEMO_USERS:
            print(f"{user['email']} / {user['password']}")

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()
