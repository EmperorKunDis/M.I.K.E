"""Lokální SQLite paměť, historie odpovědí a bezpečné návrhy tuneru."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .paths import secure_file

SCHEMA = """
CREATE TABLE IF NOT EXISTS turns(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
    text TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'voice',
    latency_ms INTEGER
);
CREATE INDEX IF NOT EXISTS idx_turns_created ON turns(created_at);
CREATE VIRTUAL TABLE IF NOT EXISTS turns_fts USING fts5(
    text, content='turns', content_rowid='id', tokenize='unicode61 remove_diacritics 2'
);
CREATE TRIGGER IF NOT EXISTS turns_ai AFTER INSERT ON turns BEGIN
    INSERT INTO turns_fts(rowid, text) VALUES (new.id, new.text);
END;
CREATE TABLE IF NOT EXISTS facts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fact_key TEXT NOT NULL UNIQUE,
    value TEXT NOT NULL,
    source TEXT NOT NULL CHECK(source IN ('explicit', 'automatic')),
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS evaluations(
    turn_id INTEGER PRIMARY KEY REFERENCES turns(id),
    relevance INTEGER NOT NULL,
    clarity INTEGER NOT NULL,
    grounded INTEGER NOT NULL,
    total REAL NOT NULL,
    note TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS prompt_candidates(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    rationale TEXT NOT NULL,
    addendum TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('proposed', 'approved', 'rejected'))
);
"""


def now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.path.parent.chmod(0o700)
        with self.connect() as connection:
            connection.executescript(SCHEMA)
        secure_file(self.path)
        for suffix in ("-wal", "-shm"):
            secure_file(Path(f"{self.path}{suffix}"))

    @contextmanager
    def connect(self, *, readonly: bool = False) -> Iterator[sqlite3.Connection]:
        if readonly:
            connection = sqlite3.connect(f"file:{self.path}?mode=ro", uri=True, timeout=3)
        else:
            connection = sqlite3.connect(self.path, timeout=3)
            connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA busy_timeout=3000")
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            if not readonly:
                connection.commit()
        finally:
            connection.close()

    def add_turn(
        self,
        role: str,
        text: str,
        *,
        source: str = "voice",
        latency_ms: int | None = None,
    ) -> int:
        with self.connect() as connection:
            cursor = connection.execute(
                "INSERT INTO turns(created_at, role, text, source, latency_ms) VALUES (?, ?, ?, ?, ?)",
                (now_iso(), role, text.strip(), source, latency_ms),
            )
            return int(cursor.lastrowid)

    def recent_turns(self, limit: int = 8) -> list[dict[str, Any]]:
        with self.connect(readonly=True) as connection:
            rows = connection.execute(
                "SELECT id, created_at, role, text, source, latency_ms FROM turns ORDER BY id DESC LIMIT ?",
                (max(1, min(limit, 100)),),
            ).fetchall()
        return [dict(row) for row in reversed(rows)]

    def remember(self, key: str, value: str, *, source: str = "explicit") -> None:
        stamp = now_iso()
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO facts(fact_key, value, source, active, created_at, updated_at) "
                "VALUES (?, ?, ?, 1, ?, ?) ON CONFLICT(fact_key) DO UPDATE SET "
                "value=excluded.value, source=CASE WHEN facts.source='explicit' AND excluded.source='automatic' "
                "THEN facts.source ELSE excluded.source END, active=1, updated_at=excluded.updated_at "
                "WHERE facts.source!='explicit' OR excluded.source='explicit'",
                (key.casefold().strip(), value.strip(), source, stamp, stamp),
            )

    def forget(self, key: str) -> bool:
        with self.connect() as connection:
            cursor = connection.execute(
                "UPDATE facts SET active=0, updated_at=? WHERE fact_key=? AND active=1",
                (now_iso(), key.casefold().strip()),
            )
            return cursor.rowcount > 0

    def facts(self, limit: int = 30) -> list[dict[str, Any]]:
        with self.connect(readonly=True) as connection:
            rows = connection.execute(
                "SELECT fact_key, value, source, updated_at FROM facts WHERE active=1 "
                "ORDER BY CASE source WHEN 'explicit' THEN 0 ELSE 1 END, updated_at DESC LIMIT ?",
                (max(1, min(limit, 100)),),
            ).fetchall()
        return [dict(row) for row in rows]

    def search_turns(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        words = [word for word in query.replace('"', " ").split() if len(word) >= 3][:8]
        if not words:
            return []
        expression = " OR ".join(f'"{word}"' for word in words)
        with self.connect(readonly=True) as connection:
            try:
                rows = connection.execute(
                    "SELECT t.id, t.created_at, t.role, t.text FROM turns_fts f "
                    "JOIN turns t ON t.id=f.rowid WHERE turns_fts MATCH ? ORDER BY rank LIMIT ?",
                    (expression, max(1, min(limit, 20))),
                ).fetchall()
            except sqlite3.OperationalError:
                return []
        return [dict(row) for row in rows]

    def add_evaluation(
        self,
        turn_id: int,
        relevance: int,
        clarity: int,
        grounded: int,
        note: str = "",
    ) -> None:
        scores = [max(0, min(int(value), 5)) for value in (relevance, clarity, grounded)]
        with self.connect() as connection:
            connection.execute(
                "INSERT OR REPLACE INTO evaluations(turn_id, relevance, clarity, grounded, total, note, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (turn_id, *scores, sum(scores) / len(scores), note[:500], now_iso()),
            )

    def evaluation_summary(self, limit: int = 50) -> dict[str, Any]:
        with self.connect(readonly=True) as connection:
            row = connection.execute(
                "SELECT COUNT(*) count, AVG(total) average, MIN(total) minimum, MAX(total) maximum "
                "FROM (SELECT total FROM evaluations ORDER BY created_at DESC LIMIT ?)",
                (max(1, min(limit, 500)),),
            ).fetchone()
        return dict(row) if row else {"count": 0, "average": None, "minimum": None, "maximum": None}

    def propose_prompt(self, rationale: str, addendum: str) -> int:
        with self.connect() as connection:
            cursor = connection.execute(
                "INSERT INTO prompt_candidates(created_at, rationale, addendum, status) VALUES (?, ?, ?, 'proposed')",
                (now_iso(), rationale[:1000], addendum[:1000]),
            )
            return int(cursor.lastrowid)

    def export_redacted_status(self) -> str:
        """Diagnostický JSON bez přepisů a faktů."""
        return json.dumps(
            {"turns": len(self.recent_turns(100)), "evaluations": self.evaluation_summary()},
            ensure_ascii=False,
        )
