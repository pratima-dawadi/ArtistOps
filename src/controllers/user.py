from src.database.database import AMSDatabase
from datetime import datetime


class UserController:

    @staticmethod
    def list_users():
        conn = AMSDatabase.get_connection()
        rows = conn.execute("SELECT * FROM users ORDER BY id DESC").fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def create_user(data):
        conn = AMSDatabase.get_connection()
        try:
            cursor = conn.execute(
                """
                INSERT INTO users
                (first_name,last_name,email,password_hash,phone,dob,gender,address,role,created_at,updated_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    data["first_name"],
                    data["last_name"],
                    data["email"],
                    data["password"],
                    data["phone"],
                    data["dob"],
                    data["gender"],
                    data["address"],
                    data["role"],
                    datetime.now(),
                    datetime.now(),
                ),
            )

            user_id = cursor.lastrowid

            if data["role"] == "artist":
                conn.execute(
                    """
                    INSERT INTO artists
                    (user_id, stage_name, first_release_year, no_of_albums_released, created_at, updated_at)
                    VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
                    """,
                    (
                        user_id,
                        data.get("stage_name", ""),
                        data.get("first_release_year", None),
                        data.get("no_of_albums_released", 0),
                    ),
                )

            conn.commit()
            conn.close()
        except Exception as e:
            conn.rollback()
            raise e

        finally:
            conn.close()

    @staticmethod
    def update_user(data):
        conn = AMSDatabase.get_connection()

        conn.execute(
            """
            UPDATE users
            SET first_name=?, last_name=?, email=?, phone=?, dob=?, gender=?, address=?, role=?, updated_at=datetime('now')
            WHERE id=?
            """,
            (
                data.get("first_name"),
                data.get("last_name"),
                data.get("email"),
                data.get("phone"),
                data.get("dob"),
                data.get("gender"),
                data.get("address"),
                data.get("role"),
                data.get("id"),
            ),
        )

        conn.commit()
        conn.close()

    @staticmethod
    def delete_user(user_id):
        conn = AMSDatabase.get_connection()
        conn.execute("DELETE FROM users WHERE id=?", (user_id,))
        conn.commit()
        conn.close()
