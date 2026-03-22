from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from app.core.config import settings


class JobRepository:
    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or settings.db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self.connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    current_step TEXT NOT NULL,
                    progress INTEGER NOT NULL,
                    input_json TEXT NOT NULL,
                    result_json TEXT,
                    warnings_json TEXT,
                    error_message TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def create_job(self, job_id: str, input_payload: dict[str, Any]) -> None:
        now = self._now()
        with self.connection() as connection:
            connection.execute(
                """
                INSERT INTO jobs (job_id, status, current_step, progress, input_json, warnings_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job_id,
                    "queued",
                    "uploaded",
                    0,
                    json.dumps(input_payload, ensure_ascii=False),
                    json.dumps([], ensure_ascii=False),
                    now,
                    now,
                ),
            )

    def update_status(
        self,
        job_id: str,
        *,
        status: str,
        current_step: str,
        progress: int,
        warnings: list[str] | None = None,
        error_message: str | None = None,
    ) -> None:
        existing = self.get_job(job_id)
        merged_warnings = warnings if warnings is not None else existing["warnings"]
        with self.connection() as connection:
            connection.execute(
                """
                UPDATE jobs
                SET status = ?, current_step = ?, progress = ?, warnings_json = ?, error_message = ?, updated_at = ?
                WHERE job_id = ?
                """,
                (
                    status,
                    current_step,
                    progress,
                    json.dumps(merged_warnings, ensure_ascii=False),
                    error_message,
                    self._now(),
                    job_id,
                ),
            )

    def save_result(self, job_id: str, result_payload: dict[str, Any]) -> None:
        with self.connection() as connection:
            connection.execute(
                """
                UPDATE jobs
                SET status = ?, current_step = ?, progress = ?, result_json = ?, updated_at = ?
                WHERE job_id = ?
                """,
                (
                    "completed",
                    "finished",
                    100,
                    json.dumps(result_payload, ensure_ascii=False),
                    self._now(),
                    job_id,
                ),
            )

    def get_job(self, job_id: str) -> dict[str, Any]:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT * FROM jobs WHERE job_id = ?",
                (job_id,),
            ).fetchone()
        if row is None:
            raise KeyError(job_id)
        result = dict(row)
        result["input"] = json.loads(result.pop("input_json"))
        result["warnings"] = json.loads(result.pop("warnings_json") or "[]")
        result["result"] = json.loads(result.pop("result_json")) if result.get("result_json") else None
        result.pop("result_json", None)
        return result

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()
