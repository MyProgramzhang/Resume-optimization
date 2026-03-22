from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError

from app.integrations.llm_client import LlmClient
from app.schemas.resume import ResumeSchema


class ResumeStructurer:
    def __init__(self, llm_client: LlmClient | None = None) -> None:
        self.llm_client = llm_client or LlmClient()
        self.system_prompt = Path(__file__).resolve().parents[1] / "prompts" / "structure_resume.md"

    def structure(self, raw_text: str) -> ResumeSchema:
        if self.llm_client.use_mock or not self.llm_client.api_key:
            return self._heuristic_structure(raw_text)

        system_prompt = self.system_prompt.read_text(encoding="utf-8")
        user_prompt = f"简历原文如下：\n{raw_text}"
        payload = self.llm_client.generate_json(system_prompt, user_prompt)
        try:
            parsed = ResumeSchema.model_validate(payload)
        except ValidationError as exc:
            raise ValueError(f"结构化简历 JSON 校验失败：{exc}") from exc
        if self._is_effectively_empty(parsed):
            return self._heuristic_structure(raw_text)
        return parsed

    @staticmethod
    def _heuristic_structure(raw_text: str) -> ResumeSchema:
        lines = [line.strip("- ").strip() for line in raw_text.splitlines() if line.strip()]
        name = lines[0] if lines else "候选人"
        title = lines[1] if len(lines) > 1 else ""
        bullets = lines[2:8] if len(lines) > 2 else lines[1:6]
        summary = title if title and len(title) <= 30 else ""
        if not bullets:
            bullets = ["这是根据原始简历文本提取的示例内容。"]
        payload = {
            "basics": {
                "name": name,
                "phone": "",
                "email": "",
                "location": "",
                "links": [],
            },
            "summary": summary,
            "experience": [
                {
                    "block_id": "exp_1",
                    "company": "",
                    "title": title,
                    "start_date": "",
                    "end_date": "",
                    "bullets": bullets,
                }
            ],
            "education": [],
            "projects": [],
            "skills": [
                {"category": "原始提取", "items": [line for line in lines[2:6] if line][:4]},
            ],
        }
        return ResumeSchema.model_validate(payload)

    @staticmethod
    def _is_effectively_empty(resume: ResumeSchema) -> bool:
        return not any(
            [
                resume.basics.name.strip(),
                resume.summary.strip(),
                resume.experience,
                resume.education,
                resume.projects,
                resume.skills,
            ]
        )
