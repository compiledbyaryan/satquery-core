"""Durable SQLite-backed job lifecycle, outcomes, and feedback store (Tickets T03 & T11)."""
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
                    owner_id TEXT NOT NULL DEFAULT 'scientist_01',
                    idempotency_key TEXT UNIQUE,
                    query TEXT NOT NULL,
                    assets_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    task TEXT,
                    error TEXT,
                    worker_id TEXT,
                    heartbeat_at TEXT,
                    outcome_json TEXT,
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
            conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    feedback_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    claim_id TEXT,
                    version TEXT NOT NULL,
                    owner_id TEXT NOT NULL,
                    rating INTEGER,
                    notes TEXT NOT NULL,
                    is_private INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(run_id) REFERENCES runs(run_id)
                )
            """)
            conn.commit()

    def create_run(
        self,
        query: str,
        assets: Dict[str, str],
        owner_id: str = "scientist_01",
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

            count = conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
            run_id = f"run_{count + 1:04d}"

            conn.execute(
                """
                INSERT INTO runs (
                    run_id, owner_id, idempotency_key, query, assets_json,
                    status, task, error, outcome_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    run_id,
                    owner_id,
                    idempotency_key,
                    query,
                    json.dumps(assets),
                    "queued",
                    "analysis",
                    None,
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

    def save_outcome(self, run_id: str, outcome_data: Dict[str, Any]) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._get_conn() as conn:
            conn.execute(
                "UPDATE runs SET outcome_json = ?, updated_at = ? WHERE run_id = ?",
                (json.dumps(outcome_data), now, run_id),
            )
            conn.commit()

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

    def record_feedback(
        self,
        run_id: str,
        owner_id: str,
        notes: str,
        claim_id: Optional[str] = None,
        version: str = "1.0",
        rating: Optional[int] = None,
        is_private: bool = True,
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        with self._get_conn() as conn:
            count = conn.execute("SELECT COUNT(*) FROM feedback").fetchone()[0]
            fb_id = f"fb_{count + 1:04d}"
            conn.execute(
                """
                INSERT INTO feedback (
                    feedback_id, run_id, claim_id, version, owner_id,
                    rating, notes, is_private, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    fb_id,
                    run_id,
                    claim_id,
                    version,
                    owner_id,
                    rating,
                    notes,
                    1 if is_private else 0,
                    now,
                ),
            )
            conn.commit()
            return {
                "feedback_id": fb_id,
                "run_id": run_id,
                "claim_id": claim_id,
                "version": version,
                "owner_id": owner_id,
                "rating": rating,
                "notes": notes,
                "is_private": is_private,
                "created_at": now,
            }

    def get_feedback_for_run(
        self, run_id: str, caller_id: str
    ) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM feedback WHERE run_id = ?", (run_id,)
            ).fetchall()
            results = []
            for r in rows:
                item = dict(r)
                item["is_private"] = bool(item["is_private"])
                # Privacy check: private feedback is hidden unless viewed by the author
                if item["is_private"] and item["owner_id"] != caller_id:
                    continue
                results.append(item)
            return results

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        d = dict(row)
        d["assets"] = json.loads(d["assets_json"])
        if d.get("outcome_json"):
            d["outcome"] = json.loads(d["outcome_json"])
        else:
            d["outcome"] = None
        del d["assets_json"]
        return d

    def close(self):
        if self._conn:
            self._conn.close()
