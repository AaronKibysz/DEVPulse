import sqlite3
from pathlib import Path
from typing import Optional


def default_database_path() -> Path:
    return Path.home() / ".devpulse" / "devpulse.db"


class Database:
    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or default_database_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self.path)
        self._connection.row_factory = sqlite3.Row
        self._initialize()

    def _initialize(self) -> None:
        cursor = self._connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS session_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                project_id TEXT,
                title TEXT,
                model TEXT,
                tokens_json TEXT,
                cost REAL,
                updated_at INTEGER,
                fetched_at INTEGER NOT NULL,
                is_historical INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS app_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        self._connection.commit()

    def connection(self) -> sqlite3.Connection:
        return self._connection

    def close(self) -> None:
        self._connection.close()
