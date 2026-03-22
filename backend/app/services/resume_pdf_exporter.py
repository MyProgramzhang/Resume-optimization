from __future__ import annotations

from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from app.schemas.resume import ResumeSchema


class ResumePdfExporter:
    def __init__(self) -> None:
        self._register_fonts()
        styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            "ResumeTitle",
            parent=styles["Title"],
            fontName="STSong-Light",
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#172033"),
            alignment=TA_CENTER,
            spaceAfter=8,
        )
        self.meta_style = ParagraphStyle(
            "ResumeMeta",
            parent=styles["BodyText"],
            fontName="STSong-Light",
            fontSize=10.5,
            leading=14,
            textColor=colors.HexColor("#4f5c75"),
            alignment=TA_CENTER,
            spaceAfter=14,
        )
        self.section_style = ParagraphStyle(
            "ResumeSection",
            parent=styles["Heading2"],
            fontName="STSong-Light",
            fontSize=13,
            leading=18,
            textColor=colors.HexColor("#172033"),
            spaceBefore=10,
            spaceAfter=6,
        )
        self.body_style = ParagraphStyle(
            "ResumeBody",
            parent=styles["BodyText"],
            fontName="STSong-Light",
            fontSize=10.5,
            leading=16,
            textColor=colors.black,
            spaceAfter=6,
        )
        self.item_title_style = ParagraphStyle(
            "ResumeItemTitle",
            parent=styles["BodyText"],
            fontName="STSong-Light",
            fontSize=11.5,
            leading=16,
            textColor=colors.HexColor("#172033"),
            spaceAfter=2,
        )
        self.muted_style = ParagraphStyle(
            "ResumeMuted",
            parent=styles["BodyText"],
            fontName="STSong-Light",
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#62708c"),
            spaceAfter=4,
        )
        self.bullet_style = ParagraphStyle(
            "ResumeBullet",
            parent=styles["BodyText"],
            fontName="STSong-Light",
            fontSize=10.5,
            leading=15,
            leftIndent=12,
            firstLineIndent=-12,
            spaceAfter=4,
        )

    def export(self, output_path: Path, resume: ResumeSchema) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            leftMargin=18 * mm,
            rightMargin=18 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm,
            title="优化后简历",
        )

        story = self._build_story(resume)
        doc.build(story)
        return output_path

    def _build_story(self, resume: ResumeSchema) -> list:
        story: list = []

        story.append(Paragraph(self._safe_text(resume.basics.name or "候选人"), self.title_style))

        meta_parts = [resume.basics.location, resume.basics.phone, resume.basics.email]
        if resume.basics.links:
            meta_parts.extend(link.url for link in resume.basics.links if link.url)
        meta_line = " ｜ ".join(part for part in meta_parts if part)
        if meta_line:
            story.append(Paragraph(self._safe_text(meta_line), self.meta_style))

        if resume.summary:
            story.extend(self._section("个人摘要", [Paragraph(self._safe_text(resume.summary), self.body_style)]))

        if resume.experience:
            items: list = []
            for item in resume.experience:
                title_line = " / ".join(part for part in [item.title, item.company] if part)
                if title_line:
                    items.append(Paragraph(self._safe_text(title_line), self.item_title_style))
                date_line = " - ".join(part for part in [item.start_date, item.end_date] if part)
                if date_line:
                    items.append(Paragraph(self._safe_text(date_line), self.muted_style))
                items.extend(self._bullet_paragraphs(item.bullets))
                items.append(Spacer(1, 4))
            story.extend(self._section("工作经历", items))

        if resume.education:
            items = []
            for item in resume.education:
                title_line = " / ".join(part for part in [item.school, item.degree, item.major] if part)
                if title_line:
                    items.append(Paragraph(self._safe_text(title_line), self.item_title_style))
                date_line = " - ".join(part for part in [item.start_date, item.end_date] if part)
                if date_line:
                    items.append(Paragraph(self._safe_text(date_line), self.muted_style))
                items.append(Spacer(1, 4))
            story.extend(self._section("教育经历", items))

        if resume.projects:
            items = []
            for item in resume.projects:
                title_line = " / ".join(part for part in [item.name, item.role] if part)
                if title_line:
                    items.append(Paragraph(self._safe_text(title_line), self.item_title_style))
                date_line = " - ".join(part for part in [item.start_date, item.end_date] if part)
                if date_line:
                    items.append(Paragraph(self._safe_text(date_line), self.muted_style))
                items.extend(self._bullet_paragraphs(item.bullets))
                items.append(Spacer(1, 4))
            story.extend(self._section("项目经历", items))

        if resume.skills:
            skill_lines = []
            for group in resume.skills:
                line = f"{group.category}：{', '.join(group.items)}" if group.category else ", ".join(group.items)
                if line.strip("：, "):
                    skill_lines.append(Paragraph(self._safe_text(line), self.body_style))
            story.extend(self._section("技能", skill_lines))

        return story

    def _section(self, title: str, content: list) -> list:
        section_story = [Paragraph(title, self.section_style)]
        section_story.extend(content)
        return section_story

    def _bullet_paragraphs(self, bullets: list[str]) -> list:
        return [Paragraph(self._safe_text(f"- {bullet}"), self.bullet_style) for bullet in bullets if bullet.strip()]

    @staticmethod
    def _safe_text(text: str) -> str:
        return escape(text).replace("\n", "<br/>")

    @staticmethod
    def _register_fonts() -> None:
        try:
            pdfmetrics.getFont("STSong-Light")
        except KeyError:
            pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
