"""Verify each claim against immutable source spans and numeric anchors."""

from __future__ import annotations

import json
import re

from ..contracts import Skill
from ..models import SkillRequest, SkillResult


NUMBER = re.compile(r"(?<!\w)\d+(?:\.\d+)?(?:%|亿|万|千|百|元|美元|年|月|日)?")


class ClaimVerificationSkill(Skill):
    name = "claim_verification"
    version = "1.0.0"

    def execute(self, request: SkillRequest) -> SkillResult:
        processed = json.loads(request.inputs["data_processing"])
        snapshot = json.loads(request.inputs["source_snapshot"])
        evidence = json.loads(request.inputs["evidence_governance"])
        sources = {str(item["id"]): item for item in snapshot.get("sources", [])}
        governed = {str(item["id"]): item for item in evidence.get("sources", [])}
        verified_claims = []
        red_lines = []
        for claim in processed.get("claims", []):
            statement = str(claim.get("statement") or "")
            claim_numbers = sorted(set(NUMBER.findall(statement)))
            spans = []
            source_numbers: set[str] = set()
            for source_id in claim.get("source_ids", []):
                source = sources.get(str(source_id), {})
                content = str(source.get("content") or "")
                source_numbers.update(NUMBER.findall(content))
                span = self._evidence_span(statement, content)
                if span:
                    spans.append(
                        {
                            "source_id": str(source_id),
                            "quote": span,
                            "snapshot_checksum": source.get(
                                "snapshot_checksum"
                            ),
                            "original_url": source.get("url"),
                        }
                    )
            missing_numbers = sorted(set(claim_numbers) - source_numbers)
            numeric_consistent = not missing_numbers
            has_evidence = bool(spans)
            unresolved_conflict = bool(claim.get("conflicts"))
            critical = bool(claim.get("critical"))
            independent = int(claim.get("independent_source_count", 0))
            verified = (
                has_evidence
                and numeric_consistent
                and not unresolved_conflict
                and claim.get("grade") != "D"
                and (not critical or independent >= 2)
            )
            reasons = []
            if not has_evidence:
                reasons.append("没有可定位的原文证据片段")
            if missing_numbers:
                reasons.append("数字未在来源中找到：" + "、".join(missing_numbers))
            if unresolved_conflict:
                reasons.append("存在未解决冲突")
            if critical and independent < 2:
                reasons.append("关键论断缺少两个独立来源")
            if not verified and critical:
                red_lines.append(
                    {
                        "code": "UNVERIFIED_CRITICAL_CLAIM",
                        "claim_id": claim["id"],
                        "message": "；".join(reasons) or "关键论断未通过验证",
                    }
                )
            verified_claims.append(
                {
                    **claim,
                    "evidence_spans": spans,
                    "numeric_anchors": claim_numbers,
                    "missing_numeric_anchors": missing_numbers,
                    "numeric_consistent": numeric_consistent,
                    "verification_status": (
                        "verified" if verified else "blocked"
                    ),
                    "verification_reasons": reasons,
                }
            )
        count = len(verified_claims)
        verified_count = sum(
            item["verification_status"] == "verified"
            for item in verified_claims
        )
        unsupported = [
            item["id"] for item in verified_claims
            if item["verification_status"] != "verified"
        ]
        payload = {
            "claims": verified_claims,
            "metrics": {
                "claim_count": count,
                "verified_claim_count": verified_count,
                "unsupported_claim_count": len(unsupported),
                "evidence_span_coverage": (
                    verified_count / count if count else 0.0
                ),
                "numeric_consistency_ratio": (
                    sum(item["numeric_consistent"] for item in verified_claims)
                    / count if count else 0.0
                ),
                "critical_claim_count": sum(
                    item["critical"] for item in verified_claims
                ),
                "critical_verified_count": sum(
                    item["critical"]
                    and item["verification_status"] == "verified"
                    for item in verified_claims
                ),
                "unresolved_conflict_count": sum(
                    bool(item["conflicts"]) for item in verified_claims
                ),
            },
            "unsupported_claim_ids": unsupported,
            "red_lines": red_lines,
            "all_claims_verified": count > 0 and not unsupported,
            "feedback_applied": list(request.feedback),
        }
        return SkillResult(
            json.dumps(payload, ensure_ascii=False, indent=2),
            "claim_verification_report",
            {
                "claim_count": count,
                "verified_claim_count": verified_count,
                "unsupported_claim_count": len(unsupported),
                "red_line_count": len(red_lines),
            },
        )

    @staticmethod
    def _evidence_span(statement: str, content: str) -> str:
        if not content.strip():
            return ""
        normalized_statement = " ".join(statement.split())
        normalized_content = " ".join(content.split())
        if normalized_statement and normalized_statement in normalized_content:
            start = normalized_content.index(normalized_statement)
            return normalized_content[max(0, start - 80):start + len(
                normalized_statement
            ) + 80]
        statement_tokens = set(
            re.findall(r"[A-Za-z0-9_]+|[\u3400-\u9fff]", normalized_statement)
        )
        content_tokens = set(
            re.findall(r"[A-Za-z0-9_]+|[\u3400-\u9fff]", normalized_content)
        )
        overlap = (
            len(statement_tokens & content_tokens) / len(statement_tokens)
            if statement_tokens else 0.0
        )
        return normalized_content[:500] if overlap >= 0.6 else ""

    def validate(self, result: SkillResult) -> None:
        super().validate(result)
        payload = json.loads(result.content)
        if not {"claims", "metrics", "red_lines", "all_claims_verified"} <= payload.keys():
            raise ValueError("claim_verification 缺少必要字段")
