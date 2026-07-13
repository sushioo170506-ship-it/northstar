"""Assemble the quality-approved candidate into the requested deliverable."""

from __future__ import annotations

import json

from ..contracts import DocumentRenderer, Skill
from ..models import SkillRequest, SkillResult


class PublishSkill(Skill):
    name = "publish"

    def __init__(self, renderer: DocumentRenderer | None = None) -> None:
        self.renderer = renderer

    def execute(self, request: SkillRequest) -> SkillResult:
        report = request.inputs["review"]
        quality = json.loads(request.inputs["quality_gate"])
        visualizations = json.loads(request.inputs["visualization"])
        capability = json.loads(request.inputs["capability_sweep"])
        skill_research = json.loads(request.inputs["skill_research"])
        writing_standard = json.loads(request.inputs["writing_standards"])
        if not quality.get("passed"):
            raise ValueError("质量门未通过，禁止发布")
        output_format = request.config.output_format
        security = writing_standard["security"]
        if output_format == "feishu" and not security["external_delivery_allowed"]:
            raise ValueError(
                "飞书发布被信息安全策略阻断: "
                + str(security.get("block_reason") or "未获外部发布许可")
            )
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
            "self_contained": output_format in {
                "markdown", "json", "text"
            },
            "raster_exported": False,
            "third_party_candidates_reviewed": len(
                skill_research.get("candidates", [])
            ),
            "adapted_skill_specs_pending_review": len(
                skill_research.get("adapted_skill_specs", [])
            ),
            "limitations": [],
            "writing_standard_profile": writing_standard["profile"]["id"],
            "confidentiality_level": request.config.confidentiality_level,
            "delivery_link_policy": "file_only",
            "cursor_preview_link_allowed": False,
            "public_hosting_allowed": bool(
                request.config.extra.get("public_hosting_allowed", False)
            ),
        }
        published_content = report
        if output_format in {
            "docx", "pdf", "feishu", "pptx", "slides_html", "slides_zip"
        }:
            if self.renderer is None:
                raise ValueError(
                    f"{output_format} 输出需要配置 DocumentRenderer"
                )
            published_content, render_metadata = self.renderer.render(
                content=report,
                output_format=output_format,
                visualizations=visualizations,
            )
            if not render_metadata.get("rendered"):
                raise ValueError(f"{output_format} 渲染器未返回成功状态")
            manifest.update(
                {
                    "self_contained": True,
                    "rendered": True,
                    "render_metadata": render_metadata,
                }
            )
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
            published_content,
            "published_report",
            {"publish_manifest": manifest, "quality_score": quality.get("total_score")},
        )
