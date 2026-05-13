from auth import get_password_hash
from db import get_connection


demo_users = {
    "admin@academia360.pt": "admin123",
    "director@academia360.pt": "director123",
    "secretary@academia360.pt": "secretary123",
    "afonso@academia360.pt": "professor123",
    "joana@academia360.pt": "professor123",
}


connection = get_connection()
cursor = connection.cursor()

for email, password in demo_users.items():
    password_hash = get_password_hash(password)

    cursor.execute(
        """
        UPDATE users
        SET password_hash = %s
        WHERE email = %s
        """,
        (password_hash, email)
    )

connection.commit()

cursor.close()
connection.close()

print("Demo passwords updated successfully.")