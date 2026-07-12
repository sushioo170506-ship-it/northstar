"""Create portable chart and diagram specifications from report materials."""

from __future__ import annotations

import json
import re

from ..contracts import Skill, TextGenerator
from ..models import SkillRequest, SkillResult


class VisualizationSkill(Skill):
    name = "visualization"

    def __init__(self, generator: TextGenerator | None = None) -> None:
        self.generator = generator

    def execute(self, request: SkillRequest) -> SkillResult:
        issue_tree_text = request.inputs["issue_tree"]
        materials_text = request.inputs["material_integration"]
        if self.generator:
            content = self.generator.generate(
                system="你是信息可视化设计师，仅依据提供材料生成 Mermaid 或 Vega-Lite 规范。",
                prompt=(
                    f"议题树：{issue_tree_text}\n章节素材：{materials_text}\n"
                    "为流程、架构或量化信息生成可渲染 JSON 资产清单。"
                ),
                max_tokens=5000,
            )
            return SkillResult(content, "visualization_assets", {"prompt_version": "1.0"})

        issue_tree = json.loads(issue_tree_text)
        materials = json.loads(materials_text)
        assets = []
        flow_lines = ["flowchart TD", '  ROOT["研究主题"]']
        for issue in issue_tree.get("issues", []):
            issue_id = re.sub(r"[^A-Za-z0-9_]", "_", issue["id"])
            label = str(issue.get("question", "")).replace('"', "'")
            flow_lines.append(f'  {issue_id}["{label}"]')
            flow_lines.append(f"  ROOT --> {issue_id}")
            for child in issue.get("children", []):
                child_id = re.sub(r"[^A-Za-z0-9_]", "_", child["id"])
                child_label = str(child.get("question", "")).replace('"', "'")
                flow_lines.append(f'  {child_id}["{child_label}"]')
                flow_lines.append(f"  {issue_id} --> {child_id}")
        assets.append(
            {
                "id": "VIS-ISSUE-TREE",
                "type": "logic_flow",
                "format": "mermaid",
                "title": "研究问题逻辑结构",
                "section_ids": [],
                "content": "\n".join(flow_lines),
            }
        )

        category_counts: dict[str, int] = {}
        numeric_points = []
        for section_id, section in materials.get("sections", {}).items():
            for material in section.get("materials", []):
                category = material.get("category", "unknown")
                category_counts[category] = category_counts.get(category, 0) + 1
                for raw in re.findall(r"(?<!\w)(\d+(?:\.\d+)?)%?", material.get("content", "")):
                    numeric_points.append(
                        {
                            "section": section_id,
                            "source": material.get("source_id"),
                            "value": float(raw),
                        }
                    )
        assets.append(
            {
                "id": "VIS-SOURCE-MIX",
                "type": "statistical_chart",
                "format": "vega-lite",
                "title": "来源类别构成",
                "section_ids": [],
                "content": {
                    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                    "data": {
                        "values": [
                            {"category": category, "count": count}
                            for category, count in sorted(category_counts.items())
                        ]
                    },
                    "mark": "bar",
                    "encoding": {
                        "x": {"field": "category", "type": "nominal"},
                        "y": {"field": "count", "type": "quantitative"},
                    },
                },
            }
        )
        if numeric_points:
            assets.append(
                {
                    "id": "VIS-QUANTITATIVE-EVIDENCE",
                    "type": "statistical_chart",
                    "format": "vega-lite",
                    "title": "量化素材分布",
                    "section_ids": sorted({point["section"] for point in numeric_points}),
                    "content": {
                        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                        "data": {"values": numeric_points},
                        "mark": "point",
                        "encoding": {
                            "x": {"field": "section", "type": "nominal"},
                            "y": {"field": "value", "type": "quantitative"},
                            "color": {"field": "source", "type": "nominal"},
                        },
                    },
                }
            )
        payload = {
            "assets": assets,
            "metrics": {
                "asset_count": len(assets),
                "chart_count": sum(asset["type"] == "statistical_chart" for asset in assets),
                "diagram_count": sum(asset["type"] != "statistical_chart" for asset in assets),
            },
            "feedback_applied": list(request.feedback),
        }
        return SkillResult(
            json.dumps(payload, ensure_ascii=False, indent=2),
            "visualization_assets",
            payload["metrics"],
        )

    def validate(self, result: SkillResult) -> None:
        super().validate(result)
        payload = json.loads(result.content)
        if not payload.get("assets"):
            raise ValueError("visualization_assets 至少需要一个可视化成果")
        for asset in payload["assets"]:
            if not {"id", "type", "format", "content"} <= asset.keys():
                raise ValueError("可视化资产缺少必要字段")
