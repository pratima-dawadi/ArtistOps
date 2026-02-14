from datetime import datetime

from src.database.database import AMSDatabase
from src.utils.password import hash_password, verify_password
from src.utils.validate import valid_email


class AuthController:

    def register_user(self, data):
        conn = AMSDatabase.get_connection()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "").strip()

        if not email or not password:
            return False, "Email and password are required."

        if not valid_email(email):
            return False, "Invalid email format."

        existing = conn.execute(
            "SELECT id FROM users WHERE email = ?", (email,)
        ).fetchone()

        if existing:
            return False, "Email already exists."

        conn.execute(
            """
            INSERT INTO users
            (first_name, last_name, email, password_hash, phone, dob, gender, address, role, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("first_name"),
                data.get("last_name"),
                email,
                hash_password(password),
                data.get("phone"),
                data.get("dob"),
                data.get("gender"),
                data.get("address"),
                data.get("role"),
                datetime.now(),
                datetime.now(),
            ),
        )

        conn.commit()
        conn.close()
        return True, "Registration successful."

    def login_user(self, data):
        conn = AMSDatabase.get_connection()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "").strip()

        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        conn.close()

        if not user:
            return False, "Invalid credentials."

        if not verify_password(password, user["password_hash"]):
            return False, "Invalid credentials."

        return True, dict(user)
