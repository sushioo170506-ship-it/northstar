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
        issue_tree_text = request.inputs["issue_tree"]
        evidence_ledger = request.inputs["evidence_governance"]
        prompt = OUTLINE_PROMPT.format(
            topic=request.config.topic,
            expected_length=request.config.expected_length,
            style=request.config.style,
        )
        if self.generator:
            prompt += (
                f"\n证据包：\n{evidence}\n议题树：\n{issue_tree_text}"
                f"\n证据治理账本：\n{evidence_ledger}"
            )
            content = self.generator.generate(
                system="你是研究报告架构师。", prompt=prompt, max_tokens=3000
            )
            return SkillResult(content, "outline", {"prompt_version": "1.0"})

        issue_tree = json.loads(issue_tree_text)
        issue_titles = [
            item.get("question", item.get("id", "关键议题"))
            for item in issue_tree.get("issues", [])
        ]
        titles = ["摘要", *issue_titles, "风险与局限", "结论与建议"]
        weights = [1 / len(titles)] * len(titles)
        sections = [
            {
                "id": f"SEC-{index + 1:02d}",
                "title": title,
                "target_length": round(request.config.expected_length * weights[index]),
                "purpose": f"围绕“{request.config.topic}”阐明{title}",
                "evidence_requirements": ["evidence_pack"],
                "linked_issue": (
                    issue_tree["issues"][index - 1]["id"]
                    if 0 < index <= len(issue_tree.get("issues", [])) else None
                ),
            }
            for index, title in enumerate(titles)
        ]
        payload = {
            "title": request.config.topic,
            "sections": sections,
            "total_target_length": sum(item["target_length"] for item in sections),
            "feedback_applied": list(request.feedback),
            "evidence_checksum_hint": hashlib.sha256(evidence.encode("utf-8")).hexdigest(),
            "evidence_ledger_checksum_hint": hashlib.sha256(
                evidence_ledger.encode("utf-8")
            ).hexdigest(),
        }
        return SkillResult(json.dumps(payload, ensure_ascii=False, indent=2), "outline")
