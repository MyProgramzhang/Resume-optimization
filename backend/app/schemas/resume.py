from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class LinkItem(BaseModel):
    label: str = ""
    url: str = ""


class Basics(BaseModel):
    name: str = ""
    phone: str = ""
    email: str = ""
    location: str = ""
    links: list[LinkItem] = Field(default_factory=list)


class ExperienceItem(BaseModel):
    block_id: str
    company: str = ""
    title: str = ""
    start_date: str = ""
    end_date: str = ""
    bullets: list[str] = Field(default_factory=list)


class EducationItem(BaseModel):
    block_id: str
    school: str = ""
    degree: str = ""
    major: str = ""
    start_date: str = ""
    end_date: str = ""


class ProjectItem(BaseModel):
    block_id: str
    name: str = ""
    role: str = ""
    start_date: str = ""
    end_date: str = ""
    bullets: list[str] = Field(default_factory=list)


class SkillGroup(BaseModel):
    category: str = ""
    items: list[str] = Field(default_factory=list)


class ResumeSchema(BaseModel):
    basics: Basics = Field(default_factory=Basics)
    summary: str = ""
    experience: list[ExperienceItem] = Field(default_factory=list)
    education: list[EducationItem] = Field(default_factory=list)
    projects: list[ProjectItem] = Field(default_factory=list)
    skills: list[SkillGroup] = Field(default_factory=list)

    @field_validator("skills", mode="before")
    @classmethod
    def normalize_skills(cls, value: object) -> list[object]:
        if value is None:
            return []
        if not isinstance(value, list):
            return value

        normalized: list[object] = []
        for item in value:
            if isinstance(item, dict):
                normalized.append(item)
                continue
            if isinstance(item, str):
                normalized.append(cls._skill_string_to_group(item))
                continue
            normalized.append(item)
        return normalized

    @staticmethod
    def _skill_string_to_group(raw_text: str) -> dict[str, object]:
        text = raw_text.strip()
        if not text:
            return {"category": "", "items": []}

        if "：" in text:
            category, items_text = text.split("：", 1)
        elif ":" in text:
            category, items_text = text.split(":", 1)
        elif "|" in text:
            parts = [part.strip() for part in text.split("|") if part.strip()]
            category = parts[0] if parts else ""
            items_text = "|".join(parts[1:]) if len(parts) > 1 else ""
        else:
            category = "技能"
            items_text = text

        items = [
            part.strip()
            for part in items_text.replace("｜", "|").replace("、", ",").split("|")
            for part in part.split(",")
            if part.strip()
        ]
        return {"category": category.strip(), "items": items}


SectionName = Literal["summary", "experience", "education", "projects", "skills"]
