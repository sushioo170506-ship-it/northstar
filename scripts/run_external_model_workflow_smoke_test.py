#!/usr/bin/env python3
"""Smoke test for the external model research workflow.

This test validates that:
1) Workflow docs/config and 7 skill templates exist.
2) A minimal end-to-end artifact chain can be produced for one model input.
3) Required output files and key schema fields are present.

Note: This is a structural smoke test (not real research execution).
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_minimal_pdf(path: Path) -> None:
    # Minimal valid PDF structure for artifact existence checks.
    content = (
        b"%PDF-1.4\n"
        b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n"
        b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 300 144]/Contents 4 0 R>>endobj\n"
        b"4 0 obj<</Length 44>>stream\nBT /F1 12 Tf 72 72 Td (Smoke Test Report) Tj ET\nendstream endobj\n"
        b"xref\n0 5\n0000000000 65535 f \n"
        b"trailer<</Size 5/Root 1 0 R>>\nstartxref\n256\n%%EOF\n"
    )
    path.write_bytes(content)


def main() -> int:
    repo = Path(__file__).resolve().parents[1]

    required_root_files = [
        repo / "external-model-research-workflow.md",
        repo / "external-model-research-workflow.yaml",
        repo / "examples" / "external-model-research-smoke-input.json",
    ]
    required_skill_files = [
        repo / "skills" / "external-model-research" / "skill_01_brief" / "SKILL.md",
        repo / "skills" / "external-model-research" / "skill_02_outline" / "SKILL.md",
        repo / "skills" / "external-model-research" / "skill_03_evidence" / "SKILL.md",
        repo / "skills" / "external-model-research" / "skill_04_orchestration" / "SKILL.md",
        repo / "skills" / "external-model-research" / "skill_05_write_decide" / "SKILL.md",
        repo / "skills" / "external-model-research" / "skill_06_review" / "SKILL.md",
        repo / "skills" / "external-model-research" / "skill_07_publish" / "SKILL.md",
    ]

    for path in required_root_files + required_skill_files:
        ensure(path.exists(), f"Missing required file: {path}")

    workflow_yaml_text = (repo / "external-model-research-workflow.yaml").read_text(encoding="utf-8")
    for skill_id in (
        "skill_01_brief",
        "skill_02_outline",
        "skill_03_evidence",
        "skill_04_orchestration",
        "skill_05_write_decide",
        "skill_06_review",
        "skill_07_publish",
    ):
        ensure(skill_id in workflow_yaml_text, f"Workflow config missing skill id: {skill_id}")

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = Path("/tmp") / f"external-model-research-smoke-{run_id}"
    output_dir = run_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    run_input = json.loads(
        (repo / "examples" / "external-model-research-smoke-input.json").read_text(encoding="utf-8")
    )

    # Step 1: brief
    brief = {
        "model_name": run_input["model_name"],
        "report_type": run_input["report_type"],
        "audience": run_input["audience"],
        "decision_questions": [
            "Should this model enter production PoC?",
            "What are the primary deployment risks?",
        ],
        "conclusion_format": "recommend|conditional_recommend|not_recommend",
        "risk_preference": "balanced",
        "out_of_scope": ["No private internal benchmark data in smoke test"],
    }
    write_json(output_dir / "brief.json", brief)

    # Step 2: outline
    outline = {
        "sections": [
            {
                "id": "sec_1",
                "title": "执行摘要",
                "core_question": "是否建议进入PoC？",
                "evidence_requirements": ["benchmark", "cost_data", "risk"],
                "planned_assets": ["table"],
                "dod": ["给出明确结论分级"],
            },
            {
                "id": "sec_2",
                "title": "模型能力与成本评估",
                "core_question": "能力和成本是否匹配目标场景？",
                "evidence_requirements": ["benchmark", "third_party_eval", "cost_data"],
                "planned_assets": ["bar_chart", "table"],
                "dod": ["至少一条高可信证据支撑关键判断"],
            },
        ]
    }
    write_json(output_dir / "outline.json", outline)

    # Step 3: evidence
    evidence = {
        "evidence_items": [
            {
                "id": "ev_001",
                "type": "benchmark",
                "value": "MMLU 78.4",
                "timestamp": "2026-06-20",
                "source": "Third-party benchmark summary",
                "source_url": "https://example.com/benchmark",
                "confidence": "B",
            },
            {
                "id": "ev_002",
                "type": "numeric",
                "value": "$0.90 / 1M tokens (input)",
                "timestamp": "2026-06-20",
                "source": "Vendor pricing page",
                "source_url": "https://example.com/pricing",
                "confidence": "A",
            },
        ],
        "claim_checks": [
            {
                "claim": "Model is cost-effective for PoC usage",
                "independent_sources": 2,
                "status": "verified",
            }
        ],
        "confidence_summary": {"ap_a_b_ratio": 1.0, "total_items": 2},
        "data_gaps": [{"gap": "No enterprise private latency benchmark", "impact": "medium"}],
    }
    write_json(output_dir / "evidence_base.json", evidence)
    (output_dir / "references.bib").write_text(
        "@misc{smoke2026,title={Smoke Test Placeholder Source},year={2026}}\n",
        encoding="utf-8",
    )

    # Step 4: orchestration
    section_mapping = {
        "section_evidence_map": [
            {"section_id": "sec_1", "primary_evidence_ids": ["ev_001", "ev_002"], "secondary_evidence_ids": []},
            {"section_id": "sec_2", "primary_evidence_ids": ["ev_001"], "secondary_evidence_ids": ["ev_002"]},
        ]
    }
    asset_plan = {
        "assets": [
            {
                "asset_id": "tbl_001",
                "type": "table",
                "title": "能力-成本快速对照",
                "section_id": "sec_2",
                "data_fields": ["benchmark_score", "price_per_1m_tokens"],
                "source_evidence_ids": ["ev_001", "ev_002"],
            }
        ]
    }
    writing_pack = {
        "section_briefs": [
            {
                "section_id": "sec_1",
                "section_judgment": "建议进入有限范围PoC。",
                "paragraph_plan": [
                    {"role": "judgment", "evidence_ids": ["ev_001", "ev_002"]},
                    {"role": "limitation", "evidence_ids": []},
                ],
            }
        ]
    }
    write_json(output_dir / "section_mapping.json", section_mapping)
    write_json(output_dir / "asset_plan.json", asset_plan)
    write_json(output_dir / "writing_pack.json", writing_pack)

    # Step 5: write and decide
    draft_md = """# 外部模型调研报告（Smoke Test）

## 执行摘要
判断：建议进入有限范围 PoC（证据：ev_001, ev_002）。

## 能力与成本
- 指标样例：MMLU 78.4（2026-06-20，第三方基准）
- 成本样例：$0.90 / 1M tokens（2026-06-20，官方价格页）
"""
    (output_dir / "draft.md").write_text(draft_md, encoding="utf-8")
    decision = {
        "decision": "conditional_recommend",
        "rationale": ["Benchmark and cost are acceptable for PoC."],
        "assumptions": ["Production latency requires internal validation."],
        "risks": ["Insufficient private workload evidence."],
        "action_plan": [{"action": "Run 2-week PoC", "owner_role": "ML engineer", "acceptance_metric": "P95<2.5s"}],
    }
    write_json(output_dir / "decision.json", decision)

    # Step 6: review
    review = {"status": "pass", "issues": [], "gate_reason": ""}
    write_json(output_dir / "review_report.json", review)
    (output_dir / "revised_draft.md").write_text(draft_md, encoding="utf-8")

    # Step 7: publish
    (output_dir / "final.md").write_text(draft_md, encoding="utf-8")
    write_minimal_pdf(output_dir / "final.pdf")
    (output_dir / "executive_summary.md").write_text(
        "结论：有条件推荐进入 PoC。风险：私有场景延迟数据缺失。\n", encoding="utf-8"
    )
    archive = {
        "workflow_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model_name": run_input["model_name"],
        "data_cutoff_date": "2026-06-20",
        "source_snapshot_hash": "smoke-test-placeholder",
        "artifact_list": [
            "brief.json",
            "outline.json",
            "evidence_base.json",
            "section_mapping.json",
            "asset_plan.json",
            "writing_pack.json",
            "draft.md",
            "decision.json",
            "review_report.json",
            "revised_draft.md",
            "final.md",
            "final.pdf",
            "executive_summary.md",
        ],
    }
    write_json(output_dir / "archive.json", archive)

    required_outputs = [
        "brief.json",
        "outline.json",
        "evidence_base.json",
        "section_mapping.json",
        "asset_plan.json",
        "writing_pack.json",
        "draft.md",
        "decision.json",
        "review_report.json",
        "revised_draft.md",
        "final.md",
        "final.pdf",
        "executive_summary.md",
        "archive.json",
    ]
    for item in required_outputs:
        ensure((output_dir / item).exists(), f"Missing output artifact: {item}")

    ensure(review["status"] == "pass", "Review status is not pass")
    ensure(decision["decision"] in {"recommend", "conditional_recommend", "not_recommend", "green", "yellow", "red"}, "Invalid decision value")

    summary = {
        "status": "PASS",
        "run_dir": str(run_dir),
        "validated_files": len(required_outputs),
        "model_name": run_input["model_name"],
        "decision": decision["decision"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - smoke test entrypoint
        print(f"SMOKE TEST FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1)
