"""Assemble the quality-approved candidate into the requested deliverable."""

from __future__ import annotations

import json

from ..contracts import Skill
from ..models import SkillRequest, SkillResult


class PublishSkill(Skill):
    name = "publish"

    def execute(self, request: SkillRequest) -> SkillResult:
        report = request.inputs["review"]
        quality = json.loads(request.inputs["quality_gate"])
        visualizations = json.loads(request.inputs["visualization"])
        capability = json.loads(request.inputs["capability_sweep"])
        if not quality.get("passed"):
            raise ValueError("质量门未通过，禁止发布")
        output_format = request.config.output_format
        renderer_ids = {
            item["id"]: item["status"]
            for item in capability.get("external_integrations", [])
            if item["capability"] in {"diagram_rendering", "chart_rendering", "document_publishing"}
        }
        manifest = {
            "format": output_format,
            "character_count": len(report),
            "visual_asset_count": len(visualizations.get("assets", [])),
            "renderers": renderer_ids,
            "self_contained": output_format in {"markdown", "json", "text"},
            "raster_exported": False,
            "limitations": [],
        }
        if output_format == "html" and any(
            item["format"] in {"mermaid", "vega-lite"}
            for item in visualizations.get("assets", [])
        ):
            manifest["self_contained"] = False
            manifest["limitations"].append(
                "内置实现保留 Mermaid/Vega-Lite 规范；配置对应渲染器后才能内联 SVG"
            )
        if request.config.extra.get("require_png", False):
            manifest["limitations"].append(
                "PNG 是条件能力；当前运行未提供可验证的渲染器输出"
            )
        return SkillResult(
            report,
            "published_report",
            {"publish_manifest": manifest, "quality_score": quality.get("total_score")},
        )
