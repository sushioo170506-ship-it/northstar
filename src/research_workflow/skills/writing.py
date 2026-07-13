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
        processed_text = request.inputs["data_processing"]
        materials_text = request.inputs["material_integration"]
        visualizations_text = request.inputs["visualization"]
        standard_text = request.inputs["writing_standards"]
        verification_text = request.inputs.get("claim_verification", "{}")
        prompt = WRITING_PROMPT.format(
            topic=request.config.topic,
            expected_length=request.config.expected_length,
        )
        if self.generator:
            prompt += (
                f"\n已确认大纲：\n{outline_text}\n议题树：\n{issue_tree_text}"
                f"\n证据包：\n{evidence_text}\n证据账本：\n{evidence_ledger_text}"
                f"\n数据处理与评分：\n{processed_text}"
                f"\n需求简报：\n{requirements_text}\n章节素材：\n{materials_text}"
                f"\n可视化资产：\n{visualizations_text}"
                f"\n强制写作规范：\n{standard_text}"
                f"\n论断验证：\n{verification_text}"
            )
            content = self.generator.generate(
                system="你是证据驱动的研究报告作者。", prompt=prompt,
                max_tokens=max(2000, request.config.expected_length * 2),
            )
            return SkillResult(content, "draft", {"prompt_version": "1.0"})

        outline = json.loads(outline_text)
        materials = json.loads(materials_text)
        visualizations = json.loads(visualizations_text)
        processed = json.loads(processed_text)
        standard = json.loads(standard_text)
        verification = json.loads(verification_text)
        scene = standard["scene"]
        parts = [f"# {outline['title']}\n"]
        if request.config.confidentiality_level != "public":
            parts.append(
                f"> 阅读范围：{request.config.confidentiality_level}；"
                "按组织信息安全制度处理。\n"
            )
        for section_index, section in enumerate(outline["sections"]):
            target = max(60, int(section["target_length"]))
            section_materials = materials.get("sections", {}).get(
                section["id"], {}
            ).get("materials", [])
            if not section.get("linked_issue"):
                # Framing/format sections follow the selected profile but must not
                # duplicate every source mounted for substantive issue sections.
                section_materials = []
            citations = [
                f"[{item['source_id']}]({item['original_url']})"
                for item in section_materials if item.get("original_url")
            ]
            citation = (
                "（来源：" + "、".join(citations) + "）"
                if citations else "（资料缺口：待检索）"
            )
            evidence_summary = "；".join(
                f"{item.get('title')}[{','.join(item.get('evidence_grades', [])) or '未分级'}]："
                f"{item.get('content', '')[:120]}"
                for item in section_materials[:3]
            )
            lead = (
                f"本节围绕“{section['title']}”分析{request.config.topic}。"
                f"论述遵循事实、分析与建议分离原则。{citation}"
            )
            if evidence_summary:
                lead += f" 已收集素材显示：{evidence_summary}。"
            evidence_blocks = []
            for item in section_materials:
                source_content = str(item.get("content") or "").strip()
                if source_content:
                    evidence_blocks.append(
                        f"据{item.get('title', item.get('source_id'))}："
                        f"{source_content}"
                    )
            if evidence_blocks:
                available = "\n\n".join(evidence_blocks)
                remaining = max(0, target - len(lead))
                section_body = lead + "\n\n" + available[:remaining]
            else:
                section_body = lead + (
                    "\n\n本节没有足够的已验证证据，禁止以模板化文字补足篇幅；"
                    "应退回调研与论断验证节点。"
                )
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
        if scene == "technical":
            parts.append(
                "## 符号、术语与复现说明\n\n"
                "公式采用 LaTeX 块格式；术语首现定义。实验参数、数据口径和"
                "不确定性应随可复现附件补齐。\n"
            )
        elif scene == "public_account":
            parts.append(
                "## 互动\n\n"
                "你最希望进一步核验哪一项数据或应用边界？欢迎基于原始来源讨论。\n"
            )
        if request.feedback:
            parts.append("## 修订说明\n\n" + "；".join(request.feedback))
        content = "\n".join(parts)
        return SkillResult(
            content, "draft",
            {
                "character_count": len(content),
                "section_count": len(outline["sections"]),
                "claim_count": len(
                    verification.get("claims", processed.get("claims", []))
                ),
                "verified_claim_count": verification.get("metrics", {}).get(
                    "verified_claim_count"
                ),
                "scoring_status": processed.get("scoring", {}).get("status"),
                "writing_standard_profile": standard["profile"]["id"],
                "writing_scene": scene,
            },
        )
