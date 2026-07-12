"""Inline citations, canonical bibliography and bidirectional anchors."""

from __future__ import annotations

import json
import re

from ..contracts import Skill
from ..models import SkillRequest, SkillResult


class CitationManagementSkill(Skill):
    name = "citation_management"

    def execute(self, request: SkillRequest) -> SkillResult:
        draft = request.inputs["writing"]
        evidence = json.loads(request.inputs["evidence_governance"])
        style = str(request.config.extra.get("citation_style", "gbt7714")).lower()
        content = draft
        references = []
        missing = []
        citation_count = 0
        for index, source in enumerate(evidence.get("sources", []), 1):
            source_id = str(source.get("id", f"S{index}"))
            safe_id = re.sub(r"[^A-Za-z0-9_-]", "-", source_id)
            url = source.get("original_url")
            if not url:
                missing.append(source_id)
                continue
            anchors = []
            escaped_url = re.escape(str(url))
            markdown_pattern = re.compile(
                rf"\[([^\]]+)\]\({escaped_url}\)"
            )

            def replace_markdown(match):
                nonlocal citation_count
                citation_count += 1
                anchor = f"cite-{safe_id}-{len(anchors) + 1}"
                anchors.append(anchor)
                return (
                    f'<a id="{anchor}"></a>'
                    f"[{match.group(1)}]({url}) "
                    f"[[{index}]](#ref-{safe_id})"
                )

            content, replaced = markdown_pattern.subn(
                replace_markdown, content
            )
            if replaced == 0 and str(url) in content:
                anchor = f"cite-{safe_id}-1"
                anchors.append(anchor)
                citation_count += 1
                content = content.replace(
                    str(url),
                    f'<a id="{anchor}"></a>[{index}]({url})',
                    1,
                )
            if not anchors:
                missing.append(source_id)
            backlinks = " ".join(
                f"[↩{position}](#{anchor})"
                for position, anchor in enumerate(anchors, 1)
            )
            references.append(
                {
                    "number": index,
                    "source_id": source_id,
                    "anchor": f"ref-{safe_id}",
                    "formatted": self._format_reference(source, style),
                    "backlinks": backlinks,
                    "citation_anchors": anchors,
                }
            )
        heading = (
            "## 统一参考资料"
            if re.search(r"(?m)^##\s+参考", content)
            else "## 参考资料"
        )
        bibliography = [heading]
        for reference in references:
            bibliography.append(
                f'<a id="{reference["anchor"]}"></a>'
                f'[{reference["number"]}] {reference["formatted"]} '
                f'{reference["backlinks"]}'.rstrip()
            )
        cited_content = content.rstrip() + "\n\n" + "\n\n".join(bibliography) + "\n"
        source_count = len(evidence.get("sources", []))
        payload_metadata = {
            "citation_style": style,
            "source_count": source_count,
            "reference_count": len(references),
            "citation_count": citation_count,
            "missing_inline_source_ids": missing,
            "coverage": (
                (source_count - len(missing)) / source_count
                if source_count else 0.0
            ),
            "bidirectional_links": True,
        }
        return SkillResult(
            cited_content,
            "cited_draft",
            payload_metadata,
        )

    @staticmethod
    def _format_reference(source: dict, style: str) -> str:
        author = source.get("author") or source.get("title") or "Unknown"
        title = source.get("title") or "Untitled"
        year = str(source.get("published_at") or "n.d.")[:4]
        url = source.get("original_url") or ""
        if style == "apa":
            return f"{author}. ({year}). *{title}*. {url}"
        if style == "mla":
            return f'{author}. "{title}." {year}, {url}.'
        if style == "chicago":
            return f'{author}. "{title}." Accessed {year}. {url}.'
        return f"{author}. {title}[EB/OL]. {year}. {url}"

    def validate(self, result: SkillResult) -> None:
        super().validate(result)
        if "## 参考资料" not in result.content and "## 统一参考资料" not in result.content:
            raise ValueError("引用管理必须生成文末参考资料")
