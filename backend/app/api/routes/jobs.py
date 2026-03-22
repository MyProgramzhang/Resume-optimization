from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from app.repositories.job_repo import JobRepository
from app.schemas.job import CreateJobResponse, JobMode, JobStatusResponse
from app.schemas.result import DiffBlock, JobResultResponse
from app.schemas.resume import ResumeSchema
from app.services.file_store import FileStore
from app.services.job_runner import JobRunner
from app.services.resume_pdf_exporter import ResumePdfExporter
from app.services.template_resume_pdf_exporter import TemplateResumePdfExporter
from app.utils.validators import validate_job_inputs, validate_pdf_upload


router = APIRouter(prefix="/api/jobs", tags=["jobs"])
repository = JobRepository()
file_store = FileStore()
runner = JobRunner(repository=repository, file_store=file_store)
pdf_exporter = ResumePdfExporter()
template_pdf_exporter = TemplateResumePdfExporter()


@router.post("", response_model=CreateJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_job(
    background_tasks: BackgroundTasks,
    resume_file: UploadFile = File(...),
    mode: JobMode = Form(...),
    job_description: str = Form(""),
    target_role: str = Form(""),
    notes: str = Form(""),
) -> CreateJobResponse:
    content = await resume_file.read()
    validate_pdf_upload(resume_file, content)
    validate_job_inputs(mode, job_description)

    job_id = str(uuid.uuid4())
    file_store.save_binary(job_id, "original.pdf", content)
    repository.create_job(
        job_id,
        {
            "mode": mode,
            "job_description": job_description,
            "target_role": target_role,
            "notes": notes,
            "original_filename": resume_file.filename or "resume.pdf",
        },
    )
    background_tasks.add_task(runner.run, job_id)

    job = repository.get_job(job_id)
    return CreateJobResponse(
        job_id=job_id,
        status=job["status"],
        current_step=job["current_step"],
        progress=job["progress"],
        created_at=datetime.fromisoformat(job["created_at"]),
    )


@router.get("/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: str) -> JobStatusResponse:
    job = _get_job_or_404(job_id)
    return JobStatusResponse(
        job_id=job["job_id"],
        status=job["status"],
        current_step=job["current_step"],
        progress=job["progress"],
        error_message=job["error_message"],
        warnings=job["warnings"],
        created_at=datetime.fromisoformat(job["created_at"]),
        updated_at=datetime.fromisoformat(job["updated_at"]),
    )


@router.get("/{job_id}/result", response_model=JobResultResponse)
def get_job_result(job_id: str) -> JobResultResponse:
    job = _get_job_or_404(job_id)
    if job["status"] != "completed" or job["result"] is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="任务结果尚未生成完成。")
    return JobResultResponse.model_validate(job["result"])


@router.get("/{job_id}/optimized-pdf")
def download_optimized_pdf(job_id: str) -> FileResponse:
    job = _get_job_or_404(job_id)
    if job["status"] != "completed" or job["result"] is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="任务结果尚未生成完成。")

    optimized_resume = ResumeSchema.model_validate(job["result"]["optimized_resume"])
    pdf_path = _ensure_optimized_pdf(
        job_id,
        job["input"].get("original_filename", "resume.pdf"),
        optimized_resume,
        job["result"].get("diff_blocks", []),
    )
    filename = f"{Path(job['input'].get('original_filename', 'resume')).stem}_优化版.pdf"
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=filename,
    )


def _get_job_or_404(job_id: str) -> dict:
    try:
        return repository.get_job(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到对应任务。") from exc


def _ensure_optimized_pdf(job_id: str, original_filename: str, resume: ResumeSchema, diff_blocks: list[dict]) -> Path:
    target_path = file_store.job_dir(job_id) / "optimized_resume.pdf"
    if not target_path.exists():
        original_pdf = file_store.job_dir(job_id) / "original.pdf"
        generated = False
        if original_pdf.exists():
            try:
                parsed_diff_blocks = [DiffBlock.model_validate(block) for block in diff_blocks]
                _pdf_path, applied_blocks = template_pdf_exporter.export(
                    target_path,
                    original_pdf,
                    parsed_diff_blocks,
                )
                generated = applied_blocks > 0 or not parsed_diff_blocks
            except Exception:
                generated = False
        if not generated:
            pdf_exporter.export(target_path, resume)
    return target_path
