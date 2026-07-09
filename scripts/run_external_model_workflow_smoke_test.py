#!/usr/bin/env python3
"""Smoke test for model-report-orchestrator workflow (v2).

Validates:
1) workflow docs/config and orchestrator + 7 step skill files exist
2) YAML includes expected orchestrator and step skill names
3) a minimal archive-style artifact chain can be generated end-to-end
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_minimal_pdf(path: Path) -> None:
    content = (
        b"%PDF-1.4\n"
        b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n"
        b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 300 144]/Contents 4 0 R>>endobj\n"
        b"4 0 obj<</Length 41>>stream\nBT /F1 12 Tf 72 72 Td (Workflow Smoke Pass) Tj ET\nendstream endobj\n"
        b"xref\n0 5\n0000000000 65535 f \n"
        b"trailer<</Size 5/Root 1 0 R>>\nstartxref\n249\n%%EOF\n"
    )
    path.write_bytes(content)


def main() -> int:
    repo = Path(__file__).resolve().parents[1]

    required_paths = [
        repo / "external-model-research-workflow.md",
        repo / "external-model-research-workflow.yaml",
        repo / "skills" / "external-model-research" / "model-report-orchestrator" / "SKILL.md",
        repo / "skills" / "external-model-research" / "skill_01_brief" / "SKILL.md",
        repo / "skills" / "external-model-research" / "skill_02_outline" / "SKILL.md",
        repo / "skills" / "external-model-research" / "skill_03_evidence" / "SKILL.md",
        repo / "skills" / "external-model-research" / "skill_04_orchestration" / "SKILL.md",
        repo / "skills" / "external-model-research" / "skill_05_write_decide" / "SKILL.md",
        repo / "skills" / "external-model-research" / "skill_06_review" / "SKILL.md",
        repo / "skills" / "external-model-research" / "skill_07_publish" / "SKILL.md",
    ]
    for path in required_paths:
        ensure(path.exists(), f"Missing required file: {path}")

    yaml_text = (repo / "external-model-research-workflow.yaml").read_text(encoding="utf-8")
    for token in (
        "id: model-report-orchestrator",
        "name: mr-step1-scope",
        "name: mr-step2-outline",
        "name: mr-step3-collect",
        "name: mr-step4-process",
        "name: mr-step5-write",
        "name: mr-step6-review",
        "name: mr-step7-output",
        "min_sources: 25",
        "min_competitors: 5",
        "min_benchmark_metrics: 25",
        "min_tables: 12",
        "min_figure_specs: 4",
        "review_pass_score: 90",
    ):
        ensure(token in yaml_text, f"Workflow yaml missing token: {token}")

    orchestrator_text = (
        repo / "skills" / "external-model-research" / "model-report-orchestrator" / "SKILL.md"
    ).read_text(encoding="utf-8")
    ensure(
        ("防“浅报告”硬门槛" in orchestrator_text) or ("高丰富度硬门槛" in orchestrator_text),
        "Orchestrator missing anti-shallow gate section",
    )

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = Path("/tmp") / f"model-report-orchestrator-smoke-{run_id}"
    archive_dir = run_dir / "archive"

    # Step 1: scope
    scope_md = """# 报告企划书 — SmokeModel

## 读者画像
- 主要读者: 技术选型团队
- 决策类型: 选型
- 阅读场景: 周会前快速评审
- 核心担忧: 数据不准确导致误判

## 报告参数
- 报告类型: 技术选型
- 篇幅: 简报(1500-3000字)
- 风格: 决策简报风
- 结论形式: 推荐/有条件推荐/不推荐
"""
    write_text(archive_dir / "scope.md", scope_md)

    # Step 2: outline
    outline_md = """## §1 模型全景
核心问题: 这个模型的定位是什么？
素材需求: 官方模型卡, 技术报告
需要生成的图表: 基础参数对比表
"""
    write_text(archive_dir / "outline.md", outline_md)

    # Step 3: raw_data
    write_text(archive_dir / "raw_data" / "official" / "model_card_official.md", "name: SmokeModel\n")
    write_text(archive_dir / "raw_data" / "paper" / "001_report.md", "technical details\n")
    write_text(archive_dir / "raw_data" / "benchmarks" / "scores_thirdparty.csv", "metric,value\nMMLU,80.1\n")
    write_text(archive_dir / "raw_data" / "competitors" / "matrix.csv", "model,mmlu\nA,79.8\n")
    write_text(archive_dir / "raw_data" / "ecosystem" / "license.txt", "Apache-2.0\n")
    write_text(
        archive_dir / "raw_data" / "benchmark_catalog.csv",
        "metric_id,dimension,benchmark_name,value,model,unit,source_id\nm1,reasoning,MMLU,80.1,SmokeModel,%,s1\n",
    )
    write_text(
        archive_dir / "raw_data" / "competitor_catalog.csv",
        "model_name,release_window,strengths,weaknesses,pricing,source_id\nA,2026Q2,math,coding,2/12,s2\n",
    )
    write_text(archive_dir / "raw_data" / "references.md", "- https://example.com\n")

    # Step 4: processed_data
    write_text(archive_dir / "processed_data" / "section_1" / "info_card.md", "- param: 32B\n")
    write_text(archive_dir / "processed_data" / "section_3" / "benchmark_table.csv", "model,mmlu\nSmokeModel,80.1\n")
    write_text(archive_dir / "processed_data" / "figures" / "benchmark_comparison.txt", "placeholder figure\n")
    write_text(
        archive_dir / "processed_data" / "evidence_map.csv",
        "section,evidence_id,claim_id,strength\nsection_3,e1,c1,strong\n",
    )
    write_text(
        archive_dir / "processed_data" / "evidence_ledger.csv",
        "claim_id,claim_text,source_id,quote_snippet,confidence\nc1,test claim,s1,test quote,0.8\n",
    )
    write_text(archive_dir / "processed_data" / "gaps.md", "§1 ✅ 齐全\n§2 ⚠️ 待补采\n")

    # Step 5: report
    report_md = """# SmokeModel 调研报告

本文的核心发现是：该模型可进入 PoC。

数据显示，MMLU 为 80.1（第三方评测, 2026）。
这意味着它具备进入候选池的基础能力。
"""
    write_text(archive_dir / "report.md", report_md)

    # Step 6: review
    review_md = """# 复核清单

- 事实性检查: 通过
- 完整性检查: 通过
- 读者视角检查: 通过
- 逻辑一致性检查: 通过
- 写作质量检查: 通过

结论: 通过
"""
    write_text(archive_dir / "review_checklist.md", review_md)

    # Step 7: output
    write_text(archive_dir / "output" / "report.md", report_md)
    write_minimal_pdf(archive_dir / "output" / "report.pdf")
    write_text(archive_dir / "output" / "report.docx", "placeholder docx\n")
    write_text(
        archive_dir / "output" / "executive_summary.md",
        "一句话结论：有条件推荐。\n核心发现：能力达标、数据来源清晰、需补采部署数据。\n",
    )
    write_text(
        archive_dir / "output" / "decision_brief.md",
        "评级：有条件推荐\n评分卡：能力与安全强，成本与可获得性弱。\n",
    )
    write_text(archive_dir / "output" / "figures" / "placeholder.txt", "figure asset\n")
    write_text(archive_dir / "output" / "slides" / "placeholder.txt", "slides asset\n")

    # Validate required artifacts
    required = [
        archive_dir / "scope.md",
        archive_dir / "outline.md",
        archive_dir / "raw_data" / "references.md",
        archive_dir / "raw_data" / "benchmark_catalog.csv",
        archive_dir / "raw_data" / "competitor_catalog.csv",
        archive_dir / "processed_data" / "gaps.md",
        archive_dir / "processed_data" / "evidence_map.csv",
        archive_dir / "processed_data" / "evidence_ledger.csv",
        archive_dir / "report.md",
        archive_dir / "review_checklist.md",
        archive_dir / "output" / "report.md",
        archive_dir / "output" / "report.pdf",
        archive_dir / "output" / "report.docx",
        archive_dir / "output" / "executive_summary.md",
        archive_dir / "output" / "decision_brief.md",
    ]
    for path in required:
        ensure(path.exists(), f"Missing artifact: {path}")

    summary = {
        "status": "PASS",
        "run_dir": str(run_dir),
        "validated_files": len(required),
        "workflow_id": "model-report-orchestrator",
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"SMOKE TEST FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1)
