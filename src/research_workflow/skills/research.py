"""Topic decomposition and evidence packaging skill."""

from __future__ import annotations

import json
from typing import Any

from ..contracts import Skill, SourceRetriever, TextGenerator
from ..models import SkillRequest, SkillResult
from ..prompts import RESEARCH_PROMPT


class ResearchSkill(Skill):
    name = "research"

    REQUIRED_CATEGORIES = ("official", "academic", "social_media")

    def __init__(
        self,
        generator: TextGenerator | None = None,
        retriever: SourceRetriever | None = None,
    ) -> None:
        self.generator = generator
        self.retriever = retriever

    def execute(self, request: SkillRequest) -> SkillResult:
        requirements = json.loads(request.inputs["requirements_analysis"])
        issue_tree = json.loads(request.inputs["issue_tree"])
        outline = json.loads(request.inputs["outline"])
        questions = tuple(
            item.get("question", "") for item in issue_tree.get("issues", [])
            if item.get("included", True)
        )
        raw_sources = list(request.config.extra.get("sources", []))
        if self.retriever:
            raw_sources.extend(
                self.retriever.retrieve(
                    topic=request.config.topic,
                    questions=questions,
                    categories=self.REQUIRED_CATEGORIES,
                )
            )
        sources = self._normalize_sources(raw_sources)
        prompt = RESEARCH_PROMPT.format(topic=request.config.topic)
        if self.generator:
            prompt += (
                f"\n需求简报：{json.dumps(requirements, ensure_ascii=False)}"
                f"\n议题树：{json.dumps(issue_tree, ensure_ascii=False)}"
                f"\n已确认大纲：{json.dumps(outline, ensure_ascii=False)}"
                f"\n检索候选：{json.dumps(sources, ensure_ascii=False)}"
            )
            content = self.generator.generate(
                system="你是严谨的研究员。不得虚构来源。", prompt=prompt, max_tokens=4000
            )
            return SkillResult(content, "evidence_pack", {"prompt_version": "1.0"})

        present_categories = sorted(
            {source["category"] for source in sources if source["category"] != "unknown"}
        )
        missing_categories = [
            category for category in self.REQUIRED_CATEGORIES
            if category not in present_categories
        ]
        payload = {
            "topic": request.config.topic,
            "research_questions": [
                {"id": item.get("id"), "question": item.get("question")}
                for item in issue_tree.get("issues", []) if item.get("included", True)
            ],
            "sources": sources,
            "outline_sections": [
                {"id": item.get("id"), "title": item.get("title")}
                for item in outline.get("sections", [])
            ],
            "retrieval_summary": {
                "required_categories": list(self.REQUIRED_CATEGORIES),
                "present_categories": present_categories,
                "missing_categories": missing_categories,
                "external_retriever_used": self.retriever is not None,
            },
            "evidence_gaps": (
                [f"缺少来源类别：{category}" for category in missing_categories]
                if missing_categories else []
            ),
            "feedback_applied": list(request.feedback),
        }
        return SkillResult(
            json.dumps(payload, ensure_ascii=False, indent=2),
            "evidence_pack",
            {
                "source_count": len(sources),
                "source_category_count": len(present_categories),
                "requires_external_retrieval": bool(missing_categories),
            },
        )

    @classmethod
    def _normalize_sources(cls, raw_sources: list[Any]) -> list[dict[str, Any]]:
        aliases = {
            "government": "official", "primary": "official", "official": "official",
            "paper": "academic", "journal": "academic", "academic": "academic",
            "social": "social_media", "social_media": "social_media",
            "mainstream_social": "social_media",
        }
        sources: list[dict[str, Any]] = []
        seen: set[str] = set()
        for index, source in enumerate(raw_sources):
            if isinstance(source, str):
                normalized: dict[str, Any] = {
                    "id": f"S{index + 1}", "title": source, "content": source,
                    "category": "unknown",
                }
            elif isinstance(source, dict):
                normalized = dict(source)
                normalized.setdefault("id", f"S{index + 1}")
                normalized.setdefault("title", f"资料 {index + 1}")
                category = str(
                    normalized.get("category", normalized.get("source_type", "unknown"))
                ).lower()
                normalized["category"] = aliases.get(category, category)
            else:
                continue
            key = str(normalized.get("url") or normalized["id"])
            if key in seen:
                continue
            seen.add(key)
            sources.append(normalized)
        return sources

    def validate(self, result: SkillResult) -> None:
        super().validate(result)
        payload = json.loads(result.content)
        if not {"sources", "research_questions", "retrieval_summary"} <= payload.keys():
            raise ValueError("evidence_pack 缺少必要调研字段")
