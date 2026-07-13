"""Freeze normalized sources with hashes and scene-specific source policy."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import UTC, datetime

from ..contracts import Skill
from ..models import SkillRequest, SkillResult


SCENE_SOURCE_POLICIES = {
    "technical": {
        "required_categories": ("academic",),
        "minimum_sources": 2,
        "description": "技术报告至少需要两项学术来源；产业与社媒按主题选用",
    },
    "industry_investment": {
        "required_categories": ("industry", "academic"),
        "minimum_sources": 3,
        "description": "投研报告必须覆盖产业/一手信息与独立学术或方法来源",
    },
    "public_account": {
        "required_categories": ("industry", "social_media"),
        "minimum_sources": 2,
        "description": "公众号报告必须覆盖可核验事实来源与真实场景反馈",
    },
    "official_internal": {
        "required_categories": ("industry",),
        "minimum_sources": 1,
        "description": "官方/内参必须至少包含法规、标准或组织授权的一手来源",
    },
}


class SourceSnapshotSkill(Skill):
    name = "source_snapshot"
    version = "1.0.0"

    def execute(self, request: SkillRequest) -> SkillResult:
        research = json.loads(request.inputs["research"])
        standards = json.loads(request.inputs["writing_standards"])
        scene = standards["scene"]
        policy = SCENE_SOURCE_POLICIES[scene]
        now = datetime.now(UTC).isoformat()
        frozen = []
        checksums = {}
        incomplete = []
        for index, source in enumerate(research.get("sources", []), 1):
            source_id = str(source.get("id", f"S{index}"))
            content = str(source.get("content") or "")
            checksum = hashlib.sha256(content.encode("utf-8")).hexdigest()
            complete = bool(
                source.get("title")
                and source.get("url")
                and content.strip()
            )
            if not complete:
                incomplete.append(source_id)
            item = {
                **source,
                "id": source_id,
                "content": content,
                "snapshot_checksum": checksum,
                "snapshot_at": now,
                "snapshot_complete": complete,
                "retrieval_provider": source.get("provider", "configured_source"),
            }
            frozen.append(item)
            checksums[source_id] = checksum
        present = sorted(
            {
                str(source.get("category"))
                for source in frozen
                if source.get("category") not in {None, "unknown"}
            }
        )
        missing = sorted(set(policy["required_categories"]) - set(present))
        policy_passed = (
            not missing
            and len(frozen) >= int(policy["minimum_sources"])
            and not incomplete
        )
        payload = {
            "snapshot_id": str(uuid.uuid4()),
            "created_at": now,
            "topic": request.config.topic,
            "scene": scene,
            "source_policy": policy,
            "sources": frozen,
            "checksums": checksums,
            "retrieval_summary": research.get("retrieval_summary", {}),
            "social_feedback": research.get("social_feedback", {}),
            "policy_compliance": {
                "required_categories": list(policy["required_categories"]),
                "present_categories": present,
                "missing_categories": missing,
                "minimum_sources": policy["minimum_sources"],
                "actual_sources": len(frozen),
                "incomplete_snapshot_ids": incomplete,
                "passed": policy_passed,
            },
            "feedback_applied": list(request.feedback),
        }
        return SkillResult(
            json.dumps(payload, ensure_ascii=False, indent=2),
            "source_snapshot",
            {
                "snapshot_id": payload["snapshot_id"],
                "source_count": len(frozen),
                "complete_count": len(frozen) - len(incomplete),
                "policy_passed": policy_passed,
                "scene": scene,
            },
        )

    def validate(self, result: SkillResult) -> None:
        super().validate(result)
        payload = json.loads(result.content)
        if not {
            "snapshot_id", "created_at", "sources", "checksums",
            "policy_compliance",
        } <= payload.keys():
            raise ValueError("source_snapshot 缺少必要字段")
        for source in payload["sources"]:
            if payload["checksums"].get(source["id"]) != source.get(
                "snapshot_checksum"
            ):
                raise ValueError("source_snapshot 来源哈希不一致")
