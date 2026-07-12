"""Curated optional integrations; metadata only, no vendored third-party code."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IntegrationSpec:
    id: str
    capability: str
    source: str
    license: str
    stars_checked: int | None
    required: bool = False
    notes: str = ""
    author: str = "unknown"
    version_checked: str = "snapshot-2026-07-12"


# Stars are a dated selection signal, not a quality guarantee. See
# docs/OPEN_SOURCE_SKILL_CATALOG.md for provenance and review date.
DEFAULT_INTEGRATIONS = (
    IntegrationSpec(
        "crawl4ai", "industry_web_collection",
        "https://github.com/unclecode/crawl4ai", "Apache-2.0", 72_391,
        notes="Optional web-to-Markdown collector adapter.",
        author="unclecode", version_checked="v0.9.1",
    ),
    IntegrationSpec(
        "gpt-researcher", "deep_research",
        "https://github.com/assafelovic/gpt-researcher", "Apache-2.0", 28_264,
        notes="Optional multi-source research provider.",
        author="assafelovic", version_checked="v3.5.1",
    ),
    IntegrationSpec(
        "docling", "document_parsing",
        "https://github.com/docling-project/docling", "MIT", 63_028,
        notes="Optional PDF/DOCX/PPTX/table extraction adapter.",
        author="docling-project", version_checked="main@2026-07-12",
    ),
    IntegrationSpec(
        "semantic-scholar-skill", "academic_search",
        "https://github.com/Agents365-ai/semanticscholar-skill", "MIT", 53,
        notes="Agent-skill-compatible citation graph search.",
        author="Agents365-ai", version_checked="v0.8.1",
    ),
    IntegrationSpec(
        "orchestra-research-skills", "ai_research_methods",
        "https://github.com/Orchestra-Research/AI-Research-SKILLs", "MIT", 10_628,
        notes="Conditionally applicable to AI engineering research.",
        author="Orchestra-Research", version_checked="v1.7.2",
    ),
    IntegrationSpec(
        "scientific-agent-skills", "scientific_domain_methods",
        "https://github.com/K-Dense-AI/scientific-agent-skills", "MIT (top-level)",
        30_726, notes="Each selected child skill still requires license review.",
        author="K-Dense-AI", version_checked="v2.53.0",
    ),
    IntegrationSpec(
        "mermaid", "diagram_rendering",
        "https://github.com/mermaid-js/mermaid", "MIT", 89_188,
        notes="Optional renderer for generated Mermaid specifications.",
        author="mermaid-js", version_checked="develop@2026-07-12",
    ),
    IntegrationSpec(
        "vega-lite", "chart_rendering",
        "https://github.com/vega/vega-lite", "BSD-3-Clause", 5_404,
        notes="Optional renderer for generated Vega-Lite specifications.",
        author="vega", version_checked="main@2026-07-12",
    ),
    IntegrationSpec(
        "pandoc", "document_publishing",
        "https://github.com/jgm/pandoc", "GPL-2.0", 45_344,
        notes="Invoke as an external CLI; do not vendor or link its code.",
        author="jgm", version_checked="main@2026-07-12",
    ),
    IntegrationSpec(
        "openclaw-deep-research", "claim_verified_research",
        "https://github.com/MilleniumGenAI/deep-research-openclaw-agent",
        "MIT-0", 2, notes="ClawHub integration with source registry and claim ledger.",
        author="MilleniumGenAI", version_checked="main@2026-03-10",
    ),
    IntegrationSpec(
        "openclaw-deep-research-pro", "lightweight_web_research",
        "https://github.com/parags/deep-research-pro", "MIT", 7,
        notes="Low-star fallback; not preferred over mature providers.",
        author="parags", version_checked="main@2026-02-03",
    ),
)


BUILTIN_SKILL_ORDER = (
    "capability_sweep",
    "requirements_analysis",
    "skill_research",
    "issue_tree",
    "outline",
    "research",
    "evidence_governance",
    "data_processing",
    "material_integration",
    "visualization",
    "writing",
    "citation_management",
    "pressure_test",
    "formatting",
    "review",
    "quality_gate",
    "publish",
    "experience_evolution",
)
