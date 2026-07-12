"""Quality review and conservative polishing skill."""

from __future__ import annotations

import json
import re

from ..contracts import Skill, TextGenerator
from ..models import SkillRequest, SkillResult
from ..prompts import REVIEW_PROMPT


class ReviewSkill(Skill):
    name = "review"

    def __init__(self, generator: TextGenerator | None = None) -> None:
        self.generator = generator

    def execute(self, request: SkillRequest) -> SkillResult:
        formatted = request.inputs["formatting"]
        evidence = json.loads(request.inputs["research"])
        if self.generator:
            content = self.generator.generate(
                system="你是独立质量审核员，不得引入未经证实的新事实。",
                prompt=f"{REVIEW_PROMPT}\n待审报告：\n{formatted}",
                max_tokens=max(2000, request.config.expected_length * 2),
            )
            return SkillResult(content, "final_report", {"prompt_version": "1.0"})

        issues: list[str] = []
        if not evidence.get("sources"):
            issues.append("没有可核验来源，报告中的资料缺口标记不得删除")
        if request.config.output_format == "markdown" and not re.search(r"^# ", formatted):
            issues.append("缺少一级标题")
        if len(formatted) < request.config.expected_length * 0.75:
            issues.append("正文长度低于目标篇幅的 75%")
        content = formatted
        if request.feedback:
            note = "；".join(request.feedback)
            if request.config.output_format == "html":
                content = content.replace("</body>", f"<aside>审核修订：{note}</aside></body>")
            elif request.config.output_format == "json":
                payload = json.loads(content)
                payload["review_feedback"] = list(request.feedback)
                content = json.dumps(payload, ensure_ascii=False, indent=2)
            else:
                content += f"\n\n审核修订：{note}\n"
        return SkillResult(
            content,
            "final_report",
            {
                "quality_passed": not issues,
                "issues": issues,
                "checks": {
                    "non_empty": bool(content.strip()),
                    "format": request.config.output_format,
                    "source_count": len(evidence.get("sources", [])),
                },
            },
        )
