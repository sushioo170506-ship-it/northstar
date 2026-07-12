"""Discover, license-screen and adapt third-party agent skills."""

from __future__ import annotations

import json
import math
import re
import urllib.parse
import urllib.request
from typing import Any

from ..contracts import Skill
from ..integrations import DEFAULT_INTEGRATIONS
from ..models import SkillRequest, SkillResult


PERMISSIVE_LICENSES = {"MIT", "MIT-0", "Apache-2.0", "BSD-3-Clause"}
DEFAULT_GITHUB_MIN_STARS = 500
DEFAULT_OPENCLAW_MIN_STARS = 300
REQUIRED_PROVENANCE_FIELDS = {
    "name", "source_url", "author", "license", "version", "channel"
}


class SkillResearchSkill(Skill):
    """Meta-skill: research skills, not the report's subject matter."""

    name = "skill_research"

    def execute(self, request: SkillRequest) -> SkillResult:
        requirements = json.loads(request.inputs["requirements_analysis"])
        candidates = self._curated_candidates()
        candidates.extend(self._configured_candidates(request))
        live_errors = []
        if request.config.extra.get("live_skill_research", False):
            try:
                candidates.extend(self._github_search(requirements["topic"]))
            except Exception as exc:
                live_errors.append({"channel": "github", "error": str(exc)})
        deduplicated = {
            candidate["source_url"]: candidate for candidate in candidates
        }
        ranked = []
        github_min_stars = int(
            request.config.extra.get(
                "github_skill_min_stars", DEFAULT_GITHUB_MIN_STARS
            )
        )
        openclaw_min_stars = int(
            request.config.extra.get(
                "openclaw_skill_min_stars", DEFAULT_OPENCLAW_MIN_STARS
            )
        )
        for candidate in deduplicated.values():
            decision, reason = self._license_decision(candidate["license"])
            if (
                candidate["channel"] == "github_live"
                and not candidate.get("original_skill_path")
                and decision == "adapt_allowed"
            ):
                decision = "review_required"
                reason = "仅发现仓库；必须定位具体 SKILL.md 并复核子目录许可证"
            minimum_stars = self._minimum_stars(
                candidate, github_min_stars, openclaw_min_stars
            )
            stars = candidate.get("stars")
            if (
                minimum_stars > 0
                and (stars is None or int(stars) < minimum_stars)
                and decision not in {"reject"}
            ):
                decision = "below_threshold"
                reason = (
                    f"Stars {stars if stars is not None else 'unknown'} "
                    f"低于渠道门槛 {minimum_stars}"
                )
            candidate = {
                **candidate,
                "minimum_stars": minimum_stars,
                "match_score": self._match_score(candidate, requirements),
                "decision": decision,
                "decision_reason": reason,
            }
            ranked.append(candidate)
        ranked.sort(
            key=lambda item: (item["decision"] == "adapt_allowed", item["match_score"]),
            reverse=True,
        )
        limit = int(request.config.extra.get("max_adapted_skills", 3))
        adapted = [
            self._adapt(candidate) for candidate in ranked
            if candidate["decision"] == "adapt_allowed"
        ][:limit]
        payload = {
            "query": {
                "topic": requirements["topic"],
                "output_type": requirements["deliverable"]["type"],
                "channels": ["github", "openclaw_hub", "configured_repository"],
                "live_github_search": request.config.extra.get(
                    "live_skill_research", False
                ),
            },
            "candidates": ranked,
            "adapted_skill_specs": adapted,
            "live_search_errors": live_errors,
            "policy": {
                "permissive_licenses": sorted(PERMISSIVE_LICENSES),
                "unknown_license_action": "reject",
                "noncommercial_action": "reject",
                "copyleft_action": "external_process_only",
                "github_min_stars": github_min_stars,
                "openclaw_min_stars": openclaw_min_stars,
                "below_threshold_action": "observe_only",
                "dynamic_execution": False,
                "human_review_required_before_registry_install": True,
            },
            "metrics": {
                "candidate_count": len(ranked),
                "approved_count": sum(
                    item["decision"] == "adapt_allowed" for item in ranked
                ),
                "adapted_spec_count": len(adapted),
                "rejected_count": sum(
                    item["decision"] == "reject" for item in ranked
                ),
                "below_threshold_count": sum(
                    item["decision"] == "below_threshold" for item in ranked
                ),
            },
        }
        return SkillResult(
            json.dumps(payload, ensure_ascii=False, indent=2),
            "skill_research_report",
            payload["metrics"],
        )

    @staticmethod
    def _curated_candidates() -> list[dict[str, Any]]:
        result = []
        for item in DEFAULT_INTEGRATIONS:
            channel = (
                "openclaw_hub"
                if item.id.startswith("openclaw-")
                else "github"
            )
            result.append(
                {
                    "name": item.id,
                    "source_url": item.source,
                    "author": item.author,
                    "license": item.license,
                    "version": item.version_checked,
                    "channel": channel,
                    "stars": item.stars_checked,
                    "description": item.notes,
                    "capability": item.capability,
                    "original_skill_path": None,
                }
            )
        return result

    @staticmethod
    def _configured_candidates(request: SkillRequest) -> list[dict[str, Any]]:
        result = []
        for raw in request.config.extra.get("skill_candidates", []):
            if not isinstance(raw, dict):
                continue
            result.append(
                {
                    "name": str(raw.get("name", "unnamed")),
                    "source_url": str(raw.get("source_url", "")),
                    "author": str(raw.get("author", "unknown")),
                    "license": str(raw.get("license", "NOASSERTION")),
                    "version": str(raw.get("version", "unknown")),
                    "channel": str(raw.get("channel", "configured_repository")),
                    "stars": raw.get("stars"),
                    "description": str(raw.get("description", "")),
                    "capability": str(raw.get("capability", "unknown")),
                    "original_skill_path": raw.get("original_skill_path"),
                }
            )
        return [item for item in result if item["source_url"]]

    @staticmethod
    def _github_search(topic: str) -> list[dict[str, Any]]:
        query = urllib.parse.quote(f"{topic} agent skills SKILL.md")
        url = (
            "https://api.github.com/search/repositories"
            f"?q={query}&sort=stars&order=desc&per_page=10"
        )
        request = urllib.request.Request(
            url, headers={"Accept": "application/vnd.github+json",
                          "User-Agent": "northstar-skill-research/1.0"}
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
        result = []
        for repo in payload.get("items", []):
            owner = repo.get("owner", {}).get("login", "unknown")
            result.append(
                {
                    "name": repo.get("name", "unnamed"),
                    "source_url": repo.get("html_url", ""),
                    "author": owner,
                    "license": (repo.get("license") or {}).get(
                        "spdx_id", "NOASSERTION"
                    ),
                    "version": repo.get("default_branch", "unknown"),
                    "channel": "github_live",
                    "stars": repo.get("stargazers_count"),
                    "description": repo.get("description") or "",
                    "capability": "discovered_agent_skill",
                    "original_skill_path": None,
                }
            )
        return result

    @staticmethod
    def _minimum_stars(
        candidate: dict[str, Any], github_min: int, openclaw_min: int
    ) -> int:
        channel = candidate.get("channel")
        if channel in {"github", "github_live"} or "github.com" in candidate.get(
            "source_url", ""
        ):
            return github_min
        if channel == "openclaw_hub" or "clawhub.ai" in candidate.get(
            "source_url", ""
        ):
            return openclaw_min
        return 0

    @staticmethod
    def _license_decision(license_name: str) -> tuple[str, str]:
        if license_name in PERMISSIVE_LICENSES:
            return "adapt_allowed", "宽松许可证，可在保留声明后制作适配层"
        if license_name.startswith("GPL"):
            return "external_process_only", "copyleft 组件仅作为独立进程调用"
        if "NC" in license_name or license_name in {"Proprietary", "NOASSERTION", ""}:
            return "reject", "非商业、专有或许可证不明确，禁止复制改造"
        return "review_required", "许可证不在自动允许列表，需法律审查"

    @staticmethod
    def _match_score(candidate: dict[str, Any], requirements: dict) -> float:
        haystack = " ".join(
            str(candidate.get(key, "")).lower()
            for key in ("name", "description", "capability")
        )
        terms = re.findall(
            r"[a-z0-9_-]+|[\u3400-\u9fff]{2,}",
            (
                requirements["topic"] + " "
                + requirements["deliverable"]["type"]
                + " research academic data chart report"
            ).lower(),
        )
        keyword_score = sum(term in haystack for term in set(terms))
        stars = candidate.get("stars")
        adoption = math.log10(max(1, int(stars or 0)) + 1)
        return round(keyword_score * 2 + adoption, 3)

    @staticmethod
    def _adapt(candidate: dict[str, Any]) -> dict[str, Any]:
        canonical_name = "external_" + re.sub(
            r"[^a-z0-9_]+", "_", candidate["name"].lower().replace("-", "_")
        ).strip("_")
        attribution = {
            field: candidate[field] for field in REQUIRED_PROVENANCE_FIELDS
        }
        modifications = [
            "包装为 SkillRequest -> SkillResult 标准接口",
            "移除隐式会话状态，所有输入改为显式参数",
            "增加超时、错误分类、幂等与审计元数据",
            "输出统一 artifact_type，并接入 DAG 质量卡口",
            "保留原许可证和作者/来源声明，不复制不需要的原实现",
        ]
        skill_md = (
            f"---\nname: {canonical_name}\n"
            f"description: Adapter for {candidate['name']}\n"
            f"license: {candidate['license']}\nversion: adapted-1.0.0\n---\n\n"
            f"# {canonical_name}\n\n"
            f"Original source: {candidate['source_url']}\n\n"
            f"Original author: {candidate['author']}\n\n"
            f"Original version: {candidate['version']}\n\n"
            "## Modifications\n"
            + "\n".join(f"- {item}" for item in modifications)
            + "\n"
        )
        return {
            "name": canonical_name,
            "capability": candidate["capability"],
            "attribution": attribution,
            "modifications": modifications,
            "skill_md": skill_md,
            "installation_status": "pending_human_review",
        }

    def validate(self, result: SkillResult) -> None:
        super().validate(result)
        payload = json.loads(result.content)
        for candidate in payload.get("candidates", []):
            missing = REQUIRED_PROVENANCE_FIELDS - candidate.keys()
            if missing:
                raise ValueError(f"第三方 Skill 缺少溯源字段: {sorted(missing)}")
            if candidate["decision"] == "adapt_allowed" and (
                candidate["license"] not in PERMISSIVE_LICENSES
            ):
                raise ValueError("非宽松许可证候选被错误批准改造")
