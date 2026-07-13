"""Resolve one versioned, scenario-specific writing standard."""

from __future__ import annotations

import json
from typing import Any

from ..contracts import Skill
from ..models import SkillRequest, SkillResult
from ..standards_store import SQLiteWritingStandardStore


class WritingStandardsSkill(Skill):
    name = "writing_standards"
    version = "1.0.0"

    def __init__(self, store: SQLiteWritingStandardStore) -> None:
        self.store = store

    def execute(self, request: SkillRequest) -> SkillResult:
        config = request.config
        query = " ".join(
            (config.topic, config.output_type, config.style, config.audience)
        )
        explicit_id = config.extra.get("writing_standard_profile")
        profile = self.store.resolve(query, str(explicit_id) if explicit_id else None)
        self.store.record_application(request.workflow_id, profile)

        reference_selection = self._reference_selection(
            profile.scene, config.extra
        )
        security = self._security_policy(
            config.confidentiality_level,
            config.output_format,
            config.extra,
        )
        payload = {
            "profile": profile.to_dict(),
            "selected_by": "explicit" if explicit_id else "trigger_match",
            "scene": profile.scene,
            "rules": profile.rules,
            "required_sections": profile.rules.get("required_sections", []),
            "reference_selection": reference_selection,
            "security": security,
            "one_click_key": profile.id,
            "feedback_applied": list(request.feedback),
        }
        return SkillResult(
            json.dumps(payload, ensure_ascii=False, indent=2),
            "writing_standard",
            {
                "profile_id": profile.id,
                "profile_version": profile.version,
                "scene": profile.scene,
                "reference_status": reference_selection["status"],
                "external_delivery_allowed": security["external_delivery_allowed"],
            },
        )

    @staticmethod
    def _reference_selection(scene: str, extra: dict[str, Any]) -> dict[str, Any]:
        if scene == "industry_investment":
            candidates = extra.get("broker_references", [])
            required_fields = {
                "name", "report_url", "ranking_source", "ranking_date", "specialty"
            }
            valid = [
                item for item in candidates
                if isinstance(item, dict) and required_fields <= item.keys()
            ]
            return {
                "type": "sector_broker_flagship_reports",
                "required_count": 3,
                "selected": valid[:3],
                "status": "verified" if len(valid) >= 3 else "verification_required",
                "missing": max(0, 3 - len(valid)),
                "rule": "领域匹配、榜单/获奖记录可追溯、核验日期明确",
            }
        if scene == "technical":
            candidates = extra.get("arxiv_reference_papers", [])
            valid = [
                item for item in candidates
                if isinstance(item, dict)
                and item.get("arxiv_id")
                and item.get("url")
                and item.get("field")
            ]
            return {
                "type": "same_field_arxiv_papers",
                "required_count": 3,
                "selected": valid,
                "status": "verified" if len(valid) >= 3 else "verification_required",
                "missing": max(0, 3 - len(valid)),
                "rule": "同细分领域、同任务、近期且可复现；记录具体版本号",
            }
        if scene == "public_account":
            candidates = extra.get("verified_creator_references", [])
            valid = [
                item for item in candidates
                if isinstance(item, dict)
                and item.get("verified_blue_v") is True
                and item.get("profile_url")
                and item.get("sample_url")
                and item.get("verified_at")
            ]
            return {
                "type": "verified_blue_v_creators",
                "required_count": 3,
                "selected": valid,
                "status": "verified" if len(valid) >= 3 else "verification_required",
                "missing": max(0, 3 - len(valid)),
                "rule": "蓝V身份、领域匹配、原创样文和核验日期均可追溯",
            }
        return {
            "type": "official_authorities",
            "required_count": 2,
            "selected": [],
            "status": "builtin_authority",
            "missing": 0,
            "rule": "以现行条例、国家标准及组织制度为准",
        }

    @staticmethod
    def _security_policy(
        confidentiality_level: str,
        output_format: str,
        extra: dict[str, Any],
    ) -> dict[str, Any]:
        classified = confidentiality_level in {
            "secret", "confidential", "top_secret"
        }
        internal_approved = (
            confidentiality_level == "internal"
            and extra.get("feishu_target_tenant_confirmed") is True
            and extra.get("feishu_data_residency_approved") is True
        )
        external_allowed = not classified and (
            confidentiality_level == "public"
            or output_format != "feishu"
            or internal_approved
        )
        reason = None
        if classified:
            reason = "国家秘密或涉密内容禁止进入本工作流的外部发布适配器"
        elif (
            confidentiality_level == "internal"
            and output_format == "feishu"
            and not internal_approved
        ):
            reason = "内部材料写入飞书前必须确认目标租户与数据驻留审批"
        return {
            "confidentiality_level": confidentiality_level,
            "external_delivery_allowed": external_allowed,
            "block_reason": reason,
            "required_controls": [
                "最小权限", "目标租户确认", "访问审计", "保留与删除策略"
            ],
        }

    def validate(self, result: SkillResult) -> None:
        super().validate(result)
        payload = json.loads(result.content)
        if not payload.get("profile", {}).get("trigger_keywords"):
            raise ValueError("writing_standards 缺少调用触发词")
        if not payload.get("required_sections"):
            raise ValueError("writing_standards 缺少场景结构规范")
        if payload.get("scene") not in {
            "technical", "industry_investment", "public_account", "official_internal"
        }:
            raise ValueError("writing_standards 返回未知场景")
