from __future__ import annotations

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings
from app.schemas.job import JobMode


def validate_pdf_upload(upload: UploadFile, content: bytes) -> None:
    if not upload.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="缺少文件名。")
    if not upload.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="仅支持 PDF 文件。")
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小不能超过 {settings.max_upload_mb} MB。",
        )


def validate_job_inputs(mode: JobMode, job_description: str | None) -> None:
    if mode == "jd_targeted" and not (job_description or "").strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="岗位定制模式下必须填写职位描述。",
        )
