from __future__ import annotations

from app.schemas.result import DiffBlock
from app.schemas.resume import ResumeSchema


class DiffBuilder:
    def build(self, original: ResumeSchema, optimized: ResumeSchema) -> list[DiffBlock]:
        blocks: list[DiffBlock] = []

        if original.summary or optimized.summary:
            blocks.append(
                DiffBlock(
                    section="summary",
                    block_id="summary",
                    old_text=original.summary,
                    new_text=optimized.summary,
                    change_type="rewrite",
                    reason="优化了个人摘要的表达清晰度和定位准确性。",
                )
            )

        blocks.extend(self._compare_items("experience", original.experience, optimized.experience))
        blocks.extend(self._compare_items("education", original.education, optimized.education))
        blocks.extend(self._compare_items("projects", original.projects, optimized.projects))

        original_skills = "\n".join(
            f"{group.category}: {', '.join(group.items)}" for group in original.skills
        ).strip()
        optimized_skills = "\n".join(
            f"{group.category}: {', '.join(group.items)}" for group in optimized.skills
        ).strip()
        if original_skills or optimized_skills:
            blocks.append(
                DiffBlock(
                    section="skills",
                    block_id="skills",
                    old_text=original_skills,
                    new_text=optimized_skills,
                    change_type="reorder",
                    reason="重新整理了技能展示顺序，提升可读性和相关性。",
                )
            )
        return blocks

    def _compare_items(self, section: str, original_items: list, optimized_items: list) -> list[DiffBlock]:
        original_map = {item.block_id: item for item in original_items}
        optimized_map = {item.block_id: item for item in optimized_items}
        block_ids = list(dict.fromkeys([*original_map.keys(), *optimized_map.keys()]))
        result: list[DiffBlock] = []
        for block_id in block_ids:
            old_item = original_map.get(block_id)
            new_item = optimized_map.get(block_id)
            old_text = self._item_to_text(old_item)
            new_text = self._item_to_text(new_item)
            if not old_text and not new_text:
                continue
            result.append(
                DiffBlock(
                    section=section,
                    block_id=block_id,
                    old_text=old_text,
                    new_text=new_text,
                    change_type="rewrite",
                    reason="在保留原始事实的前提下优化了表述和结构顺序。",
                )
            )
        return result

    @staticmethod
    def _item_to_text(item: object | None) -> str:
        if item is None:
            return ""
        data = item.model_dump()
        lines: list[str] = []
        for key, value in data.items():
            if key == "block_id":
                continue
            if isinstance(value, list):
                if not value:
                    continue
                if value and isinstance(value[0], str):
                    lines.extend(f"- {entry}" for entry in value)
                else:
                    lines.append(str(value))
            elif value:
                lines.append(str(value))
        return "\n".join(lines).strip()
