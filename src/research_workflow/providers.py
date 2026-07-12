"""Optional production source providers using standard-library HTTP."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from collections.abc import Iterable
from typing import Any

from .contracts import SourceRetriever


class CompositeSourceRetriever(SourceRetriever):
    """Fan out a category request to configured providers and deduplicate."""

    def __init__(self, providers: Iterable[SourceRetriever]) -> None:
        self.providers = tuple(providers)
        self.last_errors: list[dict[str, str]] = []

    def retrieve(self, *, topic, questions, categories):
        self.last_errors = []
        sources = []
        for provider in self.providers:
            try:
                sources.extend(
                    provider.retrieve(
                        topic=topic, questions=questions, categories=categories
                    )
                )
            except Exception as exc:
                self.last_errors.append(
                    {
                        "provider": type(provider).__name__,
                        "error": str(exc),
                    }
                )
        deduplicated = {}
        for source in sources:
            key = str(source.get("url") or source.get("id"))
            deduplicated[key] = source
        if not deduplicated and self.last_errors:
            raise RuntimeError(json.dumps(self.last_errors, ensure_ascii=False))
        return list(deduplicated.values())


class OpenAlexRetriever(SourceRetriever):
    """No-key academic provider for OpenAlex works metadata."""

    def __init__(
        self,
        *,
        max_results: int = 20,
        timeout: int = 15,
        mailto: str | None = None,
    ) -> None:
        self.max_results = max_results
        self.timeout = timeout
        self.mailto = mailto

    def retrieve(self, *, topic, questions, categories):
        if "academic" not in categories:
            return []
        query = " ".join((topic, *questions[:3]))
        params = {
            "search": query,
            "per-page": str(self.max_results),
            "sort": "relevance_score:desc",
        }
        if self.mailto:
            params["mailto"] = self.mailto
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "northstar-research-workflow/1.0",
            },
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return [self._normalize(item) for item in payload.get("results", [])]

    @classmethod
    def _normalize(cls, item: dict[str, Any]) -> dict[str, Any]:
        ids = item.get("ids", {})
        primary = item.get("primary_location") or {}
        source = primary.get("source") or {}
        doi = item.get("doi") or ids.get("doi")
        return {
            "id": item.get("id") or doi,
            "title": item.get("display_name") or "Untitled work",
            "category": "academic",
            "source_type": "independent",
            "url": doi or primary.get("landing_page_url") or item.get("id"),
            "published_at": item.get("publication_date")
            or item.get("publication_year"),
            "content": cls._abstract(item.get("abstract_inverted_index")),
            "venue": source.get("display_name"),
            "doi": doi,
            "citation_count": item.get("cited_by_count"),
            "peer_reviewed": item.get("type") not in {"preprint"},
            "issue_ids": [],
        }

    @staticmethod
    def _abstract(inverted: dict[str, list[int]] | None) -> str:
        if not inverted:
            return ""
        positions = [
            (position, word)
            for word, indexes in inverted.items()
            for position in indexes
        ]
        return " ".join(word for _, word in sorted(positions))
