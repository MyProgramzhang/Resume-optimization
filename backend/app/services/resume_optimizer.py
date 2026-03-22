from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field, ValidationError

from app.integrations.llm_client import LlmClient
from app.schemas.job import JobMode
from app.schemas.resume import ResumeSchema


class OptimizeResult(BaseModel):
    optimized_resume: ResumeSchema
    change_summary: list[str] = Field(default_factory=list)


class ResumeOptimizer:
    def __init__(self, llm_client: LlmClient | None = None) -> None:
        self.llm_client = llm_client or LlmClient()
        self.system_prompt = Path(__file__).resolve().parents[1] / "prompts" / "optimize_resume.md"

    def optimize(
        self,
        resume: ResumeSchema,
        *,
        mode: JobMode,
        job_description: str = "",
        target_role: str = "",
        notes: str = "",
    ) -> OptimizeResult:
        if self.llm_client.use_mock or not self.llm_client.api_key:
            return self._mock_optimize(resume, mode=mode, job_description=job_description, target_role=target_role)

        system_prompt = self.system_prompt.read_text(encoding="utf-8")
        user_prompt = (
            f"优化模式：{mode}\n"
            f"目标岗位：{target_role}\n"
            f"补充说明：{notes}\n"
            f"职位描述：\n{job_description}\n\n"
            f"原始简历 JSON：\n{resume.model_dump_json(indent=2)}"
        )
        payload = self.llm_client.generate_json(system_prompt, user_prompt)
        try:
            return OptimizeResult.model_validate(payload)
        except ValidationError as exc:
            raise ValueError(f"优化后简历 JSON 校验失败：{exc}") from exc

    @staticmethod
    def _mock_optimize(
        resume: ResumeSchema,
        *,
        mode: JobMode,
        job_description: str,
        target_role: str,
    ) -> OptimizeResult:
        data = resume.model_copy(deep=True)
        if data.summary:
            suffix = " 已根据目标岗位进行了定向强化。" if mode == "jd_targeted" else " 已进行了更专业的表达优化。"
            data.summary = f"{data.summary.rstrip('。.')}{suffix}"
        for item in data.experience:
            item.bullets = [ResumeOptimizer._improve_bullet(bullet, mode, target_role) for bullet in item.bullets]
        summary = [
            "强化了经历描述中的动作表达和结果感。",
            "提升了各模块的可读性和整体一致性。",
        ]
        if mode == "jd_targeted":
            summary.append("根据目标岗位要求调整了内容重点。")
        if job_description.strip():
            summary.append("在保留原始事实的前提下突出相关关键词。")
        return OptimizeResult(optimized_resume=data, change_summary=summary)

    @staticmethod
    def _improve_bullet(bullet: str, mode: JobMode, target_role: str) -> str:
        cleaned = bullet.strip()
        if not cleaned:
            return cleaned
        if mode == "jd_targeted":
            role_text = f"，更贴合{target_role}岗位要求" if target_role else "，更贴合目标岗位要求"
            return f"负责{cleaned}{role_text}，并突出可量化成果。"
        return f"负责{cleaned}，并进一步明确职责范围和业务影响。"
