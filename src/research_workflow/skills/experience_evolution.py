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
        "evidence_pipeline": (
            "来源快照", "网页快照", "内容哈希", "抓取时间",
            "证据治理", "可追溯", "利益相关方", "证据红线",
        ),
        "data_processing": (
            "评分", "claim", "交叉验证", "证据等级",
            "论断验证", "原文片段", "数字核验", "证据对齐", "冲突仲裁",
        ),
        "compose": (
            "素材", "图表", "可视化", "写作", "引用", "内容优化", "压力测试",
        ),
        "writing_standards": (
            "写作规范", "写作标准", "模板", "触发词", "文体", "券商",
            "蓝v", "公文格式", "公式排版", "技能研究",
        ),
        "formatting": ("飞书", "word", "pdf", "网页", "排版"),
        "quality_assurance": ("质量门", "复核", "校验", "红线", "量化", "回测"),
        "research_report_orchestrator": ("流程", "确认", "工作流", "节点"),
    }

    @staticmethod
    def applicable(request: SkillRequest) -> bool:
        operations = json.loads(request.inputs.get("_user_operations", "[]"))
        return any(
            operation.get("operation")
            in {"modify", "comment", "route_revision", "update_sources"}
            for operation in operations
        )

    def execute(self, request: SkillRequest) -> SkillResult:
        if not self.applicable(request):
            payload = {
                "period": None,
                "interaction_count": 0,
                "lesson_count": 0,
                "proposals": [],
                "status": "not_applicable",
                "reason": "无修改/评论/修订操作，跳过经验沉淀",
                "feedback_applied": list(request.feedback),
            }
            return SkillResult(
                json.dumps(payload, ensure_ascii=False, indent=2),
                "experience_evolution",
                {"applicable": False, "status": "not_applicable"},
            )
        operations = json.loads(request.inputs["_user_operations"])
        if "quality_gate" in request.inputs:
            quality = json.loads(request.inputs["quality_gate"])
        else:
            quality = json.loads(request.inputs["quality_assurance"])["quality_gate"]
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
