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
        processed_text = request.inputs["data_processing"]
        quant_text = request.inputs.get("quant_finance_research", "{}")
        if self.generator:
            content = self.generator.generate(
                system="你是信息可视化设计师，仅依据提供材料生成 Mermaid 或 Vega-Lite 规范。",
                prompt=(
                    f"议题树：{issue_tree_text}\n章节素材：{materials_text}\n"
                    f"处理后数据：{processed_text}\n"
                    f"量化金融工程：{quant_text}\n"
                    "为流程、架构或量化信息生成可渲染 JSON 资产清单。"
                ),
                max_tokens=5000,
            )
            return SkillResult(content, "visualization_assets", {"prompt_version": "1.0"})

        issue_tree = json.loads(issue_tree_text)
        materials = json.loads(materials_text)
        processed = json.loads(processed_text)
        quant = json.loads(quant_text)
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
        assets.extend(
            [
                {
                    "id": "VIS-EVIDENCE-GRADES",
                    "type": "statistical_chart",
                    "format": "vega-lite",
                    "title": "高可信证据占比决定结论强度",
                    "section_ids": [],
                    "content": {
                        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                        "data": {
                            "values": [
                                {"grade": grade, "count": count}
                                for grade, count in processed.get(
                                    "evidence_grades", {}
                                ).items()
                            ]
                        },
                        "mark": "bar",
                        "encoding": {
                            "x": {"field": "grade", "type": "ordinal"},
                            "y": {"field": "count", "type": "quantitative"},
                        },
                    },
                },
                {
                    "id": "VIS-ISSUE-CLAIM-COVERAGE",
                    "type": "statistical_chart",
                    "format": "vega-lite",
                    "title": "议题证据覆盖暴露研究盲区",
                    "section_ids": [],
                    "content": {
                        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                        "data": {
                            "values": [
                                {
                                    "issue": issue.get("id"),
                                    "claims": sum(
                                        issue.get("id") in claim.get("issue_ids", [])
                                        for claim in processed.get("claims", [])
                                    ),
                                }
                                for issue in issue_tree.get("issues", [])
                            ]
                        },
                        "mark": "bar",
                        "encoding": {
                            "x": {"field": "issue", "type": "nominal"},
                            "y": {"field": "claims", "type": "quantitative"},
                        },
                    },
                },
                {
                    "id": "VIS-SOURCE-TIMELINE",
                    "type": "timeline",
                    "format": "vega-lite",
                    "title": "证据时间分布决定结论时效性",
                    "section_ids": [],
                    "content": {
                        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                        "data": {
                            "values": [
                                {
                                    "date": point.get("published_at"),
                                    "source": point.get("source_id"),
                                }
                                for point in processed.get("data_points", [])
                                if point.get("published_at")
                            ]
                        },
                        "mark": "tick",
                        "encoding": {
                            "x": {"field": "date", "type": "temporal"},
                            "color": {"field": "source", "type": "nominal"},
                        },
                    },
                },
                {
                    "id": "VIS-COMPARATIVE-SCORING",
                    "type": "comparison",
                    "format": "vega-lite",
                    "title": "评分仅在数据锚点充分时成立",
                    "section_ids": [],
                    "content": {
                        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                        "data": {
                            "values": processed.get("scoring", {}).get("results", [])
                        },
                        "mark": "bar",
                        "encoding": {
                            "x": {"field": "candidate", "type": "nominal"},
                            "y": {"field": "weighted_score", "type": "quantitative"},
                        },
                    },
                },
                {
                    "id": "VIS-SOCIAL-SENTIMENT",
                    "type": "statistical_chart",
                    "format": "vega-lite",
                    "title": "去重后的真实用户反馈揭示满意度分布",
                    "section_ids": [],
                    "content": {
                        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                        "data": {
                            "values": [
                                {"sentiment": sentiment, "count": count}
                                for sentiment, count in processed.get(
                                    "social_feedback", {}
                                ).get("sentiment_counts", {}).items()
                            ]
                        },
                        "mark": "bar",
                        "encoding": {
                            "x": {"field": "sentiment", "type": "nominal"},
                            "y": {"field": "count", "type": "quantitative"},
                        },
                    },
                },
            ]
        )
        if quant.get("applicable"):
            metrics = quant.get("backtest", {}).get("metrics", {})
            assets.append(
                {
                    "id": "VIS-QUANT-BACKTEST",
                    "type": "statistical_chart",
                    "format": "vega-lite",
                    "title": "交易成本与样本外约束后的回测指标决定策略可信度",
                    "section_ids": [],
                    "content": {
                        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                        "data": {
                            "values": [
                                {"metric": name, "value": value}
                                for name, value in metrics.items()
                                if isinstance(value, (int, float))
                            ]
                        },
                        "mark": "bar",
                        "encoding": {
                            "x": {"field": "metric", "type": "nominal"},
                            "y": {"field": "value", "type": "quantitative"},
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
