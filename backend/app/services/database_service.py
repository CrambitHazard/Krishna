"""
KRISHNA — SQLite database service.

Provides persistent storage for quiz attempts, learning progress,
and session tracking using raw sqlite3 (no ORM).

Storage
-------
The database file is stored at ``backend/data/krishna.db``.
Tables are auto-created on first access via ``_ensure_tables()``.

Thread safety
-------------
SQLite connections are not shared across threads.  Each public method
opens its own connection (short-lived), which is safe for the async
FastAPI model where blocking calls are offloaded via ``asyncio.to_thread``.

Usage:
    from app.services.database_service import DatabaseService

    db = DatabaseService()
    await db.save_quiz_attempt(session_id, topic, score, total, details)
    await db.update_progress(topic, score, total)
    progress = await db.get_progress(topic)
"""

from __future__ import annotations

import asyncio
import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ── database path ───────────────────────────────────────────────────────
_DATA_DIR = Path(__file__).resolve().parents[2] / "data"
_DB_PATH = _DATA_DIR / "krishna.db"


class DatabaseService:
    """Thin async wrapper around a SQLite database."""

    def __init__(self, db_path: Path | str | None = None) -> None:
        self._db_path = Path(db_path) if db_path else _DB_PATH
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_tables()
        logger.info("DatabaseService ready — %s", self._db_path)

    # ── connection helper ───────────────────────────────────────────────
    def _connect(self) -> sqlite3.Connection:
        """Return a new connection with row_factory set."""
        conn = sqlite3.connect(str(self._db_path))
        conn.row_factory = sqlite3.Row       # dict-like access
        conn.execute("PRAGMA journal_mode=WAL")  # better concurrency
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    # ── schema migration ────────────────────────────────────────────────
    def _ensure_tables(self) -> None:
        """Create tables if they don't exist (safe to call repeatedly)."""
        conn = self._connect()
        try:
            conn.executescript("""
                -- ── Users (minimal) ────────────────────────────────────
                CREATE TABLE IF NOT EXISTS users (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    username     TEXT    UNIQUE NOT NULL,
                    created_at   TEXT    NOT NULL DEFAULT (datetime('now'))
                );

                -- ── Sessions ───────────────────────────────────────────
                CREATE TABLE IF NOT EXISTS sessions (
                    id           TEXT    PRIMARY KEY,
                    user_id      INTEGER,
                    created_at   TEXT    NOT NULL DEFAULT (datetime('now')),
                    last_active  TEXT    NOT NULL DEFAULT (datetime('now')),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );

                -- ── Quiz attempts ──────────────────────────────────────
                CREATE TABLE IF NOT EXISTS quiz_attempts (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id   TEXT    NOT NULL,
                    topic        TEXT    NOT NULL,
                    score        INTEGER NOT NULL,
                    total        INTEGER NOT NULL,
                    percentage   REAL    NOT NULL,
                    details      TEXT,
                    timestamp    TEXT    NOT NULL DEFAULT (datetime('now'))
                );

                CREATE INDEX IF NOT EXISTS idx_quiz_session
                    ON quiz_attempts(session_id);
                CREATE INDEX IF NOT EXISTS idx_quiz_topic
                    ON quiz_attempts(topic);

                -- ── Progress (per-topic aggregate) ─────────────────────
                CREATE TABLE IF NOT EXISTS progress (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic        TEXT    UNIQUE NOT NULL,
                    accuracy     REAL    NOT NULL DEFAULT 0.0,
                    attempts     INTEGER NOT NULL DEFAULT 0,
                    total_score  INTEGER NOT NULL DEFAULT 0,
                    total_questions INTEGER NOT NULL DEFAULT 0,
                    last_updated TEXT    NOT NULL DEFAULT (datetime('now'))
                );

                CREATE INDEX IF NOT EXISTS idx_progress_topic
                    ON progress(topic);
            """)
            conn.commit()
            logger.debug("Database tables ensured.")
        finally:
            conn.close()

    # ═══════════════════════════════════════════════════════════════════
    #  Quiz Attempts
    # ═══════════════════════════════════════════════════════════════════

    async def save_quiz_attempt(
        self,
        session_id: str,
        topic: str,
        score: int,
        total: int,
        details: dict[str, Any] | None = None,
    ) -> int:
        """
        Persist a quiz attempt.

        Parameters
        ----------
        session_id : str
            The session that took the quiz.
        topic : str
            Quiz topic.
        score : int
            Number of correct answers.
        total : int
            Total number of questions.
        details : dict | None
            Optional JSON-serialisable metadata (e.g. per-question feedback).

        Returns
        -------
        int
            The row ID of the inserted attempt.
        """
        percentage = round((score / total) * 100, 1) if total > 0 else 0.0
        details_json = json.dumps(details, ensure_ascii=False) if details else None
        now = datetime.now(timezone.utc).isoformat()

        def _insert() -> int:
            conn = self._connect()
            try:
                cur = conn.execute(
                    """
                    INSERT INTO quiz_attempts
                        (session_id, topic, score, total, percentage, details, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (session_id, topic, score, total, percentage, details_json, now),
                )
                conn.commit()
                return cur.lastrowid or 0
            finally:
                conn.close()

        row_id = await asyncio.to_thread(_insert)
        logger.info(
            "Saved quiz attempt #%d — %s: %d/%d (%.1f%%)",
            row_id, topic, score, total, percentage,
        )
        return row_id

    async def get_quiz_attempts(
        self,
        session_id: str | None = None,
        topic: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Retrieve quiz attempts, optionally filtered by session or topic."""

        def _query() -> list[dict[str, Any]]:
            conn = self._connect()
            try:
                clauses: list[str] = []
                params: list[Any] = []

                if session_id:
                    clauses.append("session_id = ?")
                    params.append(session_id)
                if topic:
                    clauses.append("topic = ?")
                    params.append(topic)

                where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
                sql = f"""
                    SELECT id, session_id, topic, score, total,
                           percentage, details, timestamp
                    FROM quiz_attempts
                    {where}
                    ORDER BY timestamp DESC
                    LIMIT ?
                """
                params.append(limit)
                rows = conn.execute(sql, params).fetchall()
                return [dict(r) for r in rows]
            finally:
                conn.close()

        return await asyncio.to_thread(_query)

    # ═══════════════════════════════════════════════════════════════════
    #  Progress
    # ═══════════════════════════════════════════════════════════════════

    async def update_progress(
        self,
        topic: str,
        score: int,
        total: int,
    ) -> dict[str, Any]:
        """
        Update the running accuracy for a *topic*.

        Uses an upsert: inserts if the topic doesn't exist,
        otherwise increments the running totals and recalculates accuracy.

        Returns the updated progress row.
        """
        now = datetime.now(timezone.utc).isoformat()

        def _upsert() -> dict[str, Any]:
            conn = self._connect()
            try:
                conn.execute(
                    """
                    INSERT INTO progress
                        (topic, accuracy, attempts, total_score,
                         total_questions, last_updated)
                    VALUES (?, ?, 1, ?, ?, ?)
                    ON CONFLICT(topic) DO UPDATE SET
                        total_score     = total_score     + excluded.total_score,
                        total_questions = total_questions  + excluded.total_questions,
                        attempts        = attempts         + 1,
                        accuracy        = ROUND(
                            CAST(total_score + excluded.total_score AS REAL)
                            / (total_questions + excluded.total_questions) * 100,
                            1
                        ),
                        last_updated    = excluded.last_updated
                    """,
                    (
                        topic,
                        round((score / total) * 100, 1) if total > 0 else 0.0,
                        score,
                        total,
                        now,
                    ),
                )
                conn.commit()

                row = conn.execute(
                    "SELECT * FROM progress WHERE topic = ?", (topic,)
                ).fetchone()
                return dict(row) if row else {}
            finally:
                conn.close()

        result = await asyncio.to_thread(_upsert)
        logger.info("Updated progress for '%s': %s", topic, result)
        return result

    async def get_progress(
        self,
        topic: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Retrieve progress for a topic, or all topics if *topic* is None.
        """

        def _query() -> list[dict[str, Any]]:
            conn = self._connect()
            try:
                if topic:
                    rows = conn.execute(
                        "SELECT * FROM progress WHERE topic = ?", (topic,)
                    ).fetchall()
                else:
                    rows = conn.execute(
                        "SELECT * FROM progress ORDER BY last_updated DESC"
                    ).fetchall()
                return [dict(r) for r in rows]
            finally:
                conn.close()

        return await asyncio.to_thread(_query)

    # ═══════════════════════════════════════════════════════════════════
    #  Sessions
    # ═══════════════════════════════════════════════════════════════════

    async def create_session(self, session_id: str) -> None:
        """Create a new session record."""

        def _insert() -> None:
            conn = self._connect()
            try:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO sessions (id)
                    VALUES (?)
                    """,
                    (session_id,),
                )
                conn.commit()
            finally:
                conn.close()

        await asyncio.to_thread(_insert)

    async def touch_session(self, session_id: str) -> None:
        """Update the last_active timestamp for a session."""
        now = datetime.now(timezone.utc).isoformat()

        def _update() -> None:
            conn = self._connect()
            try:
                conn.execute(
                    "UPDATE sessions SET last_active = ? WHERE id = ?",
                    (now, session_id),
                )
                conn.commit()
            finally:
                conn.close()

        await asyncio.to_thread(_update)
