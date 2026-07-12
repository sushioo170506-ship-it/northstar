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
        issue_tree_text = request.inputs["issue_tree"]
        evidence_ledger_text = request.inputs["evidence_governance"]
        prompt = WRITING_PROMPT.format(
            topic=request.config.topic,
            expected_length=request.config.expected_length,
        )
        if self.generator:
            prompt += (
                f"\n已确认大纲：\n{outline_text}\n议题树：\n{issue_tree_text}"
                f"\n证据包：\n{evidence_text}\n证据账本：\n{evidence_ledger_text}"
            )
            content = self.generator.generate(
                system="你是证据驱动的研究报告作者。", prompt=prompt,
                max_tokens=max(2000, request.config.expected_length * 2),
            )
            return SkillResult(content, "draft", {"prompt_version": "1.0"})

        outline = json.loads(outline_text)
        evidence = json.loads(evidence_text)
        evidence_ledger = json.loads(evidence_ledger_text)
        governed_ids = {
            source["id"] for source in evidence_ledger.get("sources", [])
            if source.get("traceable")
        }
        source_ids = [
            source["id"] for source in evidence.get("sources", [])
            if source["id"] in governed_ids
        ]
        citation = f"（资料：{source_ids[0]}）" if source_ids else "（资料缺口：待检索）"
        parts = [f"# {outline['title']}\n"]
        for section in outline["sections"]:
            target = max(100, int(section["target_length"]))
            lead = (
                f"本节围绕“{section['title']}”分析{request.config.topic}。"
                f"论述遵循事实、分析与建议分离原则。{citation}"
            )
            sentences = [lead]
            counter = 1
            while len("".join(sentences)) < target:
                sentences.append(
                    f"第{counter}项分析从适用范围、证据强度、实施条件和潜在偏差四个方面"
                    f"检视该议题；现有材料不足以支持的判断不作为确定事实。"
                )
                counter += 1
            section_body = "".join(sentences)[:target]
            parts.append(f"## {section['title']}\n\n{section_body}\n")
        if request.feedback:
            parts.append("## 修订说明\n\n" + "；".join(request.feedback))
        content = "\n".join(parts)
        return SkillResult(
            content, "draft",
            {"character_count": len(content), "section_count": len(outline["sections"])},
        )
