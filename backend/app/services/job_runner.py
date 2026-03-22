from __future__ import annotations

import logging
import time

from app.core.config import settings
from app.repositories.job_repo import JobRepository
from app.services.diff_builder import DiffBuilder
from app.services.file_store import FileStore
from app.services.pdf_parser import PdfParser
from app.services.resume_optimizer import ResumeOptimizer
from app.services.resume_structurer import ResumeStructurer


logger = logging.getLogger(__name__)


class JobRunner:
    def __init__(
        self,
        repository: JobRepository | None = None,
        file_store: FileStore | None = None,
        parser: PdfParser | None = None,
        structurer: ResumeStructurer | None = None,
        optimizer: ResumeOptimizer | None = None,
        diff_builder: DiffBuilder | None = None,
    ) -> None:
        self.repository = repository or JobRepository()
        self.file_store = file_store or FileStore()
        self.parser = parser or PdfParser()
        self.structurer = structurer or ResumeStructurer()
        self.optimizer = optimizer or ResumeOptimizer()
        self.diff_builder = diff_builder or DiffBuilder()

    def run(self, job_id: str) -> None:
        started_at = time.perf_counter()
        job = self.repository.get_job(job_id)
        inputs = job["input"]
        warnings = list(job["warnings"])
        pdf_path = self.file_store.job_dir(job_id) / "original.pdf"

        try:
            self.repository.update_status(job_id, status="parsing", current_step="extracting_pdf_text", progress=15)
            parse_result = self.parser.parse(pdf_path)
            self.file_store.save_text(job_id, "extracted.txt", parse_result.text)
            if parse_result.warning:
                warnings.append(parse_result.warning)
                self.repository.update_status(
                    job_id,
                    status="parsing",
                    current_step="extracting_pdf_text",
                    progress=25,
                    warnings=warnings,
                )

            self.repository.update_status(
                job_id,
                status="structuring",
                current_step="structuring_resume",
                progress=40,
                warnings=warnings,
            )
            parsed_resume = self.structurer.structure(parse_result.text)
            self.file_store.save_json(job_id, "parsed_resume.json", parsed_resume.model_dump())

            self.repository.update_status(
                job_id,
                status="optimizing",
                current_step="optimizing_resume",
                progress=65,
                warnings=warnings,
            )
            optimized = self.optimizer.optimize(
                parsed_resume,
                mode=inputs["mode"],
                job_description=inputs.get("job_description", ""),
                target_role=inputs.get("target_role", ""),
                notes=inputs.get("notes", ""),
            )
            self.file_store.save_json(job_id, "optimized_resume.json", optimized.optimized_resume.model_dump())

            self.repository.update_status(
                job_id,
                status="diffing",
                current_step="building_diff",
                progress=85,
                warnings=warnings,
            )
            diff_blocks = self.diff_builder.build(parsed_resume, optimized.optimized_resume)

            result_payload = {
                "job_id": job_id,
                "input": {
                    "mode": inputs["mode"],
                    "target_role": inputs.get("target_role", ""),
                    "original_filename": inputs["original_filename"],
                },
                "parsed_resume": parsed_resume.model_dump(),
                "optimized_resume": optimized.optimized_resume.model_dump(),
                "change_summary": optimized.change_summary,
                "diff_blocks": [block.model_dump() for block in diff_blocks],
                "meta": {
                    "processing_ms": int((time.perf_counter() - started_at) * 1000),
                    "parser_warning": parse_result.warning,
                    "model_name": settings.model_name if not settings.use_mock_llm else "mock-llm",
                },
            }
            self.file_store.save_json(job_id, "result.json", result_payload)
            self.repository.save_result(job_id, result_payload)
        except Exception as exc:
            logger.exception("Job %s failed", job_id)
            self.repository.update_status(
                job_id,
                status="failed",
                current_step="failed",
                progress=100,
                warnings=warnings,
                error_message=str(exc),
            )
