"""MECE-style issue tree construction for evidence-answerable research."""

from __future__ import annotations

import json

from ..contracts import Skill, TextGenerator
from ..models import SkillRequest, SkillResult


class IssueTreeSkill(Skill):
    name = "issue_tree"

    def __init__(self, generator: TextGenerator | None = None) -> None:
        self.generator = generator

    def execute(self, request: SkillRequest) -> SkillResult:
        evidence_pack = request.inputs["research"]
        if self.generator:
            prompt = (
                f"围绕“{request.config.topic}”生成 3-7 个互不重叠、合计覆盖主问题、"
                f"且可由证据回答的子问题。输出 JSON。\n研究输入：{evidence_pack}"
            )
            content = self.generator.generate(
                system="你是战略分析议题树架构师。", prompt=prompt, max_tokens=2400
            )
            return SkillResult(content, "issue_tree", {"prompt_version": "1.0"})

        research = json.loads(evidence_pack)
        questions = research.get("research_questions", [])
        issues = []
        for index, item in enumerate(questions[:7]):
            question = item.get("question", "") if isinstance(item, dict) else str(item)
            issues.append(
                {
                    "id": f"ISSUE-{index + 1:02d}",
                    "question": question,
                    "hypothesis": "待证据验证",
                    "evidence_required": ["至少一个可追溯来源"],
                    "status": "open",
                }
            )
        while len(issues) < 3:
            index = len(issues)
            issues.append(
                {
                    "id": f"ISSUE-{index + 1:02d}",
                    "question": f"{request.config.topic}的关键维度 {index + 1} 是什么？",
                    "hypothesis": "待证据验证",
                    "evidence_required": ["至少一个可追溯来源"],
                    "status": "open",
                }
            )
        payload = {
            "main_question": request.config.topic,
            "issues": issues,
            "coverage": {
                "issue_count": len(issues),
                "mece_review": "需在人工确认节点复核",
            },
            "feedback_applied": list(request.feedback),
        }
        return SkillResult(
            json.dumps(payload, ensure_ascii=False, indent=2),
            "issue_tree",
            {"issue_count": len(issues), "requires_confirmation": True},
        )

    def validate(self, result: SkillResult) -> None:
        super().validate(result)
        payload = json.loads(result.content)
        count = len(payload.get("issues", []))
        if not 3 <= count <= 7:
            raise ValueError("issue_tree 必须包含 3-7 个子问题")
