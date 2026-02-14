import os
import sqlite3


class AMSDatabase:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "ams.db")
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    @classmethod
    def get_connection(cls):
        conn = sqlite3.connect(cls.DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    dob TEXT NOT NULL,
                    gender TEXT NOT NULL CHECK (gender IN ('m', 'f', 'o')),
                    address TEXT NOT NULL,
                    role TEXT NOT NULL CHECK (role IN ('super_admin', 'artist_manager', 'artist')),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS artists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE,
                    stage_name TEXT NOT NULL,
                    first_release_year INTEGER NOT NULL,
                    no_of_albums_released INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS songs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    artist_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    album_name TEXT NOT NULL,
                    genre TEXT NOT NULL CHECK (genre IN ('rnb', 'country', 'classic', 'rock', 'jazz')),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (artist_id) REFERENCES artists(id) ON DELETE CASCADE
                );

            """
            )
