"""Deterministic structural optimization for diagrams, tables, lists, and links."""

from __future__ import annotations

import json
import re
from urllib.parse import urlparse

from ..contracts import Skill
from ..models import SkillRequest, SkillResult
from ..renderers import MarkdownTableParser


class ContentOptimizationSkill(Skill):
    name = "content_optimization"
    version = "1.0.0"

    FLOW_FENCE = re.compile(r"```(?:text|txt)\s*\n(.*?)```", re.DOTALL)
    LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")

    def execute(self, request: SkillRequest) -> SkillResult:
        content = request.inputs["citation_management"]
        content, flow_count = self._convert_flows(content)
        content, table_count = self._explain_tables(content)
        content, renumbered = self._normalize_numbering(content)
        content, link_count = self._append_link_index(content)
        payload = {
            "flow_diagrams_converted": flow_count,
            "tables_explained": table_count,
            "list_items_renumbered": renumbered,
            "link_index_count": link_count,
        }
        return SkillResult(
            content,
            "optimized_draft",
            {**payload, "feedback_applied": list(request.feedback)},
        )

    @classmethod
    def _convert_flows(cls, content: str) -> tuple[str, int]:
        count = 0

        def replace(match: re.Match[str]) -> str:
            nonlocal count
            body = match.group(1).strip()
            if not re.search(r"(?:→|⇄|<->|->|↓|\n\s*[vV]\s*\n)", body):
                return match.group(0)
            mermaid = cls._flow_to_mermaid(body)
            if not mermaid:
                return match.group(0)
            count += 1
            return f"```mermaid\n{mermaid}\n```"

        return cls.FLOW_FENCE.sub(replace, content), count

    @staticmethod
    def _flow_to_mermaid(body: str) -> str:
        nodes: dict[str, str] = {}
        edges: list[tuple[str, str, str]] = []
        previous_tail: str | None = None
        vertical_pending = False

        def node(label: str) -> str:
            clean = " ".join(label.strip().strip(":：").split())
            if not clean:
                return ""
            if clean not in nodes:
                nodes[clean] = f"N{len(nodes) + 1}"
            return nodes[clean]

        for raw in body.splitlines():
            line = raw.strip()
            if not line:
                continue
            if line.lower() in {"v", "↓"}:
                vertical_pending = True
                continue
            parts = re.split(r"\s*(⇄|<->|→|->)\s*", line)
            labels = parts[::2]
            operators = parts[1::2]
            if len(labels) == 1:
                current = node(labels[0])
                if current and vertical_pending and previous_tail:
                    edges.append((previous_tail, current, ""))
                previous_tail = current or previous_tail
                vertical_pending = False
                continue
            ids = [node(label) for label in labels]
            if vertical_pending and previous_tail and ids[0]:
                edges.append((previous_tail, ids[0], ""))
            for index, operator in enumerate(operators):
                if not ids[index] or not ids[index + 1]:
                    continue
                if operator in {"⇄", "<->"}:
                    edges.append((ids[index], ids[index + 1], "双向"))
                    edges.append((ids[index + 1], ids[index], ""))
                else:
                    edges.append((ids[index], ids[index + 1], ""))
            previous_tail = ids[-1] if ids else previous_tail
            vertical_pending = False
        if len(nodes) < 2 or not edges:
            return ""
        lines = ["flowchart TD"]
        lines.extend(
            f'    {identifier}["{label.replace(chr(34), chr(39))}"]'
            for label, identifier in nodes.items()
        )
        lines.extend(
            f"    {left} -->"
            + (f"|{label}| " if label else " ")
            + right
            for left, right, label in edges
        )
        return "\n".join(lines)

    @classmethod
    def _explain_tables(cls, content: str) -> tuple[str, int]:
        lines = content.splitlines()
        output: list[str] = []
        index = 0
        count = 0
        while index < len(lines):
            if (
                index + 1 < len(lines)
                and "|" in lines[index]
                and MarkdownTableParser._cells(lines[index])
                and all(
                    MarkdownTableParser.SEPARATOR.fullmatch(cell.strip())
                    for cell in MarkdownTableParser._cells(lines[index + 1])
                )
            ):
                start = index
                headers = MarkdownTableParser._cells(lines[index])
                index += 2
                row_count = 0
                while index < len(lines):
                    cells = MarkdownTableParser._cells(lines[index])
                    if len(cells) != len(headers):
                        break
                    row_count += 1
                    index += 1
                output.extend(lines[start:index])
                following = "\n".join(lines[index:index + 3])
                if "**表格说明：**" not in following:
                    header_text = "、".join(
                        MarkdownTableParser._clean(item) for item in headers
                    )
                    output.extend(
                        [
                            "",
                            (
                                f"> **表格说明：** 本表以“{header_text}”为字段，"
                                f"共整理{row_count}条记录。指标定义以表头、单位和"
                                "同一统计口径为准；核心结论应依据同列横向比较、"
                                "同行关联及表内来源推导，不得脱离原表外推。"
                            ),
                        ]
                    )
                    count += 1
                continue
            output.append(lines[index])
            index += 1
        return "\n".join(output).rstrip() + "\n", count

    @staticmethod
    def _normalize_numbering(content: str) -> tuple[str, int]:
        counters: dict[int, int] = {}
        output = []
        changed = 0
        in_fence = False
        for line in content.splitlines():
            if line.startswith("```"):
                in_fence = not in_fence
                output.append(line)
                continue
            if not in_fence and re.match(r"^#{1,6}\s", line):
                counters.clear()
                output.append(line)
                continue
            match = None if in_fence else re.match(r"^(\s*)(\d+)[.)、]\s+(.+)$", line)
            if not match:
                output.append(line)
                continue
            indent = len(match.group(1).replace("\t", "    "))
            counters[indent] = counters.get(indent, 0) + 1
            for level in list(counters):
                if level > indent:
                    del counters[level]
            number = counters[indent]
            replacement = f"{match.group(1)}{number}. {match.group(3)}"
            if replacement != line:
                changed += 1
            output.append(replacement)
        return "\n".join(output).rstrip() + "\n", changed

    @classmethod
    def _append_link_index(cls, content: str) -> tuple[str, int]:
        base = re.split(r"(?m)^##\s+全量关联链接\s*$", content, maxsplit=1)[0].rstrip()
        links: list[tuple[str, str]] = []
        seen: set[str] = set()
        for label, url in cls.LINK.findall(base):
            if url in seen or url.startswith("#"):
                continue
            seen.add(url)
            clean_label = re.sub(r"<[^>]+>|\*\*|`", "", label).strip()
            links.append((clean_label or urlparse(url).netloc, url))
        if not links:
            return base + "\n", 0
        index = ["## 全量关联链接", ""]
        index.extend(
            f"{position}. [{label}]({url})"
            for position, (label, url) in enumerate(links, 1)
        )
        return base + "\n\n" + "\n".join(index) + "\n", len(links)

    def validate(self, result: SkillResult) -> None:
        super().validate(result)
        if re.search(r"(?m)^1\.\s.+\n1\.\s", result.content):
            raise ValueError("content_optimization 仍存在连续重复编号")
        tables = sum(
            kind == "table"
            for kind, _ in MarkdownTableParser.split_document(result.content)
        )
        if result.content.count("> **表格说明：**") < tables:
            raise ValueError("每张Markdown表格后必须有专属表格说明")
        if self.LINK.search(result.content) and "## 全量关联链接" not in result.content:
            raise ValueError("存在链接时必须生成全量关联链接索引")
