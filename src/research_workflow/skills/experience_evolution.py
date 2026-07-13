"""Extract reusable lessons and stage validated skill-document proposals."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from datetime import UTC, datetime

from ..contracts import Skill
from ..models import SkillRequest, SkillResult


class ExperienceEvolutionSkill(Skill):
    name = "experience_evolution"

    ROUTES = {
        "outline": ("大纲", "章节", "比例", "摘要"),
        "research": ("来源", "检索", "社媒", "论文", "数据"),
        "data_processing": ("评分", "claim", "交叉验证", "证据等级"),
        "visualization": ("图表", "可视化", "流程图"),
        "writing_standards": (
            "写作规范", "写作标准", "模板", "触发词", "文体", "券商",
            "蓝v", "公文格式", "公式排版",
        ),
        "writing": ("写作", "文风", "段落", "风险", "引用"),
        "citation_management": ("引用", "参考文献", "脚注", "格式"),
        "formatting": ("飞书", "word", "pdf", "网页", "排版"),
        "quality_gate": ("质量门", "复核", "校验", "红线"),
        "research_report_orchestrator": ("流程", "确认", "工作流", "节点"),
    }

    def execute(self, request: SkillRequest) -> SkillResult:
        operations = json.loads(request.inputs["_user_operations"])
        quality = json.loads(request.inputs["quality_gate"])
        lessons = []
        for operation in operations:
            if operation.get("operation") not in {
                "modify", "comment", "route_revision", "update_sources"
            }:
                continue
            payload = operation.get("payload", {})
            text = str(
                payload.get("feedback")
                or payload.get("comment")
                or payload.get("reason")
                or ""
            ).strip()
            if not text:
                continue
            normalized = re.sub(r"\s+", "", text.lower())
            target = self._route(text)
            fingerprint = hashlib.sha256(
                f"{target}:{normalized}".encode("utf-8")
            ).hexdigest()[:16]
            lessons.append(
                {
                    "fingerprint": fingerprint,
                    "target_skill": target,
                    "text": text,
                    "actor_id": payload.get("actor_id"),
                    "operation": operation.get("operation"),
                    "created_at": operation.get("created_at"),
                    "general_signal": any(
                        marker in text
                        for marker in ("每次", "以后", "默认", "所有", "通用", "应该")
                    ),
                }
            )
        frequencies = Counter(item["fingerprint"] for item in lessons)
        proposals = []
        for item in {entry["fingerprint"]: entry for entry in lessons}.values():
            frequency = frequencies[item["fingerprint"]]
            validated = (
                quality.get("passed", False)
                and (frequency >= 2 or item["general_signal"])
            )
            confidence = min(
                0.95,
                0.4 + frequency * 0.15
                + (0.2 if item["general_signal"] else 0.0)
                + (0.1 if quality.get("passed") else 0.0),
            )
            proposals.append(
                {
                    "id": f"LEARN-{item['fingerprint']}",
                    "target_skill": item["target_skill"],
                    "rule": item["text"],
                    "frequency": frequency,
                    "confidence": round(confidence, 2),
                    "status": (
                        "validated_candidate" if validated
                        else "pending_validation"
                    ),
                    "evidence_operations": [
                        lesson["operation"] for lesson in lessons
                        if lesson["fingerprint"] == item["fingerprint"]
                    ],
                    "requires_human_approval": True,
                }
            )
        now = datetime.now(UTC)
        quarter = (now.month - 1) // 3 + 1
        payload = {
            "period": f"{now.year}-Q{quarter}",
            "interaction_count": len(operations),
            "lesson_count": len(lessons),
            "proposals": sorted(
                proposals,
                key=lambda item: (item["status"], item["confidence"]),
                reverse=True,
            ),
            "effectiveness": {
                "quality_passed": quality.get("passed", False),
                "quality_score": quality.get("total_score"),
                "validated_candidate_count": sum(
                    item["status"] == "validated_candidate"
                    for item in proposals
                ),
                "pending_count": sum(
                    item["status"] == "pending_validation"
                    for item in proposals
                ),
            },
            "policy": {
                "automatic_repo_write": False,
                "human_approval_required": True,
                "managed_section_only": True,
                "quarterly_review_required": True,
            },
        }
        return SkillResult(
            json.dumps(payload, ensure_ascii=False, indent=2),
            "evolution_report",
            payload["effectiveness"],
        )

    @classmethod
    def _route(cls, text: str) -> str:
        scores = {
            skill: sum(keyword in text.lower() for keyword in keywords)
            for skill, keywords in cls.ROUTES.items()
        }
        return max(scores, key=scores.get) if max(scores.values(), default=0) else "research_report_orchestrator"
