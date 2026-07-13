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
        "minimax-docx", "word_aesthetic_formatting",
        "https://github.com/MiniMax-AI/skills/tree/main/skills/minimax-docx",
        "MIT", 13_030,
        notes=(
            "参考其OOXML样式、模板映射和校验门方法；本项目采用clean-room "
            "python-docx适配，不复制C#实现。"
        ),
        author="MiniMax-AI", version_checked="main@2026-07-13",
    ),
    IntegrationSpec(
        "frontend-slides", "html_slides_design",
        "https://github.com/zarazhangrui/frontend-slides",
        "MIT", 25_388,
        notes=(
            "张咋啦发布的HTML Slides Skill；参考单文件、自包含和视觉层级方法，"
            "本项目使用独立渲染器。"
        ),
        author="zarazhangrui",
        version_checked="9906a34d640d2111f724544cbc50f7f130569ae1",
    ),
    IntegrationSpec(
        "html-ppt-skill", "html_slides_templates",
        "https://github.com/lewislulu/html-ppt-skill",
        "MIT", 7_099,
        notes=(
            "参考固定画布、token化主题、布局预算和键盘运行时；"
            "内置HTML保持单文件并独立实现。"
        ),
        author="lewislulu", version_checked="main@2026-07-13",
    ),
    IntegrationSpec(
        "marp", "slides_multi_format",
        "https://github.com/marp-team/marp", "MIT", 12_172,
        notes="可选外部CLI；内置SlidesRenderer不依赖Node或浏览器。",
        author="marp-team", version_checked="main@2026-07-13",
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
    IntegrationSpec(
        "quants-playbook", "quant_brokerage_research_reference",
        "https://github.com/hugo2046/QuantsPlaybook",
        "NOASSERTION", 5_577,
        notes=(
            "券商金工研报复现参考库；根目录无开源许可证，部分内容仅声明学习研究用途，"
            "且依赖jqdata/jqfactor/Tushare。仅登记为observe_only，不复制或执行源码。"
        ),
        author="hugo2046",
        version_checked="87163521c75629a3466564c017ac734a236a9ce4",
    ),
)


BUILTIN_SKILL_ORDER = (
    "capability_sweep",
    "requirements_analysis",
    "skill_research",
    "writing_standards",
    "issue_tree",
    "outline",
    "research",
    "evidence_pipeline",
    "data_processing",
    "quant_finance_research",
    "material_integration",
    "visualization",
    "writing",
    "writing_finalize",
    "pressure_test",
    "formatting",
    "review",
    "quality_gate",
    "publish",
    "experience_evolution",
)
