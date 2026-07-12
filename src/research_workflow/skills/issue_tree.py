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
        requirements_text = request.inputs["requirements_analysis"]
        if self.generator:
            prompt = (
                f"围绕“{request.config.topic}”生成 3-7 个一级问题，并对可细分问题继续拆成"
                "二级问题。逐项说明必要性、写作价值和是否保留，剔除无关维度。输出 JSON。"
                f"\n需求简报：{requirements_text}"
            )
            content = self.generator.generate(
                system="你是战略分析议题树架构师。", prompt=prompt, max_tokens=2400
            )
            return SkillResult(content, "issue_tree", {"prompt_version": "1.0"})

        requirements = json.loads(requirements_text)
        dimensions = (
            ("概念、范围与评价标准", ("核心概念如何界定？", "评价目标达成应采用什么标准？")),
            ("现状、规模与变化", ("当前处于什么状态？", "近期出现了哪些重要变化？")),
            ("驱动机制与关键证据", ("哪些因素驱动现状？", "证据如何支持或反驳这些机制？")),
            ("方案比较与适用条件", ("主要方案有哪些？", "各方案在什么条件下适用？")),
            ("风险、边界与行动建议", ("结论在哪些条件下失效？", "目标受众应采取什么行动？")),
        )
        issues = []
        for index, (dimension, children) in enumerate(dimensions):
            issues.append(
                {
                    "id": f"ISSUE-{index + 1:02d}",
                    "question": f"{request.config.topic}的{dimension}是什么？",
                    "hypothesis": "待证据验证",
                    "evidence_required": ["至少一个可追溯来源"],
                    "necessity": "直接支撑研究目标和最终论证",
                    "value": f"帮助{requirements['audience']}理解{dimension}",
                    "included": True,
                    "children": [
                        {
                            "id": f"ISSUE-{index + 1:02d}-{child_index + 1:02d}",
                            "question": question,
                            "necessity": "用于回答上级问题",
                            "included": True,
                        }
                        for child_index, question in enumerate(children)
                    ],
                    "status": "open",
                }
            )
        payload = {
            "main_question": request.config.topic,
            "confirmed_topic_candidate": request.config.topic,
            "issues": issues,
            "coverage": {
                "issue_count": len(issues),
                "mece_review": "需在人工确认节点复核",
                "all_included_issues_have_value": all(item["included"] for item in issues),
            },
            "excluded_issues": [],
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
        included = [item for item in payload.get("issues", []) if item.get("included", True)]
        count = len(included)
        if not 3 <= count <= 7:
            raise ValueError("issue_tree 必须包含 3-7 个子问题")
        if any(not item.get("necessity") or not item.get("value") for item in included):
            raise ValueError("每个保留的一级问题必须说明必要性和价值")
