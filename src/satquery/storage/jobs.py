"""Durable SQLite-backed job lifecycle store (Ticket T03)."""
import json
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

VALID_STATES = {
    "queued",
    "validating",
    "running",
    "verifying",
    "succeeded",
    "partial",
    "failed",
    "cancelled",
}

TERMINAL_STATES = {"succeeded", "partial", "failed", "cancelled"}


class JobStore:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        # Keep a single open connection so in-memory databases persist across queries
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        return self._conn

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    idempotency_key TEXT UNIQUE,
                    query TEXT NOT NULL,
                    assets_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    task TEXT,
                    error TEXT,
                    worker_id TEXT,
                    heartbeat_at TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    step_id TEXT NOT NULL,
                    tool TEXT NOT NULL,
                    status TEXT NOT NULL,
                    payload_json TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(run_id) REFERENCES runs(run_id)
                )
            """)
            conn.commit()

    def create_run(
        self,
        query: str,
        assets: Dict[str, str],
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        with self._get_conn() as conn:
            if idempotency_key:
                row = conn.execute(
                    "SELECT * FROM runs WHERE idempotency_key = ?",
                    (idempotency_key,),
                ).fetchone()
                if row:
                    return self._row_to_dict(row)

            # Generate run_id
            count = conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
            run_id = f"run_{count + 1:04d}"

            conn.execute(
                """
                INSERT INTO runs (
                    run_id, idempotency_key, query, assets_json,
                    status, task, error, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    run_id,
                    idempotency_key,
                    query,
                    json.dumps(assets),
                    "queued",
                    "analysis",
                    None,
                    now,
                    now,
                ),
            )
            conn.commit()
            return self.get_run(run_id)

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM runs WHERE run_id = ?", (run_id,)
            ).fetchone()
            if not row:
                return None
            return self._row_to_dict(row)

    def update_status(
        self, run_id: str, new_status: str, error: Optional[str] = None
    ) -> Dict[str, Any]:
        if new_status not in VALID_STATES:
            raise ValueError(f"Invalid state: {new_status}")

        now = datetime.now(timezone.utc).isoformat()
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT status FROM runs WHERE run_id = ?", (run_id,)
            ).fetchone()
            if not row:
                raise KeyError(f"Run {run_id} not found")

            current_status = row["status"]
            if current_status in TERMINAL_STATES:
                raise ValueError(
                    f"Cannot transition from terminal state '{current_status}' to '{new_status}'"
                )

            conn.execute(
                """
                UPDATE runs
                SET status = ?, error = ?, updated_at = ?
                WHERE run_id = ?
            """,
                (new_status, error, now, run_id),
            )
            conn.commit()
            return self.get_run(run_id)

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        d = dict(row)
        d["assets"] = json.loads(d["assets_json"])
        del d["assets_json"]
        return d

    def close(self):
        if self._conn:
            self._conn.close()
