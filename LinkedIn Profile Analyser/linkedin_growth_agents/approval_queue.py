from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from .content_engine import DraftPost


@dataclass(frozen=True)
class QueuedPost:
    id: int
    due_date: str
    topic: str
    content_type: str
    status: str
    content: str


class ApprovalQueue:
    def __init__(self, database_path: str) -> None:
        self.database_path = Path(database_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path)

    def _init_db(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    due_date TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'draft',
                    published_urn TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def add_posts(self, posts: list[DraftPost]) -> int:
        now = datetime.utcnow().isoformat(timespec="seconds")
        with self._connect() as connection:
            connection.executemany(
                """
                INSERT INTO posts (due_date, topic, content_type, content, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, 'draft', ?, ?)
                """,
                [(post.due_date.isoformat(), post.topic, post.content_type, post.full_text, now, now) for post in posts],
            )
            return connection.total_changes

    def list_posts(self) -> list[QueuedPost]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id, due_date, topic, content_type, status, content FROM posts ORDER BY due_date, id"
            ).fetchall()
        return [QueuedPost(*row) for row in rows]

    def approve(self, post_id: int) -> None:
        self._set_status(post_id, "approved")

    def reject(self, post_id: int) -> None:
        self._set_status(post_id, "rejected")

    def _set_status(self, post_id: int, status: str) -> None:
        now = datetime.utcnow().isoformat(timespec="seconds")
        with self._connect() as connection:
            connection.execute("UPDATE posts SET status = ?, updated_at = ? WHERE id = ?", (status, now, post_id))

    def next_approved_due(self) -> QueuedPost | None:
        today = date.today().isoformat()
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT id, due_date, topic, content_type, status, content
                FROM posts
                WHERE status = 'approved' AND due_date <= ?
                ORDER BY due_date, id
                LIMIT 1
                """,
                (today,),
            ).fetchone()
        return QueuedPost(*row) if row else None

    def mark_published(self, post_id: int, published_urn: str) -> None:
        now = datetime.utcnow().isoformat(timespec="seconds")
        with self._connect() as connection:
            connection.execute(
                "UPDATE posts SET status = 'published', published_urn = ?, updated_at = ? WHERE id = ?",
                (published_urn, now, post_id),
            )
