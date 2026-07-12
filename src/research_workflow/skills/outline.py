"""Evidence-aware report outline skill."""

from __future__ import annotations

import json

from ..contracts import Skill, TextGenerator
from ..models import SkillRequest, SkillResult
from ..prompts import OUTLINE_PROMPT


class OutlineSkill(Skill):
    name = "outline"

    def __init__(self, generator: TextGenerator | None = None) -> None:
        self.generator = generator

    def execute(self, request: SkillRequest) -> SkillResult:
        requirements_text = request.inputs["requirements_analysis"]
        issue_tree_text = request.inputs["issue_tree"]
        prompt = OUTLINE_PROMPT.format(
            topic=request.config.topic,
            expected_length=request.config.expected_length,
            style=request.config.style,
        )
        if self.generator:
            prompt += (
                f"\n需求简报：\n{requirements_text}\n议题树：\n{issue_tree_text}"
            )
            content = self.generator.generate(
                system="你是研究报告架构师。", prompt=prompt, max_tokens=3000
            )
            return SkillResult(content, "outline", {"prompt_version": "1.0"})

        issue_tree = json.loads(issue_tree_text)
        requirements = json.loads(requirements_text)
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
                "chapter_claim": f"待数据验证：{title}存在可被量化或案例证伪的核心判断",
                "reader_challenge": f"这一节凭什么支持关于“{title}”的结论？",
                "anchor_requirements": [
                    {"type": "data", "need": "数值+时间+来源+口径"},
                    {"type": "comparison", "need": "至少两个同口径对象或时间点"},
                ],
                "entry_summary_budget": 100,
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
            "requirements_alignment": {
                "audience": requirements["audience"],
                "style": requirements["style"],
                "output_type": requirements["deliverable"]["type"],
                "boundaries": requirements["content_boundaries"],
            },
            "narrative_gates": {
                "opening": {
                    "type": "cognitive_conflict",
                    "budget": 25,
                    "require_numeric_anchor": True,
                },
                "section_entries": "每节首段必须给章节判断和最强锚点",
                "closing": "回扣核心判断并给出证伪边界，不使用空泛展望",
            },
            "rhythm": {
                "front_30_percent": "核心判断与最强证据",
                "middle_40_percent": "评分、对比、冲突与假说检验",
                "back_30_percent": "行动含义、边界与闭环",
            },
            "competitive_hypotheses": issue_tree.get("competitive_hypotheses", []),
        }
        return SkillResult(json.dumps(payload, ensure_ascii=False, indent=2), "outline")

    def validate(self, result: SkillResult) -> None:
        super().validate(result)
        payload = json.loads(result.content)
        sections = payload.get("sections", [])
        if not sections:
            raise ValueError("outline 必须包含章节")
        for section in sections:
            if not section.get("chapter_claim") or not section.get(
                "anchor_requirements"
            ):
                raise ValueError("每个章节必须包含判断和数据锚点需求")
        if not payload.get("narrative_gates") or not payload.get(
            "competitive_hypotheses"
        ):
            raise ValueError("outline 必须包含传播门和竞争性假说")
