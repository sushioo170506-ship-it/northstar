"""Traverse the complete skill and integration catalog before execution."""

from __future__ import annotations

import json

from ..contracts import Skill
from ..integrations import BUILTIN_SKILL_ORDER, DEFAULT_INTEGRATIONS
from ..models import SkillRequest, SkillResult


class CapabilitySweepSkill(Skill):
    name = "capability_sweep"

    def execute(self, request: SkillRequest) -> SkillResult:
        enabled = set(request.config.extra.get("enabled_integrations", []))
        disabled = set(request.config.extra.get("disabled_integrations", []))
        external = []
        for integration in DEFAULT_INTEGRATIONS:
            if integration.id in disabled:
                status = "disabled_by_config"
                reason = "用户或部署配置显式禁用"
            elif integration.id in enabled:
                status = "configured"
                reason = "本工作流已配置，适配器应在对应节点调用"
            else:
                status = "reviewed_not_configured"
                reason = "已遍历能力目录，但当前运行未配置依赖或凭证"
            external.append(
                {
                    "id": integration.id,
                    "capability": integration.capability,
                    "source": integration.source,
                    "license": integration.license,
                    "stars_checked": integration.stars_checked,
                    "status": status,
                    "reason": reason,
                }
            )
        payload = {
            "builtin_skills": [
                {"name": name, "status": "scheduled", "mandatory": True}
                for name in BUILTIN_SKILL_ORDER
            ],
            "external_integrations": external,
            "policy": {
                "all_builtin_skills_must_execute": True,
                "all_external_integrations_must_be_reviewed": True,
                "external_execution_requires_configuration": True,
                "skip_requires_reason": True,
            },
            "metrics": {
                "builtin_count": len(BUILTIN_SKILL_ORDER),
                "external_catalog_count": len(external),
                "external_traversed_count": len(external),
                "external_configured_count": sum(
                    item["status"] == "configured" for item in external
                ),
            },
        }
        return SkillResult(
            json.dumps(payload, ensure_ascii=False, indent=2),
            "capability_manifest",
            payload["metrics"],
        )

    def validate(self, result: SkillResult) -> None:
        super().validate(result)
        payload = json.loads(result.content)
        metrics = payload.get("metrics", {})
        if metrics.get("external_catalog_count") != metrics.get(
            "external_traversed_count"
        ):
            raise ValueError("外部能力目录未被完整遍历")
        actual = {item["name"] for item in payload.get("builtin_skills", [])}
        if actual != set(BUILTIN_SKILL_ORDER):
            raise ValueError("内置 Skill 清单不完整")
