from datetime import datetime

from src.database.database import AMSDatabase
from src.utils.password import hash_password


class ArtistController:

    @staticmethod
    def list_artists(page=1, page_size=5):
        conn = AMSDatabase.get_connection()
        offset = (page - 1) * page_size
        rows = conn.execute(
            "SELECT * FROM artists ORDER BY id DESC LIMIT ? OFFSET ?",
            (page_size, offset),
        ).fetchall()
        total = conn.execute("SELECT COUNT(*) as count FROM artists").fetchone()[
            "count"
        ]
        conn.close()
        return rows, total

    @staticmethod
    def get_artist_by_id(artist_id):
        conn = AMSDatabase.get_connection()
        row = conn.execute("SELECT * from artists where id=?", (artist_id,)).fetchone()
        conn.close()
        return row

    @staticmethod
    def create_artist(data):
        conn = AMSDatabase.get_connection()
        try:
            cursor = conn.execute(
                """
                INSERT INTO users
                (first_name, last_name, email, password_hash, phone, dob, gender, address, role, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["first_name"],
                    data["last_name"],
                    data["email"],
                    hash_password(data["password"]),
                    data["phone"],
                    data["dob"],
                    data["gender"],
                    data["address"],
                    "artist",
                    datetime.now(),
                    datetime.now(),
                ),
            )

            user_id = cursor.lastrowid

            conn.execute(
                """
                INSERT INTO artists
                (user_id, stage_name, first_release_year, no_of_albums_released, created_at, updated_at)
                VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
                """,
                (
                    user_id,
                    data["stage_name"],
                    data["first_release_year"],
                    data["no_of_albums_released"],
                ),
            )

            conn.commit()

        except Exception as e:
            conn.rollback()
            raise e

        finally:
            conn.close()

    @staticmethod
    def update_artist(data):
        conn = AMSDatabase.get_connection()

        conn.execute(
            """
            UPDATE artists
            SET stage_name=?, first_release_year=?, no_of_albums_released=?, updated_at=datetime('now')
            WHERE id=?
            """,
            (
                data.get("stage_name"),
                data.get("first_release_year"),
                data.get("no_of_albums_released"),
                data.get("id"),
            ),
        )

        conn.commit()
        conn.close()

    @staticmethod
    def delete_artist(artist_id):
        conn = AMSDatabase.get_connection()
        conn.execute("DELETE FROM artists WHERE id=?", (artist_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_artist_by_user_id(user_id):
        conn = AMSDatabase.get_connection()
        row = conn.execute(
            "SELECT * FROM artists WHERE user_id=?", (user_id,)
        ).fetchone()
        conn.close()
        return row
