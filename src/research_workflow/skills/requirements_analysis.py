"""Complete requirement extraction and intent normalization."""

from __future__ import annotations

import json

from ..contracts import Skill, TextGenerator
from ..models import SkillRequest, SkillResult


class RequirementsAnalysisSkill(Skill):
    name = "requirements_analysis"

    def __init__(self, generator: TextGenerator | None = None) -> None:
        self.generator = generator

    def execute(self, request: SkillRequest) -> SkillResult:
        from .capability_sweep import CapabilitySweepSkill

        sweep = CapabilitySweepSkill().execute(request)
        CapabilitySweepSkill().validate(sweep)
        sweep_payload = json.loads(sweep.content)

        config = request.config
        sources = config.extra.get("sources", [])
        if self.generator:
            prompt = (
                "完整提取需求，不得遗漏：产出形态、主题、文风、受众、篇幅、格式、"
                "内容边界、已有资料和用户前置思考。输出严格 JSON。\n"
                f"标准化配置：{json.dumps(config.to_dict(), ensure_ascii=False)}"
            )
            content = self.generator.generate(
                system="你是研究需求分析师。", prompt=prompt, max_tokens=2400
            )
            try:
                payload = json.loads(content)
            except json.JSONDecodeError:
                payload = {"raw": content, "parse_error": True}
            payload["capability_sweep"] = sweep_payload
            return SkillResult(
                json.dumps(payload, ensure_ascii=False, indent=2),
                "requirements_brief",
                {
                    "prompt_version": "1.0",
                    "pipeline_steps": ["capability_sweep", "requirements_analysis"],
                },
            )

        source_inventory = []
        for index, source in enumerate(sources):
            if isinstance(source, str):
                source_inventory.append(
                    {"id": f"S{index + 1}", "title": source, "category": "unknown"}
                )
            elif isinstance(source, dict):
                source_inventory.append(
                    {
                        "id": source.get("id", f"S{index + 1}"),
                        "title": source.get("title", f"资料 {index + 1}"),
                        "category": source.get("category", source.get("source_type", "unknown")),
                        "has_url": bool(source.get("url")),
                    }
                )
        missing = []
        if config.audience == "通用专业读者":
            missing.append("目标受众未提供，当前使用默认值")
        if not config.content_boundaries:
            missing.append("未声明额外内容边界")
        if not sources:
            missing.append("未提供参考资料，后续必须由检索适配器补齐")
        payload = {
            "intent": "generate_research_report",
            "deliverable": {
                "type": config.output_type,
                "format": config.output_format,
                "expected_length": config.expected_length,
                "language": config.language,
            },
            "topic": config.topic,
            "style": config.style,
            "audience": config.audience,
            "content_boundaries": list(config.content_boundaries),
            "reference_inventory": source_inventory,
            "prior_thoughts": config.prior_thoughts,
            "workflow_profile": config.workflow_profile,
            "confidentiality_level": config.confidentiality_level,
            "missing_or_defaulted": missing,
            "capability_sweep": sweep_payload,
            "feedback_applied": list(request.feedback),
        }
        return SkillResult(
            json.dumps(payload, ensure_ascii=False, indent=2),
            "requirements_brief",
            {
                "source_count": len(source_inventory),
                "missing_dimension_count": len(missing),
                "pipeline_steps": ["capability_sweep", "requirements_analysis"],
            },
        )

    def validate(self, result: SkillResult) -> None:
        super().validate(result)
        payload = json.loads(result.content)
        required = {
            "deliverable", "topic", "style", "audience", "content_boundaries",
            "reference_inventory", "prior_thoughts",
            "workflow_profile", "confidentiality_level",
        }
        if not required <= payload.keys():
            raise ValueError("requirements_brief 缺少必要需求维度")
