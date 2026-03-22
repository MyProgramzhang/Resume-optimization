from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


JobMode = Literal["general", "jd_targeted"]
JobStatus = Literal[
    "queued",
    "parsing",
    "structuring",
    "optimizing",
    "diffing",
    "completed",
    "failed",
]


class CreateJobResponse(BaseModel):
    job_id: str
    status: JobStatus
    current_step: str
    progress: int
    created_at: datetime


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    current_step: str
    progress: int
    error_message: str | None = None
    warnings: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
