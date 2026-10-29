import json
import time
from typing import List, Optional

from devpulse.domain.models import Session
from devpulse.storage.database import Database


class SnapshotRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def save_sessions(self, sessions: List[Session], is_historical: bool = False) -> None:
        cursor = self.database.connection().cursor()
        cursor.execute("DELETE FROM session_snapshots")
        fetched_at = int(time.time())
        for session in sessions:
            cursor.execute(
                """
                INSERT INTO session_snapshots
                (session_id, project_id, title, model, tokens_json, cost, updated_at, fetched_at, is_historical)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session.id,
                    session.project_id,
                    session.title,
                    session.model.name if session.model else None,
                    json.dumps(
                        {
                            "input": session.tokens.input,
                            "output": session.tokens.output,
                            "reasoning": session.tokens.reasoning,
                            "cache_read": session.tokens.cache_read,
                            "cache_write": session.tokens.cache_write,
                        }
                    ),
                    session.cost,
                    session.updated_at,
                    fetched_at,
                    1 if is_historical else 0,
                ),
            )
        self.database.connection().commit()

    def load_latest(self) -> List[dict]:
        cursor = self.database.connection().cursor()
        cursor.execute("SELECT * FROM session_snapshots ORDER BY id")
        rows = cursor.fetchall()
        result = []
        for row in rows:
            tokens = json.loads(row["tokens_json"]) if row["tokens_json"] else {}
            result.append(
                {
                    "session_id": row["session_id"],
                    "project_id": row["project_id"],
                    "title": row["title"],
                    "model": row["model"],
                    "tokens": tokens,
                    "cost": row["cost"],
                    "updated_at": row["updated_at"],
                    "fetched_at": row["fetched_at"],
                    "is_historical": bool(row["is_historical"]),
                }
            )
        return result

    def last_fetched_at(self) -> Optional[int]:
        cursor = self.database.connection().cursor()
        cursor.execute("SELECT MAX(fetched_at) AS value FROM session_snapshots")
        row = cursor.fetchone()
        return int(row["value"]) if row and row["value"] is not None else None
