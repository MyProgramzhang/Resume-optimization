from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import fitz

from app.schemas.result import DiffBlock


@dataclass
class MatchedLine:
    page_index: int
    rect: fitz.Rect
    text: str
    font_size: float


class TemplateResumePdfExporter:
    def __init__(self) -> None:
        self.font_path = self._resolve_font_path()
        self.font_alias = "resume-cjk"

    def export(
        self,
        output_path: Path,
        original_pdf_path: Path,
        diff_blocks: list[DiffBlock],
    ) -> tuple[Path, int]:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        document = fitz.open(original_pdf_path)
        applied_blocks = 0
        try:
            for page in document:
                self._ensure_font(page)

            candidates = self._collect_candidates(document)
            for block in diff_blocks:
                if self._apply_block(document, block, candidates):
                    applied_blocks += 1

            document.save(output_path, garbage=4, deflate=True)
        finally:
            document.close()
        return output_path, applied_blocks

    def _apply_block(
        self,
        document: fitz.Document,
        block: DiffBlock,
        candidates: dict[tuple[int, int], MatchedLine],
    ) -> bool:
        old_lines = self._meaningful_lines(block.old_text)
        new_lines = self._meaningful_lines(block.new_text)
        if not old_lines or old_lines == new_lines:
            return False

        matched_lines = self._match_lines(candidates, old_lines)
        if not matched_lines:
            return False

        matched_lines.sort(key=lambda item: (item.page_index, item.rect.y0, item.rect.x0))
        first_page_index = matched_lines[0].page_index
        if any(item.page_index != first_page_index for item in matched_lines):
            return False

        page = document[first_page_index]
        target_rect = self._union_rect(item.rect for item in matched_lines)
        fontsize = max(8.0, min(item.font_size for item in matched_lines) if matched_lines else 10.5)
        expanded_rect = fitz.Rect(
            target_rect.x0 - 1,
            target_rect.y0 - 1,
            target_rect.x1 + 1,
            target_rect.y1 + max(6, (len(new_lines) - len(old_lines)) * fontsize * 1.2 + 2),
        )

        page.add_redact_annot(expanded_rect, fill=(1, 1, 1))
        page.apply_redactions()

        text = "\n".join(new_lines)
        inserted = self._insert_text(page, expanded_rect, text, fontsize)
        return inserted

    def _insert_text(self, page: fitz.Page, rect: fitz.Rect, text: str, fontsize: float) -> bool:
        if not text.strip():
            return True

        font_name = self.font_alias if self.font_path else "helv"
        for size in [fontsize, fontsize - 0.5, fontsize - 1.0, fontsize - 1.5, fontsize - 2.0]:
            if size < 7.0:
                continue
            inserted = page.insert_textbox(
                rect,
                text,
                fontsize=size,
                fontname=font_name,
                color=(0, 0, 0),
                align=fitz.TEXT_ALIGN_LEFT,
                lineheight=1.15,
            )
            if inserted >= 0:
                return True
        return False

    def _match_lines(self, candidates: dict[tuple[int, int], MatchedLine], old_lines: list[str]) -> list[MatchedLine]:
        matches: list[MatchedLine] = []
        used: set[tuple[int, int]] = set()

        for old_line in old_lines:
            normalized_old = self._normalize_text(old_line)
            best_score = 0.0
            best_key: tuple[int, int] | None = None
            best_candidate: MatchedLine | None = None
            for key, candidate in candidates.items():
                if key in used:
                    continue
                score = self._similarity(normalized_old, self._normalize_text(candidate.text))
                if score > best_score:
                    best_score = score
                    best_key = key
                    best_candidate = candidate

            if best_candidate and best_key and best_score >= 0.55:
                used.add(best_key)
                matches.append(best_candidate)
        return matches

    def _collect_candidates(self, document: fitz.Document) -> dict[tuple[int, int], MatchedLine]:
        candidates: dict[tuple[int, int], MatchedLine] = {}
        counter = 0
        for page in document:
            words = page.get_text("words", sort=True)
            lines: dict[tuple[int, int], list[tuple[float, float, float, float, str]]] = {}
            for x0, y0, x1, y1, text, block_no, line_no, _word_no in words:
                lines.setdefault((block_no, line_no), []).append((x0, y0, x1, y1, str(text)))

            for items in lines.values():
                items.sort(key=lambda item: (item[1], item[0]))
                line_text = " ".join(item[4] for item in items).strip()
                if not line_text:
                    continue
                rect = fitz.Rect(
                    min(item[0] for item in items),
                    min(item[1] for item in items),
                    max(item[2] for item in items),
                    max(item[3] for item in items),
                )
                font_size = max(8.5, rect.height * 0.8)
                candidates[(page.number, counter)] = MatchedLine(
                    page_index=page.number,
                    rect=rect,
                    text=line_text,
                    font_size=font_size,
                )
                counter += 1
        return candidates

    @staticmethod
    def _meaningful_lines(text: str) -> list[str]:
        return [line.strip() for line in text.splitlines() if line.strip()]

    @staticmethod
    def _normalize_text(text: str) -> str:
        text = text.replace("•", "-").replace("·", "").replace("，", ",").replace("：", ":")
        text = re.sub(r"^\-\s*", "", text.strip())
        text = re.sub(r"\s+", "", text)
        return text.lower()

    @staticmethod
    def _similarity(a: str, b: str) -> float:
        if not a or not b:
            return 0.0
        if a == b:
            return 1.0
        if a in b or b in a:
            shorter = min(len(a), len(b))
            longer = max(len(a), len(b))
            return shorter / longer
        common = sum(1 for char in a if char in b)
        return common / max(len(a), len(b))

    @staticmethod
    def _union_rect(rects: Iterable[fitz.Rect]) -> fitz.Rect:
        rects = list(rects)
        current = fitz.Rect(rects[0])
        for rect in rects[1:]:
            current |= rect
        return current

    def _ensure_font(self, page: fitz.Page) -> None:
        if not self.font_path:
            return
        try:
            page.insert_font(fontname=self.font_alias, fontfile=self.font_path)
        except RuntimeError:
            pass

    @staticmethod
    def _resolve_font_path() -> str | None:
        candidates = [
            Path("C:/Windows/Fonts/msyh.ttc"),
            Path("C:/Windows/Fonts/msyh.ttf"),
            Path("C:/Windows/Fonts/simsun.ttc"),
            Path("C:/Windows/Fonts/simhei.ttf"),
        ]
        for candidate in candidates:
            if candidate.exists():
                return str(candidate)
        return None
