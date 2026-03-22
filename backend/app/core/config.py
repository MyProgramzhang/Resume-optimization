from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
PROJECT_DIR = BASE_DIR.parent

load_dotenv(BASE_DIR / ".env")


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_optional_bool(name: str) -> bool | None:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return None
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    model_api_key: str = os.getenv("MODEL_API_KEY", "")
    model_base_url: str = os.getenv("MODEL_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    model_name: str = os.getenv("MODEL_NAME", "qwen-plus")
    model_thinking_type: str = os.getenv("MODEL_THINKING_TYPE", "").strip()
    model_enable_thinking: bool | None = _env_optional_bool("MODEL_ENABLE_THINKING")
    use_mock_llm: bool = _env_bool("USE_MOCK_LLM", True)
    db_path: Path = PROJECT_DIR / os.getenv("DB_PATH", "backend/storage/app.db")
    storage_root: Path = PROJECT_DIR / os.getenv("STORAGE_ROOT", "backend/storage/jobs")
    max_upload_mb: int = int(os.getenv("MAX_UPLOAD_MB", "10"))
    max_pdf_pages: int = int(os.getenv("MAX_PDF_PAGES", "10"))
    job_timeout_seconds: int = int(os.getenv("JOB_TIMEOUT_SECONDS", "180"))
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")


settings = Settings()
