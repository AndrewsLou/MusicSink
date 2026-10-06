import sqlite3
from datetime import datetime, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS track_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    spotify_track_id TEXT UNIQUE,
    youtube_video_id TEXT UNIQUE,
    artist TEXT NOT NULL,
    title TEXT NOT NULL,
    added_via TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


class Database:
    def __init__(self, path: str):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def is_empty(self) -> bool:
        row = self.conn.execute("SELECT COUNT(*) AS c FROM track_mappings").fetchone()
        return row["c"] == 0

    def all_mappings(self) -> list[sqlite3.Row]:
        return self.conn.execute("SELECT * FROM track_mappings").fetchall()

    def insert_mapping(self, spotify_track_id: str, youtube_video_id: str, artist: str, title: str, added_via: str) -> None:
        self.conn.execute(
            """
            INSERT INTO track_mappings
                (spotify_track_id, youtube_video_id, artist, title, added_via, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (spotify_track_id, youtube_video_id, artist, title, added_via, datetime.now(timezone.utc).isoformat()),
        )
        self.conn.commit()

    def delete_mapping(self, mapping_id: int) -> None:
        self.conn.execute("DELETE FROM track_mappings WHERE id = ?", (mapping_id,))
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()
