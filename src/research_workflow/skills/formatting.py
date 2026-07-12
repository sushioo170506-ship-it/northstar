"""Formatting and style-normalization skill."""

from __future__ import annotations

import html
import json
import re

from ..contracts import Skill, TextGenerator
from ..models import SkillRequest, SkillResult
from ..prompts import FORMAT_PROMPT


class FormattingSkill(Skill):
    name = "formatting"

    def __init__(self, generator: TextGenerator | None = None) -> None:
        self.generator = generator

    def execute(self, request: SkillRequest) -> SkillResult:
        draft = request.inputs["writing"]
        prompt = FORMAT_PROMPT.format(
            output_format=request.config.output_format, style=request.config.style
        )
        if self.generator:
            content = self.generator.generate(
                system="你是报告编辑与排版专家。", prompt=f"{prompt}\n初稿：\n{draft}",
                max_tokens=max(2000, request.config.expected_length * 2),
            )
            return SkillResult(content, "formatted_draft", {"prompt_version": "1.0"})

        normalized = re.sub(r"\n{3,}", "\n\n", draft.strip()) + "\n"
        output_format = request.config.output_format
        if output_format == "html":
            blocks: list[str] = []
            for block in normalized.split("\n\n"):
                escaped = html.escape(block)
                if escaped.startswith("# "):
                    blocks.append(f"<h1>{escaped[2:]}</h1>")
                elif escaped.startswith("## "):
                    blocks.append(f"<h2>{escaped[3:]}</h2>")
                else:
                    blocks.append(f"<p>{escaped.replace(chr(10), '<br>')}</p>")
            content = (
                '<!doctype html><html lang="zh-CN"><meta charset="utf-8">'
                f"<title>{html.escape(request.config.topic)}</title><body>"
                + "".join(blocks) + "</body></html>"
            )
        elif output_format == "json":
            content = json.dumps(
                {"title": request.config.topic, "style": request.config.style,
                 "content_markdown": normalized},
                ensure_ascii=False, indent=2,
            )
        elif output_format == "text":
            content = re.sub(r"^#{1,6}\s+", "", normalized, flags=re.MULTILINE)
        elif output_format == "feishu":
            content = normalized
        elif output_format in {"docx", "pdf"}:
            # Canonical Markdown is handed to an injected renderer in publish.
            content = normalized
        else:
            content = normalized
        return SkillResult(
            content, "formatted_draft",
            {
                "format": output_format,
                "style": request.config.style,
                "requires_renderer": output_format in {"docx", "pdf"},
                "native_format": output_format in {
                    "markdown", "html", "json", "text", "feishu"
                },
            },
        )
