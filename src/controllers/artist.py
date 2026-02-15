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

    @staticmethod
    def export_artists_csv_rows():
        conn = AMSDatabase.get_connection()
        rows = conn.execute(
            """
            SELECT u.first_name, u.last_name, u.email, u.phone, u.dob, u.gender, u.address,
                   a.stage_name, a.first_release_year, a.no_of_albums_released
            FROM artists a
            JOIN users u ON u.id = a.user_id
            ORDER BY a.id DESC
            """
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def import_artists(rows):
        if not rows:
            return 0

        conn = AMSDatabase.get_connection()
        created_count = 0

        try:
            for _, row in enumerate(rows, start=1):
                first_name = (row.get("first_name") or "").strip()
                last_name = (row.get("last_name") or "").strip()
                email = (row.get("email") or "").strip()
                password = (row.get("password") or "").strip()
                phone = (row.get("phone") or "").strip()
                dob = (row.get("dob") or "").strip()
                gender = (row.get("gender") or "").strip()
                gender = gender if gender in ["m", "f", "o"] else "o"
                address = (row.get("address") or "").strip()
                stage_name = (row.get("stage_name") or "").strip()
                release_year = (row.get("first_release_year") or "").strip()
                album_count = (row.get("no_of_albums_released") or "").strip()

                if not stage_name or not release_year or not album_count:
                    continue

                try:
                    release_year = int(release_year)
                    album_count = int(album_count)
                except ValueError:
                    continue

                cursor = conn.execute(
                    """
                    INSERT INTO users
                    (first_name, last_name, email, password_hash, phone, dob, gender, address, role, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        first_name or "Artist",
                        last_name or "Artist",
                        email,
                        hash_password(password or "Import123"),
                        phone,
                        dob,
                        gender,
                        address,
                        "artist",
                        datetime.now(),
                        datetime.now(),
                    ),
                )

                conn.execute(
                    """
                    INSERT INTO artists
                    (user_id, stage_name, first_release_year, no_of_albums_released, created_at, updated_at)
                    VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
                    """,
                    (
                        cursor.lastrowid,
                        stage_name,
                        release_year,
                        album_count,
                    ),
                )
                created_count += 1

            conn.commit()
            return created_count
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
