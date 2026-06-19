USE academia360;

INSERT INTO Tref_UserRoles (RoleID, Name, InsertUsername)
VALUES (1, 'admin', 'recover_admin')
ON DUPLICATE KEY UPDATE Name = VALUES(Name);

-- Password must be generated with create_demo_passwords.py because the backend uses PBKDF2 hashes.
-- Run from DB/backend:
--   python create_demo_passwords.py
