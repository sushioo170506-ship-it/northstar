"""Topic decomposition and evidence packaging skill."""

from __future__ import annotations

import json
import hashlib
import re
from typing import Any

from ..contracts import Skill, SourceRetriever, TextGenerator
from ..models import SkillRequest, SkillResult
from ..prompts import RESEARCH_PROMPT


class ResearchSkill(Skill):
    name = "research"

    REQUIRED_CATEGORIES = ("industry", "academic", "social_media")
    DEFAULT_SOCIAL_PLATFORMS = (
        "wechat_official_account", "weibo", "zhihu", "xiaohongshu",
        "bilibili", "xueqiu", "reddit", "hacker_news", "x",
        "linkedin", "youtube", "bluesky", "mastodon",
    )

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
        standards = json.loads(request.inputs.get("writing_standards", "{}"))
        scene_categories = {
            "technical": ("academic",),
            "industry_investment": ("industry", "academic"),
            "public_account": ("industry", "social_media"),
            "official_internal": ("industry",),
        }
        required_categories = scene_categories.get(
            standards.get("scene"), self.REQUIRED_CATEGORIES
        )
        questions = tuple(
            item.get("question", "") for item in issue_tree.get("issues", [])
            if item.get("included", True)
        )
        raw_sources = list(request.config.extra.get("sources", []))
        retrieval_errors: dict[str, str] = {}
        if self.retriever:
            for category in required_categories:
                try:
                    raw_sources.extend(
                        self.retriever.retrieve(
                            topic=request.config.topic,
                            questions=questions,
                            categories=(category,),
                        )
                    )
                except Exception as exc:
                    retrieval_errors[category] = str(exc)
        sources = self._normalize_sources(raw_sources)
        prompt = RESEARCH_PROMPT.format(topic=request.config.topic)
        model_analysis = None
        if self.generator:
            prompt += (
                f"\n需求简报：{json.dumps(requirements, ensure_ascii=False)}"
                f"\n议题树：{json.dumps(issue_tree, ensure_ascii=False)}"
                f"\n已确认大纲：{json.dumps(outline, ensure_ascii=False)}"
                f"\n检索候选：{json.dumps(sources, ensure_ascii=False)}"
            )
            generated = self.generator.generate(
                system="你是严谨的研究员。不得虚构来源。", prompt=prompt, max_tokens=4000
            )
            try:
                model_analysis = json.loads(generated)
            except json.JSONDecodeError:
                model_analysis = {"raw": generated, "parse_error": True}

        present_categories = sorted(
            {source["category"] for source in sources if source["category"] != "unknown"}
        )
        missing_categories = [
            category for category in required_categories
            if category not in present_categories
        ]
        social_platforms = sorted(
            {
                source.get("platform")
                for source in sources
                if source.get("category") == "social_media"
                and source.get("platform")
            }
        )
        social_feedback = self._social_feedback(sources)
        pass_status = {
            category: {
                "status": (
                    "error" if category in retrieval_errors
                    else "completed" if category in present_categories
                    else "missing"
                ),
                "source_count": sum(
                    source["category"] == category for source in sources
                ),
                "error": retrieval_errors.get(category),
            }
            for category in required_categories
        }
        payload = {
            "topic": request.config.topic,
            "research_questions": [
                {"id": item.get("id"), "question": item.get("question")}
                for item in issue_tree.get("issues", []) if item.get("included", True)
            ],
            "sources": sources,
            "social_feedback": social_feedback,
            "outline_sections": [
                {"id": item.get("id"), "title": item.get("title")}
                for item in outline.get("sections", [])
            ],
            "retrieval_summary": {
                "required_categories": list(required_categories),
                "present_categories": present_categories,
                "missing_categories": missing_categories,
                "external_retriever_used": self.retriever is not None,
                "passes": pass_status,
                "requested_social_platforms": list(
                    request.config.extra.get(
                        "social_platforms", self.DEFAULT_SOCIAL_PLATFORMS
                    )
                ),
                "present_social_platforms": social_platforms,
            },
            "evidence_gaps": (
                [f"缺少来源类别：{category}" for category in missing_categories]
                if missing_categories else []
            ),
            "model_analysis": model_analysis,
            "feedback_applied": list(request.feedback),
        }
        return SkillResult(
            json.dumps(payload, ensure_ascii=False, indent=2),
            "evidence_pack",
            {
                "source_count": len(sources),
                "source_category_count": len(present_categories),
                "requires_external_retrieval": bool(missing_categories),
                "prompt_version": "1.0" if self.generator else None,
                "social_feedback_count": social_feedback["metrics"][
                    "deduplicated_count"
                ],
                "social_satisfaction": social_feedback["metrics"][
                    "satisfaction_ratio"
                ],
            },
        )

    @classmethod
    def _normalize_sources(cls, raw_sources: list[Any]) -> list[dict[str, Any]]:
        aliases = {
            "government": "industry", "primary": "industry", "official": "industry",
            "commercial": "industry", "industry": "industry",
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
                if normalized["category"] == "social_media":
                    normalized["platform"] = normalized.get(
                        "platform"
                    ) or cls._infer_social_platform(
                        str(normalized.get("url", ""))
                    )
            else:
                continue
            key = str(normalized.get("url") or normalized["id"])
            if key in seen:
                continue
            seen.add(key)
            sources.append(normalized)
        return sources

    @staticmethod
    def _infer_social_platform(url: str) -> str:
        hosts = {
            "mp.weixin.qq.com": "wechat_official_account",
            "weibo.com": "weibo",
            "zhihu.com": "zhihu",
            "xiaohongshu.com": "xiaohongshu",
            "bilibili.com": "bilibili",
            "xueqiu.com": "xueqiu",
            "reddit.com": "reddit",
            "news.ycombinator.com": "hacker_news",
            "x.com": "x",
            "twitter.com": "x",
            "linkedin.com": "linkedin",
            "youtube.com": "youtube",
            "bsky.app": "bluesky",
        }
        for host, platform in hosts.items():
            if host in url:
                return platform
        return "other_social"

    @classmethod
    def _social_feedback(cls, sources: list[dict[str, Any]]) -> dict[str, Any]:
        positive = {
            "好", "优秀", "稳定", "满意", "推荐", "提升", "快", "准确",
            "useful", "good", "great", "excellent", "stable", "recommend",
        }
        negative = {
            "差", "失败", "不稳定", "失望", "错误", "慢", "崩溃", "贵",
            "bad", "poor", "fail", "unstable", "slow", "error", "expensive",
        }
        seen: set[str] = set()
        items = []
        raw_count = 0
        duplicate_count = 0
        for source in sources:
            if source.get("category") != "social_media":
                continue
            raw_count += 1
            content = re.sub(r"\s+", " ", str(source.get("content", ""))).strip()
            normalized = re.sub(r"[^\w\u3400-\u9fff]+", "", content.lower())
            fingerprint = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
            if fingerprint in seen:
                duplicate_count += 1
                continue
            seen.add(fingerprint)
            lower = content.lower()
            positive_hits = sum(token in lower for token in positive)
            negative_hits = sum(token in lower for token in negative)
            sentiment = (
                "positive" if positive_hits > negative_hits
                else "negative" if negative_hits > positive_hits
                else "neutral"
            )
            items.append(
                {
                    "id": source.get("id"),
                    "platform": source.get("platform", "other_social"),
                    "author": source.get("author") or source.get("account"),
                    "published_at": source.get("published_at"),
                    "url": source.get("url"),
                    "content": content,
                    "fingerprint": fingerprint,
                    "sentiment": sentiment,
                    "positive_hits": positive_hits,
                    "negative_hits": negative_hits,
                    "traceable": bool(source.get("url")),
                }
            )
        counts = {
            sentiment: sum(item["sentiment"] == sentiment for item in items)
            for sentiment in ("positive", "negative", "neutral")
        }
        polar = counts["positive"] + counts["negative"]
        return {
            "items": items,
            "platforms": sorted({item["platform"] for item in items}),
            "sentiment_counts": counts,
            "metrics": {
                "raw_count": raw_count,
                "deduplicated_count": len(items),
                "duplicate_count": duplicate_count,
                "traceable_count": sum(item["traceable"] for item in items),
                "traceability_ratio": (
                    sum(item["traceable"] for item in items) / len(items)
                    if items else 0.0
                ),
                "satisfaction_ratio": (
                    counts["positive"] / polar if polar else None
                ),
            },
            "method": {
                "sentiment": "deterministic bilingual lexicon baseline",
                "limitation": (
                    "讽刺、转述和领域语境可能误判；满意度只代表有明确极性的去重样本"
                ),
            },
        }

    def validate(self, result: SkillResult) -> None:
        super().validate(result)
        payload = json.loads(result.content)
        if not {"sources", "research_questions", "retrieval_summary"} <= payload.keys():
            raise ValueError("evidence_pack 缺少必要调研字段")
