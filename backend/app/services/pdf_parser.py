from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pdfplumber

from app.core.config import settings
from app.utils.text_cleaner import clean_resume_text


@dataclass
class ParseResult:
    text: str
    page_count: int
    warning: str | None = None


class PdfParser:
    def parse(self, pdf_path: Path) -> ParseResult:
        page_texts: list[str] = []
        with pdfplumber.open(pdf_path) as pdf:
            page_count = len(pdf.pages)
            if page_count > settings.max_pdf_pages:
                raise ValueError(f"PDF 页数不能超过 {settings.max_pdf_pages} 页。")
            for page in pdf.pages:
                page_texts.append(page.extract_text() or "")

        merged = clean_resume_text("\n\n".join(page_texts))
        if len(merged) < 80:
            raise ValueError("PDF 文本提取失败。V1 暂不支持扫描版 PDF。")

        warning = None
        if any(not text.strip() for text in page_texts):
            warning = "部分页面的文本提取效果较弱，请仔细检查结果。"

        return ParseResult(text=merged, page_count=page_count, warning=warning)
