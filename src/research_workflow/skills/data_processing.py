"""Claim ledger, triangulation, data grading and optional comparative scoring."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict

from ..contracts import Skill
from ..models import SkillRequest, SkillResult


class DataProcessingSkill(Skill):
    name = "data_processing"

    def execute(self, request: SkillRequest) -> SkillResult:
        research = json.loads(request.inputs["research"])
        evidence = json.loads(request.inputs["evidence_governance"])
        outline = json.loads(request.inputs["outline"])
        governed = {item["id"]: item for item in evidence.get("sources", [])}
        issue_sections = {
            section.get("linked_issue"): section["id"]
            for section in outline.get("sections", [])
            if section.get("linked_issue")
        }
        grouped: dict[str, list[dict]] = defaultdict(list)
        data_points = []
        for source in research.get("sources", []):
            key = str(source.get("claim_key") or source.get("id"))
            grouped[key].append(source)
            for raw in re.findall(r"(?<!\w)(\d+(?:\.\d+)?%?)", source.get("content", "")):
                data_points.append(
                    {
                        "value": raw,
                        "source_id": source.get("id"),
                        "published_at": source.get("published_at"),
                        "context": source.get("content", "")[:240],
                    }
                )

        claims = []
        grade_counts: Counter[str] = Counter()
        conflict_count = 0
        for index, (key, sources) in enumerate(grouped.items(), 1):
            source_ids = [str(item.get("id")) for item in sources]
            independent_count = sum(
                not governed.get(source_id, {}).get("stakeholder", False)
                for source_id in source_ids
            )
            issue_ids = sorted(
                {
                    issue_id
                    for source in sources
                    for issue_id in source.get("issue_ids", [])
                    if issue_id in issue_sections
                }
            )
            conflicts = sorted(
                {
                    str(conflict)
                    for source in sources
                    for conflict in source.get("conflicts_with", [])
                }
            )
            conflict_count += bool(conflicts)
            if independent_count >= 2:
                grade = "A+"
                confidence = 0.95
            elif len(source_ids) >= 2 and independent_count >= 1:
                grade = "A"
                confidence = 0.88
            elif any(
                governed.get(source_id, {}).get("traceable", False)
                for source_id in source_ids
            ):
                grade = "B" if independent_count else "C"
                confidence = 0.75 if independent_count else 0.55
            else:
                grade = "D"
                confidence = 0.25
            grade_counts[grade] += 1
            statement = next(
                (
                    source.get("claim") or source.get("content")
                    for source in sources
                    if source.get("claim") or source.get("content")
                ),
                sources[0].get("title", "未命名论断"),
            )
            claims.append(
                {
                    "id": f"CLAIM-{index:03d}",
                    "claim_key": key,
                    "statement": str(statement)[:500],
                    "source_ids": source_ids,
                    "independent_source_count": independent_count,
                    "issue_ids": issue_ids,
                    "section_ids": [issue_sections[item] for item in issue_ids],
                    "critical": any(bool(item.get("critical")) for item in sources),
                    "grade": grade,
                    "confidence": confidence,
                    "conflicts": conflicts,
                    "status": "conflicted" if conflicts else "supported",
                }
            )

        scoring = self._score(request)
        critical = [claim for claim in claims if claim["critical"]]
        payload = {
            "claims": claims,
            "data_points": data_points,
            "social_feedback": research.get("social_feedback", {}),
            "evidence_grades": dict(sorted(grade_counts.items())),
            "triangulation": {
                "claim_count": len(claims),
                "multi_source_claim_count": sum(
                    len(claim["source_ids"]) >= 2 for claim in claims
                ),
                "conflicted_claim_count": conflict_count,
                "critical_claim_count": len(critical),
                "critical_verified_count": sum(
                    claim["independent_source_count"] >= 2 and not claim["conflicts"]
                    for claim in critical
                ),
            },
            "scoring": scoring,
            "feedback_applied": list(request.feedback),
        }
        return SkillResult(
            json.dumps(payload, ensure_ascii=False, indent=2),
            "processed_research_data",
            {
                "claim_count": len(claims),
                "data_point_count": len(data_points),
                "conflicted_claim_count": conflict_count,
                "scoring_status": scoring["status"],
            },
        )

    def _score(self, request: SkillRequest) -> dict:
        candidates = request.config.extra.get("comparison_candidates", [])
        dimensions = request.config.extra.get("scoring_dimensions", [])
        if not candidates or not dimensions:
            return {
                "status": "not_applicable",
                "reason": "未配置可比对象或数据锚定评分维度，禁止主观打分",
                "candidates": list(candidates),
                "dimensions": [],
                "results": [],
            }
        if not 5 <= len(candidates) <= 10 or not 4 <= len(dimensions) <= 6:
            return {
                "status": "invalid",
                "reason": "可比对象必须 5-10 个，评分维度必须 4-6 个",
                "candidates": list(candidates),
                "dimensions": dimensions,
                "results": [],
            }
        total_weight = sum(float(item.get("weight", 0)) for item in dimensions)
        if total_weight <= 0:
            return {
                "status": "invalid",
                "reason": "评分维度权重总和必须大于 0",
                "candidates": list(candidates),
                "dimensions": dimensions,
                "results": [],
            }
        results = []
        for candidate in candidates:
            weighted = 0.0
            details = []
            for dimension in dimensions:
                values = dimension.get("values", {})
                raw = values.get(candidate)
                if raw is None:
                    details.append(
                        {"dimension": dimension.get("name"), "score": None, "reason": "缺数据"}
                    )
                    continue
                anchor_10 = dimension.get("anchor_10")
                anchor_5 = dimension.get("anchor_5")
                if anchor_10 is None or anchor_5 is None or anchor_10 == anchor_5:
                    details.append(
                        {
                            "dimension": dimension.get("name"),
                            "score": None,
                            "reason": "缺少有效的 10/5 分数据锚点",
                        }
                    )
                    continue
                direction = 1.0 if dimension.get("higher_is_better", True) else -1.0
                numerator = direction * (float(raw) - float(anchor_5))
                denominator = direction * (float(anchor_10) - float(anchor_5))
                score = max(0.0, min(10.0, 5 + 5 * numerator / denominator))
                weight = float(dimension.get("weight", 0)) / total_weight
                weighted += score * weight
                details.append(
                    {
                        "dimension": dimension.get("name"),
                        "score": score,
                        "weight": weight,
                        "source": dimension.get("source"),
                        "value": raw,
                        "anchor_10": anchor_10,
                        "anchor_5": anchor_5,
                        "calculation": (
                            f"{score:.2f} = 5 + 5 × ({raw} - {anchor_5})"
                            f" / ({anchor_10} - {anchor_5})"
                        ),
                    }
                )
            results.append(
                {"candidate": candidate, "weighted_score": round(weighted, 2), "details": details}
            )
        results.sort(key=lambda item: item["weighted_score"], reverse=True)
        return {
            "status": "completed",
            "reason": None,
            "candidates": list(candidates),
            "dimensions": dimensions,
            "results": results,
            "boundary": "权重和锚点仅适用于当前研究场景；缺失数据不应推断补齐。",
        }

    def validate(self, result: SkillResult) -> None:
        super().validate(result)
        payload = json.loads(result.content)
        if not {"claims", "data_points", "triangulation", "scoring"} <= payload.keys():
            raise ValueError("processed_research_data 缺少必要字段")
