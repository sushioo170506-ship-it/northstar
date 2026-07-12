"""Evidence-aware report outline skill."""

from __future__ import annotations

import hashlib
import json

from ..contracts import Skill, TextGenerator
from ..models import SkillRequest, SkillResult
from ..prompts import OUTLINE_PROMPT


class OutlineSkill(Skill):
    name = "outline"

    def __init__(self, generator: TextGenerator | None = None) -> None:
        self.generator = generator

    def execute(self, request: SkillRequest) -> SkillResult:
        evidence = request.inputs["research"]
        prompt = OUTLINE_PROMPT.format(
            topic=request.config.topic,
            expected_length=request.config.expected_length,
            style=request.config.style,
        )
        if self.generator:
            prompt += f"\n证据包：\n{evidence}"
            content = self.generator.generate(
                system="你是研究报告架构师。", prompt=prompt, max_tokens=3000
            )
            return SkillResult(content, "outline", {"prompt_version": "1.0"})

        titles = ["摘要", "研究背景与范围", "现状与关键发现", "机制分析", "风险与局限", "结论与建议"]
        weights = [0.08, 0.15, 0.24, 0.24, 0.13, 0.16]
        sections = [
            {
                "id": f"SEC-{index + 1:02d}",
                "title": title,
                "target_length": round(request.config.expected_length * weights[index]),
                "purpose": f"围绕“{request.config.topic}”阐明{title}",
                "evidence_requirements": ["evidence_pack"],
            }
            for index, title in enumerate(titles)
        ]
        payload = {
            "title": request.config.topic,
            "sections": sections,
            "total_target_length": sum(item["target_length"] for item in sections),
            "feedback_applied": list(request.feedback),
            "evidence_checksum_hint": hashlib.sha256(evidence.encode("utf-8")).hexdigest(),
        }
        return SkillResult(json.dumps(payload, ensure_ascii=False, indent=2), "outline")
