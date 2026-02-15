from src.database.database import AMSDatabase


class SongController:

    @staticmethod
    def list_songs():
        conn = AMSDatabase.get_connection()
        rows = conn.execute(
            """
            SELECT s.*, a.stage_name
            FROM songs s
            JOIN artists a ON s.artist_id = a.id
        """
        ).fetchall()
        conn.close()
        return rows

    @staticmethod
    def list_artist_song(artist_id):
        conn = AMSDatabase.get_connection()
        rows = conn.execute(
            """
            SELECT s.*, a.stage_name
            FROM songs s
            JOIN artists a ON s.artist_id = a.id
            where s.artist_id=?
        """,
            (artist_id,),
        ).fetchall()
        conn.close()
        return rows

    @staticmethod
    def create_song(data):
        conn = AMSDatabase.get_connection()
        conn.execute(
            """
            INSERT INTO songs
            (artist_id,title,album_name,genre,created_at,updated_at)
            VALUES (?,?,?,?,datetime('now'),datetime('now'))
        """,
            (
                data["artist_id"],
                data["title"],
                data["album_name"],
                data["genre"],
            ),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def update_song(data):
        conn = AMSDatabase.get_connection()

        conn.execute(
            """
            UPDATE songs
            SET title=?, album_name=?, genre=?, updated_at=datetime('now')
            WHERE id=?
            """,
            (
                data.get("title"),
                data.get("album_name"),
                data.get("genre"),
                data.get("id"),
            ),
        )

        conn.commit()
        conn.close()

    @staticmethod
    def delete_song(song_id):
        conn = AMSDatabase.get_connection()
        conn.execute("DELETE FROM songs WHERE id=?", (song_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_song_by_id(song_id):
        conn = AMSDatabase.get_connection()
        row = conn.execute("SELECT * FROM songs WHERE id=?", (song_id,)).fetchone()
        conn.close()
        return row
