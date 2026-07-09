#!/usr/bin/env python3
"""Generate a full example run for model-report-orchestrator (GPT-5.6)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


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
        b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 600 300]/Contents 4 0 R>>endobj\n"
        b"4 0 obj<</Length 69>>stream\nBT /F1 16 Tf 72 180 Td (GPT-5.6 Full Report Generated) Tj ET\nendstream endobj\n"
        b"xref\n0 5\n0000000000 65535 f \n"
        b"trailer<</Size 5/Root 1 0 R>>\nstartxref\n294\n%%EOF\n"
    )
    path.write_bytes(content)


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    run_dir = repo / "archive" / "runs" / "gpt-5.6-full"
    run_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y-%m-%d %H:%M UTC")

    # Step 1: scope
    scope = f"""# 报告企划书 — GPT-5.6

## 读者画像
- 主要读者: 技术选型团队
- 决策类型: 选型
- 阅读场景: 架构评审会前 10 分钟速览
- 核心担忧: 数据口径不一致导致选型偏差

## 报告参数
- 报告类型: 技术选型
- 篇幅: 长篇详实(3000-5000字)
- 风格: 严谨技术风
- 结论形式: 推荐/有条件推荐/不推荐 + 理由

## 约束条件
- 必须包含: 成本分析、安全评估、横向对标
- 可以忽略: 训练历史沿革细节
- 截止时间: {now.strftime("%Y-%m-%d")}
"""
    write_text(run_dir / "scope.md", scope)

    # Step 2: outline
    outline = """# GPT-5.6 — 章节大纲

## §1 模型全景
核心问题: GPT-5.6 的定位和分层是什么？
素材需求: 模型卡/官方发布/文档
需要生成图表: 模型层级对照表

## §2 技术拆解
核心问题: 与前代相比关键技术变化是什么？
素材需求: 官方技术说明/系统卡
需要生成图表: 架构流程图

## §3 能力评测
核心问题: 官方和第三方能力信号是否一致？
素材需求: 官方 benchmark / 第三方评测
需要生成图表: benchmark 对比柱状图

## §4 横向对标
核心问题: 与同类模型相比性价比如何？
素材需求: 竞品数据、价格数据
需要生成图表: 对比矩阵

## §5 部署分析
核心问题: 上线门槛与成本结构如何？
素材需求: API 文档、部署与价格说明
需要生成图表: 成本分层表

## §6 生态与开放性
核心问题: 安全与生态成熟度是否满足落地要求？
素材需求: 系统卡、社区与文档信息
需要生成图表: 风险分级表

## §7 结论与建议
核心问题: 是否推荐进入 PoC 与上线？
素材需求: 前六章汇总
需要生成图表: 场景推荐表
"""
    write_text(run_dir / "outline.md", outline)

    # Step 3: raw_data
    write_text(
        run_dir / "raw_data" / "official" / "release_official.md",
        "OpenAI 发布 GPT-5.6 Sol/Terra/Luna，初期 limited preview，后续扩大发布。",
    )
    write_text(
        run_dir / "raw_data" / "official" / "models_docs_official.md",
        "Models 文档列出价格、上下文窗口、工具支持。",
    )
    write_text(
        run_dir / "raw_data" / "paper" / "system_card_official.md",
        "Preparedness: Biological/Chemical High, Cybersecurity High, AI Self-Improvement below High。",
    )
    write_text(
        run_dir / "raw_data" / "benchmarks" / "official_benchmark.md",
        "官方提到 Terminal-Bench 等能力提升。",
    )
    write_text(
        run_dir / "raw_data" / "benchmarks" / "thirdparty_notes.md",
        "第三方复现口径待补齐，标注为待验证。",
    )
    write_text(
        run_dir / "raw_data" / "competitors" / "competitor_matrix.csv",
        "model,input_cost,output_cost\nGPT-5.6-Terra,2.5,15\nCompetitor-X,2.8,14\n",
    )
    write_text(
        run_dir / "raw_data" / "ecosystem" / "community_updates.md",
        "社区公告显示 7/9 扩大发布更新。",
    )
    write_text(
        run_dir / "raw_data" / "references.md",
        "- https://openai.com/index/previewing-gpt-5-6-sol/\n"
        "- https://platform.openai.com/docs/models\n"
        "- https://deploymentsafety.openai.com/gpt-5-6-preview\n"
        "- https://community.openai.com/t/introducing-gpt-5-6-series-sol-terra-and-luna-coming-july-9/1384931\n",
    )

    # Step 4: processed_data
    write_text(
        run_dir / "processed_data" / "section_1" / "info_card.md",
        "- 系列: Sol/Terra/Luna\n- 定位: 旗舰/均衡/低成本\n- 发布时间: 2026-06-26\n",
    )
    write_text(
        run_dir / "processed_data" / "section_3" / "benchmark_table.csv",
        "metric,official_signal,thirdparty_signal\nTerminal-Bench,提升,待补齐\n",
    )
    write_text(
        run_dir / "processed_data" / "section_4" / "comparison_matrix.md",
        "| 维度 | GPT-5.6 Terra | Competitor-X |\n|---|---:|---:|\n| input成本 | 2.5 | 2.8 |\n",
    )
    write_text(
        run_dir / "processed_data" / "section_5" / "deployment_table.md",
        "| 项目 | 值 |\n|---|---|\n| 上下文窗口 | 1M/400K(分层) |\n| 主要风险 | 口径不一致 |\n",
    )
    write_text(
        run_dir / "processed_data" / "section_6" / "risk_points.md",
        "- 高能力域（Cyber/Bio）带来更强治理要求\n- 需评估误拦截率\n",
    )
    write_text(run_dir / "processed_data" / "figures" / "placeholder.txt", "figure placeholders\n")
    write_text(
        run_dir / "processed_data" / "gaps.md",
        "§1 ✅ 齐全\n§2 ✅ 齐全\n§3 ⚠️ 第三方大规模复现数据不足\n§4 ✅ 齐全\n§5 ✅ 齐全\n§6 ✅ 齐全\n",
    )

    # Step 5: report
    report = f"""# GPT-5.6 外部模型调研报告（完整版）

> 生成时间：{ts}

## 执行摘要
本文的核心发现是：**GPT-5.6 适合进入 PoC，但不建议绕过验证直接全量上线。**

## §1 模型全景
数据显示，GPT-5.6 采用 Sol/Terra/Luna 三层能力分级。  
这意味着可以通过路由策略实现“高价值任务用 Sol、主流任务用 Terra、成本敏感任务用 Luna”。

## §2 技术拆解
与该发现形成对照的是，公开技术细节更多集中在能力与安全框架，而非完整训练细节。  
这意味着工程决策要更依赖实测而非仅依赖发布叙事。

## §3 能力评测
数据显示，官方 benchmark 信号积极，但第三方复现实测仍有缺口。  
这意味着在选型阶段应将官方数据视为候选信号，不应直接等同上线保证。

## §4 横向对标
数据显示，Terra 在公开口径下具备较强成本竞争力。  
这意味着它应作为默认路由候选，而 Sol 作为高复杂任务升级路径。

## §5 部署分析
需要指出，公开页面在部分价格口径上存在差异。  
这意味着上线前必须执行账单回归与配额/权限校验。

## §6 生态与开放性
数据显示，系统卡将相关高风险能力标为 High，并采用分层安全治理。  
这意味着你需要把误拦截率和降级回退能力纳入上线门槛。

## §7 结论与建议
### 适用场景推荐
| 场景 | 推荐 |
|---|---|
| 复杂推理与关键任务 | Sol |
| 主流生产任务 | Terra |
| 成本敏感与高并发 | Luna |

### 综合评级
**有条件推荐**：通过 2 周 PoC 且满足质量/成本/安全阈值后再扩大流量。
"""
    write_text(run_dir / "report.md", report)

    # Step 6: review
    review = """# 复核清单

## 事实性检查
- [x] 数字有来源
- [x] 官方与第三方区分
- [x] 未核实表述已标注

## 完整性检查
- [x] 覆盖全部章节
- [x] 缺失项已标注在 gaps.md

## 读者视角检查
- [x] 结论可直接用于选型决策
- [x] 术语解释充分

## 逻辑一致性检查
- [x] 正文支撑结论
- [x] 局限声明清晰

## 写作质量检查
- [x] 无背景套话开篇
- [x] 关键数字附“这意味着”解读

结论：通过（可进入输出步骤）
"""
    write_text(run_dir / "review_checklist.md", review)

    # Step 7: output
    write_text(run_dir / "output" / "report.md", report)
    write_minimal_pdf(run_dir / "output" / "report.pdf")
    write_text(
        run_dir / "output" / "executive_summary.md",
        "一句话结论：有条件推荐。\n核心发现：分层路由价值高、官方与第三方口径需并行验证、上线前必须完成PoC门禁。\n",
    )
    write_text(run_dir / "output" / "figures" / "placeholder.txt", "figures placeholder\n")
    write_text(run_dir / "output" / "slides" / "placeholder.txt", "slides placeholder\n")

    manifest = {
        "workflow_id": "model-report-orchestrator",
        "generated_at": now.isoformat(),
        "model_name": "GPT-5.6",
        "artifacts": [
            "scope.md",
            "outline.md",
            "raw_data/",
            "processed_data/",
            "report.md",
            "review_checklist.md",
            "output/report.md",
            "output/report.pdf",
            "output/executive_summary.md",
        ],
    }
    write_json(run_dir / "run_manifest.json", manifest)

    summary = {
        "status": "PASS",
        "workflow_id": "model-report-orchestrator",
        "run_dir": str(run_dir),
        "decision": "conditional_recommend",
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
