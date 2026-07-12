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
        requirements = json.loads(request.inputs["requirements_analysis"])
        evidence = json.loads(request.inputs["research"])
        evidence_ledger = json.loads(request.inputs["evidence_governance"])
        material_integration = json.loads(request.inputs["material_integration"])
        visualizations = json.loads(request.inputs["visualization"])
        pressure_test = json.loads(request.inputs["pressure_test"])
        if self.generator:
            content = self.generator.generate(
                system="你是独立质量审核员，不得引入未经证实的新事实。",
                prompt=(
                    f"{REVIEW_PROMPT}\n待审报告：\n{formatted}"
                    f"\n证据账本：\n{request.inputs['evidence_governance']}"
                    f"\n需求简报：\n{request.inputs['requirements_analysis']}"
                    f"\n素材映射：\n{request.inputs['material_integration']}"
                    f"\n可视化：\n{request.inputs['visualization']}"
                    f"\n压力测试：\n{request.inputs['pressure_test']}"
                ),
                max_tokens=max(2000, request.config.expected_length * 2),
            )
            return SkillResult(content, "final_report", {"prompt_version": "1.0"})

        issues: list[str] = []
        if not evidence.get("sources"):
            issues.append("没有可核验来源，报告中的资料缺口标记不得删除")
        if evidence_ledger.get("red_lines"):
            issues.append("证据治理发现红线，必须由质量门阻断发布")
        issues.extend(pressure_test.get("repair_actions", []))
        categories = set(evidence_ledger.get("metrics", {}).get("source_categories", []))
        required_categories = {"industry", "academic", "social_media"}
        missing_categories = sorted(required_categories - categories)
        if missing_categories:
            issues.append("缺少必需来源类别：" + "、".join(missing_categories))
        missing_links = [
            source["id"] for source in evidence_ledger.get("sources", [])
            if not source.get("original_url") or source["original_url"] not in formatted
        ]
        if missing_links:
            issues.append("终稿缺少原始来源链接：" + "、".join(missing_links))
        if material_integration.get("metrics", {}).get("mount_coverage", 0.0) < 1.0:
            issues.append("存在未挂载到章节的素材")
        if not visualizations.get("assets"):
            issues.append("没有生成可视化成果")
        for boundary in requirements.get("content_boundaries", []):
            for prefix in ("不得包含:", "不得包含：", "禁止:", "禁止："):
                if boundary.startswith(prefix):
                    forbidden = boundary[len(prefix):].strip()
                    if forbidden and forbidden in formatted:
                        issues.append(f"违反内容边界：不得包含“{forbidden}”")
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
                "review_checks_passed": not issues,
                "issues": issues,
                "checks": {
                    "non_empty": bool(content.strip()),
                    "format": request.config.output_format,
                    "source_count": len(evidence.get("sources", [])),
                    "source_categories": sorted(categories),
                    "missing_source_links": missing_links,
                    "material_mount_coverage": material_integration.get(
                        "metrics", {}
                    ).get("mount_coverage", 0.0),
                    "visual_asset_count": len(visualizations.get("assets", [])),
                    "audience": requirements.get("audience"),
                    "style": requirements.get("style"),
                },
            },
        )
