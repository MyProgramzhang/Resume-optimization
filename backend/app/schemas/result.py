from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.resume import ResumeSchema, SectionName


class DiffBlock(BaseModel):
    section: SectionName
    block_id: str
    old_text: str
    new_text: str
    change_type: str
    reason: str


class ResultInputMeta(BaseModel):
    mode: str
    target_role: str = ""
    original_filename: str


class ResultMeta(BaseModel):
    processing_ms: int
    parser_warning: str | None = None
    model_name: str


class JobResultResponse(BaseModel):
    job_id: str
    input: ResultInputMeta
    parsed_resume: ResumeSchema
    optimized_resume: ResumeSchema
    change_summary: list[str] = Field(default_factory=list)
    diff_blocks: list[DiffBlock] = Field(default_factory=list)
    meta: ResultMeta
