"""Map governed evidence to confirmed outline sections."""

from __future__ import annotations

import json

from ..contracts import Skill, TextGenerator
from ..models import SkillRequest, SkillResult


class MaterialIntegrationSkill(Skill):
    name = "material_integration"

    def __init__(self, generator: TextGenerator | None = None) -> None:
        self.generator = generator

    def execute(self, request: SkillRequest) -> SkillResult:
        outline_text = request.inputs["outline"]
        research_text = request.inputs["research"]
        ledger_text = request.inputs["evidence_governance"]
        if self.generator:
            content = self.generator.generate(
                system="你是研究素材编辑，所有材料必须挂载到确定章节且保留原始链接。",
                prompt=(
                    f"大纲：{outline_text}\n调研材料：{research_text}\n"
                    f"证据账本：{ledger_text}\n输出严格 JSON 章节素材包。"
                ),
                max_tokens=5000,
            )
            return SkillResult(content, "section_materials", {"prompt_version": "1.0"})

        outline = json.loads(outline_text)
        research = json.loads(research_text)
        ledger = json.loads(ledger_text)
        governed = {source["id"]: source for source in ledger.get("sources", [])}
        sections = {
            section["id"]: {
                "title": section["title"],
                "linked_issue": section.get("linked_issue"),
                "materials": [],
            }
            for section in outline.get("sections", [])
        }
        fallback = next(
            (section_id for section_id, section in sections.items() if section["linked_issue"]),
            next(iter(sections), None),
        )
        mounted = 0
        for source in research.get("sources", []):
            governed_source = governed.get(source.get("id"), {})
            issue_ids = set(governed_source.get("issue_ids", []))
            targets = [
                section_id for section_id, section in sections.items()
                if section["linked_issue"] in issue_ids
            ]
            if not targets and fallback:
                targets = [fallback]
            material = {
                "source_id": source.get("id"),
                "title": source.get("title"),
                "category": source.get("category", "unknown"),
                "original_url": source.get("url"),
                "content": source.get("content", ""),
                "usage": "作为本章节事实、数据或背景依据",
            }
            for target in targets:
                sections[target]["materials"].append(material)
            if targets:
                mounted += 1
        total = len(research.get("sources", []))
        payload = {
            "sections": sections,
            "metrics": {
                "material_count": total,
                "mounted_material_count": mounted,
                "mount_coverage": mounted / total if total else 0.0,
            },
            "feedback_applied": list(request.feedback),
        }
        return SkillResult(
            json.dumps(payload, ensure_ascii=False, indent=2),
            "section_materials",
            payload["metrics"],
        )

    def validate(self, result: SkillResult) -> None:
        super().validate(result)
        payload = json.loads(result.content)
        if not {"sections", "metrics"} <= payload.keys():
            raise ValueError("section_materials 缺少章节或覆盖指标")
