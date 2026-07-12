"""Section-oriented drafting skill with bounded incremental generation."""

from __future__ import annotations

import json

from ..contracts import Skill, TextGenerator
from ..models import SkillRequest, SkillResult
from ..prompts import WRITING_PROMPT


class WritingSkill(Skill):
    name = "writing"

    def __init__(self, generator: TextGenerator | None = None) -> None:
        self.generator = generator

    def execute(self, request: SkillRequest) -> SkillResult:
        outline_text = request.inputs["outline"]
        evidence_text = request.inputs["research"]
        requirements_text = request.inputs["requirements_analysis"]
        issue_tree_text = request.inputs["issue_tree"]
        evidence_ledger_text = request.inputs["evidence_governance"]
        materials_text = request.inputs["material_integration"]
        visualizations_text = request.inputs["visualization"]
        prompt = WRITING_PROMPT.format(
            topic=request.config.topic,
            expected_length=request.config.expected_length,
        )
        if self.generator:
            prompt += (
                f"\n已确认大纲：\n{outline_text}\n议题树：\n{issue_tree_text}"
                f"\n证据包：\n{evidence_text}\n证据账本：\n{evidence_ledger_text}"
                f"\n需求简报：\n{requirements_text}\n章节素材：\n{materials_text}"
                f"\n可视化资产：\n{visualizations_text}"
            )
            content = self.generator.generate(
                system="你是证据驱动的研究报告作者。", prompt=prompt,
                max_tokens=max(2000, request.config.expected_length * 2),
            )
            return SkillResult(content, "draft", {"prompt_version": "1.0"})

        outline = json.loads(outline_text)
        materials = json.loads(materials_text)
        visualizations = json.loads(visualizations_text)
        parts = [f"# {outline['title']}\n"]
        for section_index, section in enumerate(outline["sections"]):
            target = max(100, int(section["target_length"]))
            section_materials = materials.get("sections", {}).get(
                section["id"], {}
            ).get("materials", [])
            citations = [
                f"[{item['source_id']}]({item['original_url']})"
                for item in section_materials if item.get("original_url")
            ]
            citation = (
                "（来源：" + "、".join(citations) + "）"
                if citations else "（资料缺口：待检索）"
            )
            evidence_summary = "；".join(
                f"{item.get('title')}：{item.get('content', '')[:120]}"
                for item in section_materials[:3]
            )
            lead = (
                f"本节围绕“{section['title']}”分析{request.config.topic}。"
                f"论述遵循事实、分析与建议分离原则。{citation}"
            )
            if evidence_summary:
                lead += f" 已收集素材显示：{evidence_summary}。"
            sentences = [lead]
            counter = 1
            while len("".join(sentences)) < target:
                sentences.append(
                    f"第{counter}项分析从适用范围、证据强度、实施条件和潜在偏差四个方面"
                    f"检视该议题；现有材料不足以支持的判断不作为确定事实。"
                )
                counter += 1
            section_body = "".join(sentences)
            parts.append(f"## {section['title']}\n\n{section_body}\n")
            applicable = [
                asset for asset in visualizations.get("assets", [])
                if section["id"] in asset.get("section_ids", [])
                or (not asset.get("section_ids") and section_index == 0)
            ]
            for asset in applicable:
                if asset["format"] == "mermaid":
                    rendered = f"```mermaid\n{asset['content']}\n```"
                else:
                    rendered = (
                        "```json\n"
                        + json.dumps(asset["content"], ensure_ascii=False, indent=2)
                        + "\n```"
                    )
                parts.append(f"### {asset['title']}\n\n{rendered}\n")
        if request.feedback:
            parts.append("## 修订说明\n\n" + "；".join(request.feedback))
        content = "\n".join(parts)
        return SkillResult(
            content, "draft",
            {"character_count": len(content), "section_count": len(outline["sections"])},
        )
