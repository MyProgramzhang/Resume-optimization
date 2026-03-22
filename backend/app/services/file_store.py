from __future__ import annotations

import json
from pathlib import Path

from app.core.config import settings


class FileStore:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or settings.storage_root
        self.root.mkdir(parents=True, exist_ok=True)

    def job_dir(self, job_id: str) -> Path:
        path = self.root / job_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def save_binary(self, job_id: str, filename: str, content: bytes) -> Path:
        path = self.job_dir(job_id) / filename
        path.write_bytes(content)
        return path

    def save_text(self, job_id: str, filename: str, content: str) -> Path:
        path = self.job_dir(job_id) / filename
        path.write_text(content, encoding="utf-8")
        return path

    def save_json(self, job_id: str, filename: str, content: dict) -> Path:
        path = self.job_dir(job_id) / filename
        path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
        return path
