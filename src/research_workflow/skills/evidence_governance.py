"""Source provenance, independence and red-line evidence checks."""

from __future__ import annotations

import json

from ..contracts import Skill, TextGenerator
from ..models import SkillRequest, SkillResult


class EvidenceGovernanceSkill(Skill):
    name = "evidence_governance"

    def __init__(self, generator: TextGenerator | None = None) -> None:
        self.generator = generator

    def execute(self, request: SkillRequest) -> SkillResult:
        research_text = request.inputs.get(
            "source_snapshot", request.inputs.get("research", "{}")
        )
        issue_tree_text = request.inputs["issue_tree"]
        model_analysis = None
        if self.generator:
            prompt = (
                "审计来源的主体、时间、一手性、利益相关性、独立验证和冲突。"
                "不得把无法验证等同于虚假。输出 JSON 证据账本、问题和红线。\n"
                f"证据包：{research_text}\n议题树：{issue_tree_text}"
            )
            generated = self.generator.generate(
                system="你是独立证据治理审核员。", prompt=prompt, max_tokens=4000
            )
            try:
                model_analysis = json.loads(generated)
            except json.JSONDecodeError:
                model_analysis = {"raw": generated, "parse_error": True}

        research = json.loads(research_text)
        issue_tree = json.loads(issue_tree_text)
        valid_issue_ids = {
            issue["id"] for issue in issue_tree.get("issues", []) if issue.get("id")
        }
        issue_coverage: dict[str, list[str]] = {
            issue_id: [] for issue_id in valid_issue_ids
        }
        governed = []
        issues: list[dict[str, str]] = []
        red_lines: list[dict[str, str]] = []
        for index, source in enumerate(research.get("sources", [])):
            source_id = str(source.get("id", f"S{index + 1}"))
            source_type = str(source.get("source_type", "unknown"))
            category = str(source.get("category", "unknown"))
            original_url = source.get("url")
            stakeholder = bool(source.get("stakeholder", source_type == "stakeholder"))
            independent = source.get("independent_verification", [])
            if isinstance(independent, str):
                independent = [independent]
            traceable = bool(source.get("title")) and bool(
                source.get("url") or source.get("content")
            )
            published_at = source.get("published_at") or source.get("year")
            critical = bool(source.get("critical", False))
            source_issue_ids = source.get("issue_ids", [])
            if isinstance(source_issue_ids, str):
                source_issue_ids = [source_issue_ids]
            linked_issues = sorted(set(source_issue_ids) & valid_issue_ids)
            for issue_id in linked_issues:
                issue_coverage[issue_id].append(source_id)
            if source.get("fabricated") is True:
                red_lines.append(
                    {"code": "FABRICATED_SOURCE", "source_id": source_id,
                     "message": "来源被显式标记为编造"}
                )
            if critical and not traceable:
                red_lines.append(
                    {"code": "UNTRACEABLE_CRITICAL_SOURCE", "source_id": source_id,
                     "message": "关键来源无法追溯"}
                )
            if critical and stakeholder and not independent:
                red_lines.append(
                    {"code": "SOLE_STAKEHOLDER_SUPPORT", "source_id": source_id,
                     "message": "关键论断仅由利益相关方声明支撑"}
                )
            if not traceable:
                issues.append(
                    {"severity": "high" if critical else "medium", "source_id": source_id,
                     "message": "来源缺少标题或可核验内容/URL"}
                )
            if not published_at:
                issues.append(
                    {"severity": "low", "source_id": source_id, "message": "来源缺少发布时间"}
                )
            governed.append(
                {
                    "id": source_id,
                    "title": source.get("title", ""),
                    "category": category,
                    "original_url": original_url,
                    "source_type": source_type,
                    "published_at": published_at,
                    "traceable": traceable,
                    "stakeholder": stakeholder,
                    "independent_verification": independent,
                    "critical": critical,
                    "issue_ids": linked_issues,
                    "snapshot_checksum": source.get("snapshot_checksum"),
                    "snapshot_at": source.get("snapshot_at"),
                    "snapshot_complete": source.get("snapshot_complete", False),
                }
            )
        total = len(governed)
        traceable_count = sum(item["traceable"] for item in governed)
        linked_count = sum(bool(item["original_url"]) for item in governed)
        categories = sorted(
            {item["category"] for item in governed if item["category"] != "unknown"}
        )
        independently_supported = sum(
            bool(item["independent_verification"]) for item in governed if item["critical"]
        )
        critical_count = sum(item["critical"] for item in governed)
        payload = {
            "sources": governed,
            "issue_coverage": issue_coverage,
            "metrics": {
                "source_count": total,
                "traceability_ratio": traceable_count / total if total else 0.0,
                "original_link_coverage": linked_count / total if total else 0.0,
                "source_categories": categories,
                "source_category_count": len(categories),
                "critical_source_count": critical_count,
                "critical_independent_coverage": (
                    independently_supported / critical_count if critical_count else None
                ),
            },
            "issues": issues,
            "red_lines": red_lines,
            "model_analysis": model_analysis,
            "feedback_applied": list(request.feedback),
        }
        return SkillResult(
            json.dumps(payload, ensure_ascii=False, indent=2),
            "evidence_ledger",
            {
                "source_count": total,
                "red_line_count": len(red_lines),
                "traceability_ratio": payload["metrics"]["traceability_ratio"],
                "original_link_coverage": payload["metrics"]["original_link_coverage"],
                "source_category_count": len(categories),
                "prompt_version": "1.0" if self.generator else None,
            },
        )

    def validate(self, result: SkillResult) -> None:
        super().validate(result)
        payload = json.loads(result.content)
        if not {"sources", "metrics", "issues", "red_lines"} <= payload.keys():
            raise ValueError("evidence_ledger 缺少必要字段")
