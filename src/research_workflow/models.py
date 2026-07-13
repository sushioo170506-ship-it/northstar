"""Shared, dependency-free contracts for every skill."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class NodeStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    WAITING_CONFIRMATION = "waiting_confirmation"
    FAILED = "failed"
    INVALIDATED = "invalidated"


class WorkflowStatus(StrEnum):
    RUNNING = "running"
    WAITING_CONFIRMATION = "waiting_confirmation"
    COMPLETED = "completed"
    FAILED = "failed"


SUPPORTED_FORMATS = {
    "markdown", "html", "json", "text", "feishu", "docx", "pdf",
    "pptx", "slides_html",
}
SUPPORTED_WORKFLOW_PROFILES = {"quick", "standard", "deep", "regulatory"}
SUPPORTED_CONFIDENTIALITY_LEVELS = {
    "public", "internal", "secret", "confidential", "top_secret"
}


@dataclass(frozen=True)
class ReportConfig:
    topic: str
    expected_length: int = 5000
    style: str = "专业、客观、证据驱动"
    output_format: str = "markdown"
    language: str = "zh-CN"
    output_type: str = "research_report"
    audience: str = "通用专业读者"
    content_boundaries: tuple[str, ...] = ()
    prior_thoughts: str = ""
    workflow_profile: str = "deep"
    confidentiality_level: str = "public"
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "ReportConfig":
        topic = " ".join(str(raw.get("topic", "")).split())
        if not topic:
            raise ValueError("topic 不能为空")
        if len(topic) > 500:
            raise ValueError("topic 不能超过 500 个字符")
        try:
            expected_length = int(raw.get("expected_length", 5000))
        except (TypeError, ValueError) as exc:
            raise ValueError("expected_length 必须为整数") from exc
        if not 500 <= expected_length <= 500_000:
            raise ValueError("expected_length 必须在 500 到 500000 之间")
        style = " ".join(str(raw.get("style", "") or "专业、客观、证据驱动").split())
        output_format = str(raw.get("output_format", "markdown")).strip().lower()
        aliases = {
            "md": "markdown", "htm": "html", "web": "html", "webpage": "html",
            "网页": "html", "txt": "text", "word": "docx", "飞书": "feishu",
            "ppt": "pptx", "powerpoint": "pptx", "slides": "slides_html",
            "幻灯片": "slides_html",
        }
        output_format = aliases.get(output_format, output_format)
        if output_format not in SUPPORTED_FORMATS:
            raise ValueError(f"output_format 必须是 {sorted(SUPPORTED_FORMATS)} 之一")
        language = str(raw.get("language", "zh-CN")).strip() or "zh-CN"
        output_type = " ".join(
            str(raw.get("output_type", "research_report")).split()
        ) or "research_report"
        audience = " ".join(
            str(raw.get("audience", "通用专业读者")).split()
        ) or "通用专业读者"
        raw_boundaries = raw.get("content_boundaries", ())
        if isinstance(raw_boundaries, str):
            raw_boundaries = [raw_boundaries]
        if not isinstance(raw_boundaries, (list, tuple)):
            raise ValueError("content_boundaries 必须是字符串数组")
        content_boundaries = tuple(
            " ".join(str(item).split()) for item in raw_boundaries if str(item).strip()
        )
        prior_thoughts = str(raw.get("prior_thoughts", "")).strip()
        workflow_profile = str(raw.get("workflow_profile", "deep")).strip().lower()
        if workflow_profile not in SUPPORTED_WORKFLOW_PROFILES:
            raise ValueError(
                f"workflow_profile 必须是 {sorted(SUPPORTED_WORKFLOW_PROFILES)} 之一"
            )
        confidentiality_level = str(
            raw.get("confidentiality_level", "public")
        ).strip().lower()
        confidentiality_aliases = {
            "公开": "public",
            "内部": "internal",
            "秘密": "secret",
            "机密": "confidential",
            "绝密": "top_secret",
        }
        confidentiality_level = confidentiality_aliases.get(
            confidentiality_level, confidentiality_level
        )
        if confidentiality_level not in SUPPORTED_CONFIDENTIALITY_LEVELS:
            raise ValueError(
                "confidentiality_level 必须是 "
                f"{sorted(SUPPORTED_CONFIDENTIALITY_LEVELS)} 之一"
            )
        extra = raw.get("extra", {})
        if not isinstance(extra, dict):
            raise ValueError("extra 必须是对象")
        return cls(
            topic=topic,
            expected_length=expected_length,
            style=style,
            output_format=output_format,
            language=language,
            output_type=output_type,
            audience=audience,
            content_boundaries=content_boundaries,
            prior_thoughts=prior_thoughts,
            workflow_profile=workflow_profile,
            confidentiality_level=confidentiality_level,
            extra=extra,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ContextItem:
    id: str
    workflow_id: str
    node_id: str
    artifact_type: str
    content: str
    created_at: str
    metadata: dict[str, Any]
    score: float = 0.0


@dataclass(frozen=True)
class SkillRequest:
    workflow_id: str
    node_id: str
    config: ReportConfig
    inputs: dict[str, Any]
    context: tuple[ContextItem, ...] = ()
    feedback: tuple[str, ...] = ()


@dataclass(frozen=True)
class SkillResult:
    content: str
    artifact_type: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RunOutcome:
    workflow_id: str
    status: WorkflowStatus
    waiting_at: str | None = None
    final_artifact_id: str | None = None
