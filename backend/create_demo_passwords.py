import os

import mysql.connector
from dotenv import load_dotenv

from auth import get_password_hash

load_dotenv()


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "academia360"),
        port=int(os.getenv("DB_PORT", 3306))
    )


def main():
    demo_users = [
        {
            "email": "admin@academia360.local",
            "password": "admin"
        },
        {
            "email": "laura.mendes@academia360.local",
            "password": "director"
        },
        {
            "email": "rita.almeida@academia360.local",
            "password": "secretary"
        },
        {
            "email": "miguel.ramos@academia360.local",
            "password": "professor"
        },
        {
            "email": "ines.duarte@academia360.local",
            "password": "professor"
        },
        {
            "email": "pedro.neves@academia360.local",
            "password": "professor"
        }
    ]

    connection = get_connection()
    cursor = connection.cursor()

    for user in demo_users:
        password_hash = get_password_hash(user["password"])

        cursor.execute("""
            UPDATE Tbl_Users
            SET PasswordHash = %s,
                ChangeUsername = 'create_demo_passwords'
            WHERE Email = %s
        """, (
            password_hash,
            user["email"]
        ))

        print(f"Updated password for {user['email']}")

    connection.commit()

    cursor.close()
    connection.close()

    print("")
    print("Demo passwords created successfully.")
    print("")
    print("Login users:")
    print("admin@academia360.local / admin")
    print("laura.mendes@academia360.local / director")
    print("rita.almeida@academia360.local / secretary")
    print("miguel.ramos@academia360.local / professor")
    print("ines.duarte@academia360.local / professor")
    print("pedro.neves@academia360.local / professor")


if __name__ == "__main__":
    main()