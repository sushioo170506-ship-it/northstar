"""Topic decomposition and evidence packaging skill."""

from __future__ import annotations

import json
from typing import Any

from ..contracts import Skill, TextGenerator
from ..models import SkillRequest, SkillResult
from ..prompts import RESEARCH_PROMPT


class ResearchSkill(Skill):
    name = "research"

    def __init__(self, generator: TextGenerator | None = None) -> None:
        self.generator = generator

    def execute(self, request: SkillRequest) -> SkillResult:
        prompt = RESEARCH_PROMPT.format(topic=request.config.topic)
        if self.generator:
            content = self.generator.generate(
                system="你是严谨的研究员。不得虚构来源。", prompt=prompt, max_tokens=4000
            )
            return SkillResult(content, "evidence_pack", {"prompt_version": "1.0"})

        raw_sources = request.config.extra.get("sources", [])
        sources: list[dict[str, Any]] = []
        for index, source in enumerate(raw_sources):
            if isinstance(source, str):
                sources.append({"id": f"S{index + 1}", "title": source, "content": source})
            elif isinstance(source, dict):
                normalized = dict(source)
                normalized.setdefault("id", f"S{index + 1}")
                normalized.setdefault("title", f"资料 {index + 1}")
                sources.append(normalized)
        dimensions = [
            "概念与范围", "现状与驱动因素", "关键机制与证据", "风险与局限", "结论与建议"
        ]
        payload = {
            "topic": request.config.topic,
            "research_questions": [
                {"id": f"RQ{i + 1}", "question": f"{request.config.topic}：{dimension}是什么？"}
                for i, dimension in enumerate(dimensions)
            ],
            "sources": sources,
            "evidence_gaps": [] if sources else ["未提供可核验资料，需要外部检索适配器补充来源"],
            "feedback_applied": list(request.feedback),
        }
        return SkillResult(
            json.dumps(payload, ensure_ascii=False, indent=2),
            "evidence_pack",
            {"source_count": len(sources), "requires_external_retrieval": not bool(sources)},
        )
