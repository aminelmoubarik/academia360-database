from db import get_connection
from auth import get_password_hash


def update_password(cursor, email: str, password: str):
    password_hash = get_password_hash(password)

    cursor.execute("""
        UPDATE Tbl_Users
        SET PasswordHash = %s,
            ChangeUsername = 'create_demo_passwords'
        WHERE Email = %s
    """, (
        password_hash,
        email
    ))

    if cursor.rowcount == 0:
        print(f"User not found: {email}")
    else:
        print(f"Updated password for {email}")


def main():
    demo_users = [
        {
            "email": "admin@academia360.local",
            "password": "admin"
        },
        {
            "email": "director@academia360.local",
            "password": "director"
        },
        {
            "email": "secretary@academia360.local",
            "password": "secretary"
        },
        {
            "email": "daniel.martins@academia360.local",
            "password": "professor"
        },
        {
            "email": "ana.costa@academia360.local",
            "password": "professor"
        },
        {
            "email": "carlos.ferreira@academia360.local",
            "password": "professor"
        }
    ]

    connection = get_connection()
    cursor = connection.cursor()

    try:
        for user in demo_users:
            update_password(
                cursor,
                user["email"],
                user["password"]
            )

        connection.commit()

        print("")
        print("Demo passwords created successfully.")
        print("")
        print("Login users:")
        print("admin@academia360.local / admin")
        print("director@academia360.local / director")
        print("secretary@academia360.local / secretary")
        print("daniel.martins@academia360.local / professor")
        print("ana.costa@academia360.local / professor")
        print("carlos.ferreira@academia360.local / professor")

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()