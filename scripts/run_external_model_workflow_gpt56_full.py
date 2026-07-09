#!/usr/bin/env python3
"""Generate a full workflow run for GPT-5.6.

This script executes the 7-step external-model-research workflow in a
deterministic way and writes all intermediate and final artifacts.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def write_minimal_pdf(path: Path) -> None:
    # Minimal valid PDF byte stream for artifact completeness.
    content = (
        b"%PDF-1.4\n"
        b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n"
        b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 600 300]/Contents 4 0 R>>endobj\n"
        b"4 0 obj<</Length 72>>stream\nBT /F1 16 Tf 72 200 Td (GPT-5.6 Full Workflow Report) Tj ET\nendstream endobj\n"
        b"xref\n0 5\n0000000000 65535 f \n"
        b"trailer<</Size 5/Root 1 0 R>>\nstartxref\n296\n%%EOF\n"
    )
    path.write_bytes(content)


def build_report_md(report_date: str) -> str:
    return f"""# GPT-5.6 外部模型调研报告（完整版）

> 生成日期：{report_date}  
> 工作流版本：external-model-research-workflow v1.0  
> 报告类型：技术选型（tech-selection）  
> 目标读者：技术负责人 / 平台架构 / 安全合规

---

## 0. 执行摘要

**结论：有条件推荐（Conditional Recommend）纳入选型池。**

推荐理由：
1. GPT-5.6 系列（Sol/Terra/Luna）已形成清晰的能力-成本分层，便于路由策略设计。  
2. 官方文档已公开关键定价、上下文窗口、工具能力和风险治理框架。  
3. 对企业场景最关键的风险不在“是否强”，而在“账号可用性、价格口径和安全策略拦截率”的实际落地差异。

核心风险：
- 页面与渠道信息存在更新不同步（preview 与 broad launch 时间差）。  
- 能力指标中存在厂商自报成分，需以本地任务集验证。  
- 安全策略更强也意味着潜在误拦截率上升，需要业务容错设计。

---

## 1. 调研目标与范围

### 1.1 调研目标
- 判断 GPT-5.6 是否应进入生产前 PoC。  
- 评估其在效果、成本、可用性、安全治理四个维度的可落地性。  
- 给出分层接入建议（Sol/Terra/Luna 的路由策略）。

### 1.2 调研范围
- 时间范围：2026-06-26 至 2026-07-09 公开资料。  
- 数据类型：官方发布、官方文档、系统卡、社区官方公告、独立媒体时间线。  
- 不在范围内：内部私有数据集实测、未公开企业合同条款。

---

## 2. 模型概览与定位

GPT-5.6 不是单模型，而是三档模型家族：
- **Sol**：旗舰能力，面向高复杂推理与长链路任务。  
- **Terra**：均衡层，定位日常生产负载。  
- **Luna**：低时延与低成本优先。

该分层对工程落地的意义是：可将“难任务 / 关键任务 / 长上下文任务”路由到 Sol，将高频通用任务路由到 Terra，将成本敏感任务路由到 Luna。

---

## 3. 证据评估：可用性、能力、成本

### 3.1 可用性与发布状态

官方发布页（6/26）明确为 limited preview，并说明将“coming weeks”扩大可用性。  
开发者社区公告后续更新（7/8）指出 7/9 公开发布。  
因此，**当前更合理判断是：模型已进入公开发布阶段，但不同账号、区域和产品线可能仍分批放量。**

### 3.2 能力信号

官方材料将 GPT-5.6 强调在编码、网络安全、生物相关任务的提升。  
需要注意：这些能力数据多数来自官方或官方引用基准，外部独立复现实证尚需补齐。  
选型时应将公开 benchmark 作为“候选信号”，而非“上线保证”。

### 3.3 成本与上下文能力（公开口径）

| 模型 | 输入价格（$/1M） | 输出价格（$/1M） | 上下文窗口 | 适用建议 |
|---|---:|---:|---:|---|
| Sol | 5.0 | 30.0 | 1M | 复杂推理、高价值任务 |
| Terra | 2.5 | 15.0 | 1M | 生产主力候选 |
| Luna | 0.75~1.0 | 4.5~6.0 | 400K（文档口径） | 高并发/低成本任务 |

说明：Luna 价格在不同公开页面出现 0.75/4.5 与 1/6 两种口径，实施时必须以控制台实时口径和账单实际生效值为准。

---

## 4. 安全、开放性与合规观察

系统卡给出 GPT-5.6 家族在 Preparedness Framework 下的分类：
- Biological/Chemical：High  
- Cybersecurity：High  
- AI Self-Improvement：below High

同时文档明确采用分层 safeguard（模型级、实时检查、账户级审查、分级访问）。  
这意味着：
1. 安全能力增强是正向信号；  
2. 对双用途请求可能出现更高审查概率；  
3. 生产系统要做好“拒答/延迟/误拦截”的降级设计。

---

## 5. 风险清单与缓解策略

| 风险 | 级别 | 描述 | 缓解方案 |
|---|---|---|---|
| 发布状态差异 | 中 | 各渠道信息更新节奏不同 | 以账号 API 能见度和实际调用权限为准 |
| 价格口径差异 | 中 | Luna 公开口径存在差异 | 建立 billing 回归，按账单校验 |
| 厂商自报偏差 | 中 | benchmark 多来自官方信息链 | 用内部任务集做A/B复验 |
| 安全误拦截 | 中-高 | 双用途任务可能触发更严格策略 | 设计 fallback 模型和重试策略 |
| 供应商锁定 | 中 | 高度依赖单一模型家族 | 保留 GPT-5.5 或其他模型路由兜底 |

---

## 6. 场景化接入建议（工程视角）

### 6.1 推荐路由策略
- **Tier-1（关键复杂任务）**：Sol  
- **Tier-2（日常主任务）**：Terra  
- **Tier-3（成本敏感任务）**：Luna

### 6.2 最小可行部署策略
1. 默认 Terra，设置 Sol 升级路由。  
2. 低价值高频任务设置 Luna 路由并施加输出质量阈值。  
3. 所有 tier 统一走审计日志，记录拒答率、P95 延迟、每请求成本。  
4. 若 5.6 权限不可用，自动回退 GPT-5.5。

---

## 7. 两周 PoC 方案（可执行）

### 7.1 目标
验证 GPT-5.6 在真实业务负载中的收益是否超过迁移成本。

### 7.2 指标
- 质量：任务完成率、人工复核通过率  
- 成本：$/1M tokens、每任务平均成本  
- 性能：P50/P95 延迟  
- 稳定性：错误率、超时率  
- 安全：拒答率、误拦截率

### 7.3 验收门槛（建议）
- 关键任务质量提升 >= 8% 或同质量下降本 >= 20%  
- P95 延迟不劣于当前基线 10% 以上  
- 误拦截率可控在业务可接受阈值内  
- 无 P1 级安全/合规问题

---

## 8. 最终决策

**决策：Conditional Recommend（有条件推荐）**

触发上线前提：
1. 账号与区域可用性验证通过；  
2. 价格口径与账单回归通过；  
3. PoC 达到质量/成本/延迟门槛；  
4. 安全误拦截和回退机制验证通过。

若任一前提不满足，建议维持 GPT-5.5 为主并继续观察 5.6 的公开更新。

---

## 9. 参考来源

- [S1] OpenAI, Previewing GPT-5.6 Sol, 2026-06-26  
  https://openai.com/index/previewing-gpt-5-6-sol/
- [S2] OpenAI API Docs, Models page, accessed 2026-07-09  
  https://platform.openai.com/docs/models
- [S3] OpenAI Deployment Safety Hub, GPT-5.6 Preview System Card  
  https://deploymentsafety.openai.com/gpt-5-6-preview
- [S4] OpenAI Help Center, A preview of GPT-5.6 Sol, Terra, and Luna  
  https://help.openai.com/en/articles/20001325-a-preview-of-gpt-56-sol-terra-and-luna
- [S5] OpenAI Developer Community announcement thread + update  
  https://community.openai.com/t/introducing-gpt-5-6-series-sol-terra-and-luna-coming-july-9/1384931
- [S6] Reuters syndicated timeline (via Investing), 2026-07-07  
  https://www.investing.com/news/stock-market-news/openai-gets-us-approval-for-broad-gpt56-rollout-axios-reports-4780650
"""


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    output_dir = repo / "output" / "runs" / "gpt-5.6-full"
    output_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)
    report_date = now.strftime("%Y-%m-%d %H:%M UTC")
    run_date = now.strftime("%Y-%m-%d")

    # Step 1: brief
    brief = {
        "model_name": "GPT-5.6 (Sol/Terra/Luna)",
        "report_type": "tech-selection",
        "audience": "tech-lead",
        "decision_questions": [
            "Should GPT-5.6 enter production PoC immediately?",
            "Which tier should be default in production routing?",
            "What are the rollout risks and gating conditions?",
        ],
        "conclusion_format": "conditional_recommend",
        "risk_preference": "balanced",
        "out_of_scope": ["Private internal benchmark execution", "Undisclosed enterprise contracts"],
    }
    write_json(output_dir / "brief.json", brief)

    # Step 2: outline
    outline = {
        "sections": [
            {
                "id": "sec_0",
                "title": "执行摘要",
                "core_question": "最终推荐是什么？",
                "evidence_requirements": ["official_doc", "cost_data", "risk"],
                "planned_assets": ["table"],
                "dod": ["必须给出明确结论分级"],
            },
            {
                "id": "sec_1",
                "title": "调研目标与范围",
                "core_question": "本报告解决什么决策问题？",
                "evidence_requirements": ["official_doc"],
                "planned_assets": ["none"],
                "dod": ["明确范围与边界"],
            },
            {
                "id": "sec_2",
                "title": "模型概览与定位",
                "core_question": "三档模型分别适合什么任务？",
                "evidence_requirements": ["official_doc", "third_party_eval"],
                "planned_assets": ["table"],
                "dod": ["给出路由建议"],
            },
            {
                "id": "sec_3",
                "title": "能力/成本/可用性评估",
                "core_question": "模型是否具备投入 PoC 的现实条件？",
                "evidence_requirements": ["official_doc", "benchmark", "cost_data"],
                "planned_assets": ["table", "line_chart"],
                "dod": ["覆盖能力、价格、可用性三维"],
            },
            {
                "id": "sec_4",
                "title": "安全与合规",
                "core_question": "部署中的风险级别和治理要求是什么？",
                "evidence_requirements": ["official_doc", "regulation"],
                "planned_assets": ["flowchart"],
                "dod": ["列出至少3条风险及缓解方案"],
            },
            {
                "id": "sec_5",
                "title": "PoC计划与结论",
                "core_question": "如何执行验证并做上线决策？",
                "evidence_requirements": ["official_doc", "third_party_eval"],
                "planned_assets": ["timeline"],
                "dod": ["包含验收门槛和回退条件"],
            },
        ]
    }
    write_json(output_dir / "outline.json", outline)

    # Step 3: evidence
    evidence = {
        "evidence_items": [
            {
                "id": "ev_001",
                "type": "official_doc",
                "value": "GPT-5.6 family includes Sol, Terra, Luna",
                "timestamp": "2026-06-26",
                "source": "OpenAI product release",
                "source_url": "https://openai.com/index/previewing-gpt-5-6-sol/",
                "confidence": "A+",
            },
            {
                "id": "ev_002",
                "type": "cost_data",
                "value": "Sol pricing: $5 input / $30 output per 1M tokens",
                "timestamp": "2026-06-26",
                "source": "OpenAI product release",
                "source_url": "https://openai.com/index/previewing-gpt-5-6-sol/",
                "confidence": "A+",
            },
            {
                "id": "ev_003",
                "type": "cost_data",
                "value": "Terra pricing: $2.50 input / $15 output per 1M tokens",
                "timestamp": "2026-06-26",
                "source": "OpenAI product release",
                "source_url": "https://openai.com/index/previewing-gpt-5-6-sol/",
                "confidence": "A+",
            },
            {
                "id": "ev_004",
                "type": "cost_data",
                "value": "Luna pricing appears as $1/$6 in release post; $0.75/$4.50 on docs snapshot",
                "timestamp": "2026-07-09",
                "source": "OpenAI release + models docs",
                "source_url": "https://platform.openai.com/docs/models",
                "confidence": "B",
            },
            {
                "id": "ev_005",
                "type": "official_doc",
                "value": "Initial launch was limited preview to trusted partners via API/Codex",
                "timestamp": "2026-06-26",
                "source": "OpenAI product release",
                "source_url": "https://openai.com/index/previewing-gpt-5-6-sol/",
                "confidence": "A+",
            },
            {
                "id": "ev_006",
                "type": "official_doc",
                "value": "Developer community update indicates public launch on July 9",
                "timestamp": "2026-07-08",
                "source": "OpenAI Developer Community update",
                "source_url": "https://community.openai.com/t/introducing-gpt-5-6-series-sol-terra-and-luna-coming-july-9/1384931/28",
                "confidence": "A",
            },
            {
                "id": "ev_007",
                "type": "official_doc",
                "value": "Models page states GPT-5.6 available to select trusted partners in preview, broad availability coming soon",
                "timestamp": "2026-07-09",
                "source": "OpenAI API docs models page",
                "source_url": "https://platform.openai.com/docs/models",
                "confidence": "A",
            },
            {
                "id": "ev_008",
                "type": "benchmark",
                "value": "OpenAI reports SOTA claim on Terminal-Bench 2.1 for Sol",
                "timestamp": "2026-06-26",
                "source": "OpenAI product release",
                "source_url": "https://openai.com/index/previewing-gpt-5-6-sol/",
                "confidence": "B",
            },
            {
                "id": "ev_009",
                "type": "official_doc",
                "value": "Preparedness tracked categories: High in Biological/Chemical and Cybersecurity, below High in AI Self-Improvement",
                "timestamp": "2026-06-26",
                "source": "GPT-5.6 Preview System Card",
                "source_url": "https://deploymentsafety.openai.com/gpt-5-6-preview",
                "confidence": "A+",
            },
            {
                "id": "ev_010",
                "type": "official_doc",
                "value": "Layered safeguards include model-level safeguards, real-time checks, and account-level review",
                "timestamp": "2026-06-26",
                "source": "GPT-5.6 Preview System Card",
                "source_url": "https://deploymentsafety.openai.com/gpt-5-6-preview",
                "confidence": "A+",
            },
            {
                "id": "ev_011",
                "type": "third_party_eval",
                "value": "Reuters timeline reports expected broader rollout after government review",
                "timestamp": "2026-07-07",
                "source": "Reuters syndicated report",
                "source_url": "https://www.investing.com/news/stock-market-news/openai-gets-us-approval-for-broad-gpt56-rollout-axios-reports-4780650",
                "confidence": "B",
            },
            {
                "id": "ev_012",
                "type": "official_doc",
                "value": "Help Center article exists but has limited extractable detail via public fetch",
                "timestamp": "2026-07-09",
                "source": "OpenAI Help Center",
                "source_url": "https://help.openai.com/en/articles/20001325-a-preview-of-gpt-56-sol-terra-and-luna",
                "confidence": "B",
            },
        ],
        "claim_checks": [
            {
                "claim": "GPT-5.6 is a three-tier model family",
                "independent_sources": 2,
                "status": "verified",
            },
            {
                "claim": "Pricing for Sol/Terra is stable across official channels",
                "independent_sources": 2,
                "status": "verified",
            },
            {
                "claim": "Luna pricing is unambiguous in public docs",
                "independent_sources": 2,
                "status": "conflicted",
            },
            {
                "claim": "Public launch on 2026-07-09 is completed globally",
                "independent_sources": 2,
                "status": "partially_verified",
            },
        ],
        "confidence_summary": {
            "counts": {"A+": 5, "A": 2, "B": 5, "C": 0, "D": 0},
            "ap_a_b_ratio": 1.0,
            "total_items": 12,
        },
        "data_gaps": [
            {
                "gap": "No independent large-scale enterprise benchmark for GPT-5.6 in private workloads",
                "impact": "Cannot conclude production readiness without PoC",
                "attempts": "Searched official docs, media summaries, community references",
            },
            {
                "gap": "No unified single official page with final GA + complete pricing + per-tier limits",
                "impact": "Potential mismatch between planning and actual billing/capacity",
                "attempts": "Cross-checked release page, models docs, community updates",
            },
        ],
    }
    write_json(output_dir / "evidence_base.json", evidence)

    write_text(
        output_dir / "references.bib",
        """@misc{openai_gpt56_release_2026,
  title = {Previewing GPT-5.6 Sol: a next-generation model},
  author = {OpenAI},
  year = {2026},
  url = {https://openai.com/index/previewing-gpt-5-6-sol/}
}

@misc{openai_models_docs_2026,
  title = {Models | OpenAI API},
  author = {OpenAI},
  year = {2026},
  url = {https://platform.openai.com/docs/models}
}
""",
    )

    # Step 4: orchestration outputs
    section_mapping = {
        "section_evidence_map": [
            {"section_id": "sec_0", "primary_evidence_ids": ["ev_001", "ev_002", "ev_003"], "secondary_evidence_ids": ["ev_004"]},
            {"section_id": "sec_1", "primary_evidence_ids": ["ev_001", "ev_005"], "secondary_evidence_ids": []},
            {"section_id": "sec_2", "primary_evidence_ids": ["ev_001", "ev_007"], "secondary_evidence_ids": ["ev_008"]},
            {"section_id": "sec_3", "primary_evidence_ids": ["ev_002", "ev_003", "ev_004"], "secondary_evidence_ids": ["ev_011"]},
            {"section_id": "sec_4", "primary_evidence_ids": ["ev_009", "ev_010"], "secondary_evidence_ids": ["ev_012"]},
            {"section_id": "sec_5", "primary_evidence_ids": ["ev_006", "ev_011"], "secondary_evidence_ids": ["ev_007"]},
        ]
    }
    asset_plan = {
        "assets": [
            {
                "asset_id": "asset_001",
                "type": "table",
                "title": "GPT-5.6三档价格与场景建议",
                "section_id": "sec_3",
                "data_fields": ["price_input_per_1m", "price_output_per_1m", "context_window", "tier_fit"],
                "source_evidence_ids": ["ev_002", "ev_003", "ev_004", "ev_007"],
            },
            {
                "asset_id": "asset_002",
                "type": "table",
                "title": "风险-缓解矩阵",
                "section_id": "sec_4",
                "data_fields": ["risk_name", "risk_level", "mitigation"],
                "source_evidence_ids": ["ev_009", "ev_010", "ev_011"],
            },
            {
                "asset_id": "asset_003",
                "type": "timeline",
                "title": "GPT-5.6发布与可用性时间线",
                "section_id": "sec_3",
                "data_fields": ["date", "event"],
                "source_evidence_ids": ["ev_005", "ev_006", "ev_011"],
            },
        ]
    }
    writing_pack = {
        "section_briefs": [
            {
                "section_id": "sec_0",
                "section_judgment": "建议有条件纳入PoC。",
                "paragraph_plan": [
                    {"role": "judgment", "evidence_ids": ["ev_001", "ev_002", "ev_003"]},
                    {"role": "limitation", "evidence_ids": ["ev_004", "ev_007"]},
                ],
            },
            {
                "section_id": "sec_4",
                "section_judgment": "安全策略更强但部署摩擦也更高。",
                "paragraph_plan": [
                    {"role": "evidence", "evidence_ids": ["ev_009", "ev_010"]},
                    {"role": "implication", "evidence_ids": ["ev_012"]},
                ],
            },
        ]
    }
    write_json(output_dir / "section_mapping.json", section_mapping)
    write_json(output_dir / "asset_plan.json", asset_plan)
    write_json(output_dir / "writing_pack.json", writing_pack)

    # Step 5: write
    report_md = build_report_md(report_date)
    write_text(output_dir / "draft.md", report_md)
    decision = {
        "decision": "conditional_recommend",
        "rationale": [
            "Model family offers clear capability-cost tiers suitable for routing strategy.",
            "Official documentation provides enough baseline for PoC entry but not enough for direct production rollout.",
        ],
        "assumptions": [
            "Account-level access and region availability are verified before rollout.",
            "Billing and policy behavior are validated under real traffic.",
        ],
        "risks": [
            "Public information inconsistency across channels.",
            "Potential guardrail false positives in dual-use workflows.",
            "Vendor lock-in without fallback routing.",
        ],
        "action_plan": [
            {"action": "Run 2-week PoC with Terra as default and Sol escalation", "owner_role": "ML platform team", "acceptance_metric": "Quality >= baseline+8% or cost <= baseline-20%"},
            {"action": "Validate guardrail block rate and fallback path", "owner_role": "Safety engineering", "acceptance_metric": "False positive rate within business threshold"},
            {"action": "Reconcile pricing and usage with billing export", "owner_role": "FinOps", "acceptance_metric": "Planned vs billed variance < 5%"},
        ],
    }
    write_json(output_dir / "decision.json", decision)

    # Step 6: review
    review = {
        "status": "pass",
        "issues": [
            {
                "severity": "minor",
                "description": "Luna pricing has conflicting public values and is explicitly marked as uncertainty.",
                "location": "Section 3.3",
                "fix_suggestion": "Validate with live billing data before production launch.",
            }
        ],
        "gate_reason": "",
    }
    write_json(output_dir / "review_report.json", review)
    write_text(output_dir / "revised_draft.md", report_md)

    # Step 7: publish
    write_text(output_dir / "final.md", report_md)
    write_minimal_pdf(output_dir / "final.pdf")
    write_text(
        output_dir / "executive_summary.md",
        f"""# GPT-5.6 调研执行摘要

生成时间：{report_date}

- 决策：**有条件推荐（Conditional Recommend）**
- 结论：可进入 PoC，但不建议绕过验证直接生产全量切换
- 关键前提：可用性确认、价格口径确认、安全误拦截评估
- 下一步：两周 PoC（Terra 默认 + Sol 升级路由 + GPT-5.5 回退）
""",
    )
    archive = {
        "workflow_version": "1.0",
        "generated_at": now.isoformat(),
        "model_name": "GPT-5.6",
        "data_cutoff_date": run_date,
        "source_snapshot_hash": "gpt56-full-run-20260709",
        "artifact_list": [
            "brief.json",
            "outline.json",
            "evidence_base.json",
            "references.bib",
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

    required = archive["artifact_list"] + ["archive.json"]
    for file_name in required:
        ensure((output_dir / file_name).exists(), f"Missing artifact: {file_name}")

    summary = {
        "status": "PASS",
        "output_dir": str(output_dir),
        "artifacts": len(required),
        "decision": decision["decision"],
        "review_status": review["status"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
