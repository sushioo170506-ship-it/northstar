#!/usr/bin/env python3
"""Generate a richer full example run for model-report-orchestrator (GPT-5.6)."""

from __future__ import annotations

import json
import shutil
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
        b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 620 360]/Contents 4 0 R>>endobj\n"
        b"4 0 obj<</Length 78>>stream\nBT /F1 16 Tf 72 220 Td (GPT-5.6 Full Report - Data Rich Version) Tj ET\nendstream endobj\n"
        b"xref\n0 5\n0000000000 65535 f \n"
        b"trailer<</Size 5/Root 1 0 R>>\nstartxref\n305\n%%EOF\n"
    )
    path.write_bytes(content)


def build_report(ts: str) -> str:
    return f"""# GPT-5.6 外部模型调研报告（数据增强版）

> 生成时间：{ts}  
> 工作流：model-report-orchestrator（7步）  
> 报告类型：技术选型  
> 数据窗口：2026-06-26 至 2026-07-09 公共信息

---

## Executive Summary

**一句话结论：有条件推荐（Conditional Recommend）。**

GPT-5.6（Sol/Terra/Luna）在“能力分层 + 成本分层 + 安全治理”上具备明确工程可用性，适合进入 PoC 选型池；但当前公开信息仍存在三类不确定性：  
1) 发布状态与可用性信息存在渠道更新不同步；  
2) Luna 价格口径在不同官方页面出现差异；  
3) 第三方独立复现实测仍不足，无法直接替代内部验证。

---

## §1 模型全景（模型是什么）

### 1.1 基础档案卡（信息卡）

| 字段 | 值 | 来源 |
|---|---|---|
| 系列名称 | GPT-5.6（Sol / Terra / Luna） | S1 |
| 首次公开时间 | 2026-06-26 | S1 |
| 初期发布形态 | limited preview（API/Codex，受限伙伴） | S1 |
| 后续公开信号 | 开发者社区更新提到 7/9 公共发布 | S5 |
| 官方文档状态提示 | models 页面仍出现 preview/broad soon 口径 | S2 |
| 定价（发布页） | Sol 5/30, Terra 2.5/15, Luna 1/6 ($/1M in/out) | S1 |
| 定价（models页快照） | Luna 0.75/4.5（与发布页存在差异） | S2 |
| 上下文窗口（models页快照） | Sol/Terra 1M，Luna 400K | S2 |
| 最大输出 | 128K（三档） | S2 |
| 工具支持 | Functions/Web search/File search/Computer use | S2 |

> 判断：GPT-5.6 不是“单一升级版”，而是“可路由的三档能力产品线”。  
> 这意味着后续决策应是“任务路由设计”，而不是“单模型二选一”。

---

## §2 技术拆解（为什么强）

### 2.1 官方可见技术变化（可验证）

- 引入 `max` reasoning effort（给 Sol 更长推理时间）[S1]。  
- 引入 `ultra` mode（通过 subagents 加速复杂任务）[S1]。  
- Prompt caching 策略更明确：  
  - cache write 计费为 uncached input 的 1.25x  
  - cache read 仍有 90% discount  
  - cache minimum life: 30 min [S1]

### 2.2 安全治理栈（可验证）

系统卡与发布页共同描述了分层 safeguard：  
模型级拒绝策略 -> 实时分类器 -> 账户级审查 -> 分级访问 [S1][S3]。

### 2.3 架构表达图（Mermaid）

```mermaid
flowchart LR
    A[User Request] --> B[Model-level policy boundary]
    B --> C[Real-time misuse classifiers]
    C --> D[Reasoning review for high-risk cases]
    D --> E[Allow / Block]
    E --> F[Account-level monitoring]
```

> 判断：技术增益和安全治理是“绑定发布”的，不是纯性能升级。  
> 这意味着接入成本不只在 token 成本，也在策略适配和误拦截治理。

---

## §3 能力评测（有多少硬证据）

### 3.1 官方能力信号（含数字）

| 维度 | 指标/描述 | 数值 | 备注 | 来源 |
|---|---|---:|---|---|
| 生物能力 | Virology Capabilities Test | 53.5% | 社区公告引用官方口径 | S5 |
| 生物能力 | Molecular Biology | 60.0% | 同上 | S5 |
| 生物能力 | Human Pathogen Capabilities | 68.4% | 同上 | S5 |
| 生物能力 | World-Class Bio | 68.3% | 同上 | S5 |
| 网络安全效率 | ExploitBench token usage | ~1/3 vs 对比前沿系统 | 比较对象未完全公开同口径细节 | S1/S5 |
| 代码任务 | Terminal-Bench 2.1 | “new SOTA” | 未给统一可复算分值 | S1 |

### 3.2 第三方独立验证状态

| 维度 | 独立复现成熟度 | 现状 |
|---|---|---|
| 通用 benchmark（MMLU/GSM8K/HumanEval） | 中 | 有散点信息，无统一同口径基线 |
| 长链路 agent 任务 | 低-中 | 多为厂商/社区个案 |
| 双用途安全任务 | 中 | 系统卡信息较全，但公开可复算样本有限 |

> 判断：目前“可证据化能力”以官方链路为主，第三方同口径复现不足。  
> 这意味着你可以做 PoC 决策，但不应做“跳过 PoC 直接全量上线”的决策。

---

## §4 横向对标（能力/成本/不确定性）

### 4.1 成本分层对比（每 1M token，in/out）

| 模型层 | 发布页口径 | models页口径 | 备注 |
|---|---|---|---|
| Sol | 5 / 30 | 5 / 30 | 一致 |
| Terra | 2.5 / 15 | 2.5 / 15 | 一致 |
| Luna | 1 / 6 | 0.75 / 4.5 | 存在差异，需账单验证 |

### 4.2 典型月负载成本情景（100M input + 20M output）

> 计算方式：`总成本 = input_mtok * input_price + output_mtok * output_price`

| 路由档位 | 按发布页口径成本($) | 按models页口径成本($) |
|---|---:|---:|
| Sol | 1100 | 1100 |
| Terra | 550 | 550 |
| Luna | 220 | 165 |

> 判断：Terra 在成本上可作为“默认主路由”候选，Sol 用于高价值复杂任务升级。  
> 这意味着“默认 Terra + 条件升级 Sol + 成本敏感落到 Luna”的三层路由具备经济性。

### 4.3 时间线图（Mermaid）

```mermaid
timeline
    title GPT-5.6 发布与可用性时间线
    2026-06-26 : 官方发布 GPT-5.6（limited preview）
    2026-06-26 : API/Codex 受限伙伴接入
    2026-07-08 : 开发者社区更新提到 7/9 公共发布
    2026-07-09 : 文档口径仍有 preview/coming soon 残留
```

---

## §5 部署分析（能不能落）

### 5.1 部署参数表（公共口径）

| 维度 | Sol | Terra | Luna | 来源 |
|---|---|---|---|---|
| Context window | 1M | 1M | 400K | S2 |
| Max output | 128K | 128K | 128K | S2 |
| Latency label | Fast | Fast | Faster | S2 |
| Tooling | Functions/Web/File/Computer use | 同左 | 同左 | S2 |

### 5.2 上线门禁（建议）

| 门禁项 | 验收阈值 | 是否必须 |
|---|---|---|
| 账号可用性（区域+权限） | `/v1/models` 可见目标模型ID | 是 |
| 成本回归 | 计划成本与账单偏差 < 5% | 是 |
| 质量收益 | 关键任务质量提升 >= 8% 或同质量降本 >= 20% | 是 |
| 延迟 | P95 不劣于现网基线 10% 以上 | 是 |
| 误拦截率 | 在业务阈值内并有回退机制 | 是 |

### 5.3 路由建议

| 任务类型 | 默认档位 | 升级/回退策略 |
|---|---|---|
| 高复杂推理、关键决策 | Sol | 失败回退 Terra |
| 日常生产主任务 | Terra | 高难样本升级 Sol |
| 成本敏感批处理 | Luna | 质量不达标回退 Terra |

---

## §6 生态与开放性（风险在哪里）

### 6.1 Preparedness 关键信息（官方）

| 类别 | 等级 | 说明 |
|---|---|---|
| Biological/Chemical | High | 系统卡明确标注 |
| Cybersecurity | High | 系统卡明确标注 |
| AI Self-Improvement | below High | 系统卡明确标注 |
| Critical cyber threshold | 未跨越（测试条件下） | 系统卡说明无法自主产出关键级 exploit |

### 6.2 风险登记表（含缓解）

| 风险 | 严重度 | 触发信号 | 缓解动作 |
|---|---|---|---|
| 发布口径不同步 | 中 | 页面状态不一致 | 以账号权限和实测可用性为准 |
| Luna 定价差异 | 中 | 1/6 vs 0.75/4.5 | 以账单导出做成本回归 |
| 第三方复现不足 | 中-高 | 公开同口径基线不足 | 建立内部 benchmark 回归套件 |
| 安全误拦截 | 中-高 | 双用途请求误拒 | 增加人工复核与回退路由 |
| 供应商锁定 | 中 | 单供应商依赖升高 | 维护 GPT-5.5/其他模型兜底 |

---

## §7 结论与建议

### 7.1 综合评估

从“能力信号、成本分层、治理成熟度”看，GPT-5.6 值得进入 PoC。  
从“口径一致性、独立复现、上线风险”看，不建议直接全量切换。

### 7.2 场景推荐

| 场景 | 推荐 | 理由 |
|---|---|---|
| 复杂推理与高价值任务 | Sol | 能力上限更高，适配关键任务 |
| 通用主流程 | Terra | 成本-能力平衡最好 |
| 高并发低成本任务 | Luna | 单位成本最低，但需严格质量阈值 |

### 7.3 综合评级

**有条件推荐（Conditional Recommend）**  
前提：通过两周 PoC + 通过账单回归 + 通过安全误拦截评估 + 建立回退机制。

---

## 附录A：证据台账（摘录）

| ID | 证据 | 日期 | 级别 |
|---|---|---|---|
| S1 | OpenAI 发布页（previewing gpt-5.6） | 2026-06-26 | A+ |
| S2 | OpenAI models 文档页 | 2026-07-09 访问 | A |
| S3 | GPT-5.6 Preview System Card | 2026-06-26 | A+ |
| S4 | Help Center 预览说明 | 2026-07-09 访问 | B |
| S5 | OpenAI Developer Community 更新 | 2026-07-08 | A |
| S6 | Reuters 时间线（转载） | 2026-07-07 | B |

"""


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    run_dir = repo / "archive" / "runs" / "gpt-5.6-full"
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y-%m-%d %H:%M UTC")
    date_only = now.strftime("%Y-%m-%d")

    # Step 1: scope
    scope = f"""# 报告企划书 — GPT-5.6

## 读者画像
- 主要读者: 技术选型团队、平台架构组、安全治理组
- 决策类型: 选型（是否纳入生产候选）
- 阅读场景: 周会评审 + 立项决策附件
- 核心担忧: 数据口径不一致导致误判；结论不可执行

## 报告参数
- 报告类型: 技术选型
- 篇幅: 长篇详实(3000-5000字)
- 风格: 严谨技术风 + 决策可执行
- 结论形式: 推荐/有条件推荐/不推荐 + 触发条件

## 约束条件
- 必须包含: 定量数据表、对标矩阵、风险表、PoC门禁
- 可以忽略: 未公开训练实现细节
- 截止时间: {date_only}
"""
    write_text(run_dir / "scope.md", scope)

    # Step 2: outline
    outline = """# GPT-5.6 — 章节大纲（技术选型骨架）

## §1 模型全景
核心问题: 模型家族定位与公开状态是什么？
篇幅权重: 12%
素材需求: 官方发布、模型文档、社区官方更新
图表需求: 模型信息卡

## §2 技术拆解
核心问题: 可验证的技术变化是什么？
篇幅权重: 14%
素材需求: 发布页、系统卡
图表需求: 安全栈流程图

## §3 能力评测
核心问题: 能力信号到底有多硬？
篇幅权重: 18%
素材需求: 官方 benchmark 信号、第三方验证状态
图表需求: 能力证据表

## §4 横向对标
核心问题: 成本/能力/不确定性如何平衡？
篇幅权重: 18%
素材需求: 分层定价、时间线、竞品成本样本
图表需求: 定价对比、时间线

## §5 部署分析
核心问题: 上线门槛和运行策略是什么？
篇幅权重: 16%
素材需求: 模型规格、工具能力、门禁项
图表需求: 部署参数表、路由表

## §6 生态与开放性
核心问题: 安全与治理风险如何量化？
篇幅权重: 12%
素材需求: 系统卡、文档、媒体时间线
图表需求: 风险登记表

## §7 结论与建议
核心问题: 给什么结论、在什么前提下执行？
篇幅权重: 10%
素材需求: 前六章汇总
图表需求: 场景推荐表
"""
    write_text(run_dir / "outline.md", outline)

    # Step 3: raw_data
    write_text(
        run_dir / "raw_data" / "official" / "release_official.md",
        """来源: https://openai.com/index/previewing-gpt-5-6-sol/
时间: 2026-06-26
关键信息:
- GPT-5.6 family: Sol/Terra/Luna
- 初期 limited preview（API/Codex，trusted partners）
- 价格: Sol 5/30, Terra 2.5/15, Luna 1/6 ($/1M in/out)
- cache write 1.25x uncached input
- cache read 90% discount
- cache minimum life 30 minutes
- Cerebras: up to 750 tokens/s (July, select customers)
""",
    )
    write_text(
        run_dir / "raw_data" / "official" / "models_docs_snapshot.md",
        """来源: https://platform.openai.com/docs/models
时间: 2026-07-09
关键信息:
- 页面提示: GPT-5.6 preview to select trusted partners, broad availability coming soon
- Sol/Terra/Luna 价格与规格展示
- 可见口径: Luna 0.75/4.5 ($/1M in/out), context 400K
- Sol/Terra context 1M, max output 128K
- 工具: Functions/Web search/File search/Computer use
""",
    )
    write_text(
        run_dir / "raw_data" / "official" / "developer_community_update.md",
        """来源: https://community.openai.com/t/introducing-gpt-5-6-series-sol-terra-and-luna-coming-july-9/1384931/28
时间: 2026-07-08
关键信息:
- UPDATE: GPT-5.6 Sol/Terra/Luna public launch on July 9
""",
    )
    write_text(
        run_dir / "raw_data" / "paper" / "system_card_extract.md",
        """来源: https://deploymentsafety.openai.com/gpt-5-6-preview
时间: 2026-06-26
关键信息:
- Preparedness tracked categories:
  - High in Biological and Chemical
  - High in Cybersecurity
  - below High in AI Self-Improvement
- Rule-out note: under tested configs, no functional critical-severity exploit was produced
""",
    )
    write_text(
        run_dir / "raw_data" / "benchmarks" / "official_signals.csv",
        "metric,value,source\n"
        "SecureBio Virology,53.5,S5\n"
        "SecureBio Molecular Biology,60.0,S5\n"
        "SecureBio Human Pathogen,68.4,S5\n"
        "SecureBio World-Class Bio,68.3,S5\n"
        "ExploitBench token usage ratio,~0.33,S1/S5\n"
        "Terminal-Bench 2.1,New SOTA (no public score),S1\n",
    )
    write_text(
        run_dir / "raw_data" / "benchmarks" / "thirdparty_validation_notes.md",
        """第三方验证现状:
- 存在公开讨论与零散案例
- 缺少统一同口径、可复算的大规模复现报告
结论: 需要内部 PoC 作为主验证路径
""",
    )
    write_text(
        run_dir / "raw_data" / "competitors" / "pricing_competitor_sample.csv",
        "model,input_price,output_price,source\n"
        "GPT-5.6 Sol,5,30,S1\n"
        "GPT-5.6 Terra,2.5,15,S1\n"
        "GPT-5.6 Luna release,1,6,S1\n"
        "GPT-5.6 Luna docs,0.75,4.5,S2\n",
    )
    write_text(
        run_dir / "raw_data" / "ecosystem" / "media_timeline.md",
        """来源: Reuters syndicated timeline (S6)
用途: 交叉确认发布节奏、监管背景、扩大发布时间线
可信度: B（媒体层）
""",
    )
    write_text(
        run_dir / "raw_data" / "references.md",
        """| ID | 来源 | 类型 | 可信度 |
|---|---|---|---|
| S1 | https://openai.com/index/previewing-gpt-5-6-sol/ | 官方发布页 | A+ |
| S2 | https://platform.openai.com/docs/models | 官方文档页 | A |
| S3 | https://deploymentsafety.openai.com/gpt-5-6-preview | 官方系统卡 | A+ |
| S4 | https://help.openai.com/en/articles/20001325-a-preview-of-gpt-56-sol-terra-and-luna | 官方帮助中心 | B |
| S5 | https://community.openai.com/t/introducing-gpt-5-6-series-sol-terra-and-luna-coming-july-9/1384931 | 官方社区公告 | A |
| S6 | https://www.investing.com/news/stock-market-news/openai-gets-us-approval-for-broad-gpt56-rollout-axios-reports-4780650 | Reuters转载 | B |
""",
    )

    # Step 4: processed_data
    write_text(
        run_dir / "processed_data" / "section_1" / "info_card.md",
        """| 维度 | Sol | Terra | Luna | 备注 |
|---|---|---|---|---|
| 定位 | 旗舰能力 | 均衡主力 | 低成本高速度 | 三档路由 |
| input $/1M | 5 | 2.5 | 1 或 0.75 | 来源口径差异 |
| output $/1M | 30 | 15 | 6 或 4.5 | 来源口径差异 |
| context | 1M | 1M | 400K | docs snapshot |
| max output | 128K | 128K | 128K | docs snapshot |
""",
    )
    write_text(
        run_dir / "processed_data" / "section_2" / "tech_highlights.md",
        """- `max` reasoning effort: 更高推理计算预算（S1）
- `ultra` mode: subagents 协同处理复杂任务（S1）
- layered safeguards: model-level -> real-time classifiers -> account-level review（S1/S3）
- cache policy: write 1.25x, read 90% discount, min life 30m（S1）
""",
    )
    write_text(
        run_dir / "processed_data" / "section_2" / "architecture_diagram.mmd",
        """flowchart LR
A[Request] --> B[Model Policy]
B --> C[Realtime Classifier]
C --> D[High-risk Reasoning Review]
D --> E[Allow or Block]
E --> F[Account-level Monitoring]
""",
    )
    write_text(
        run_dir / "processed_data" / "section_3" / "benchmark_table.csv",
        "metric,value,unit,source,confidence\n"
        "SecureBio Virology,53.5,%,S5,B\n"
        "SecureBio Molecular Biology,60.0,%,S5,B\n"
        "SecureBio Human Pathogen,68.4,%,S5,B\n"
        "SecureBio World-Class Bio,68.3,%,S5,B\n"
        "ExploitBench token usage ratio,0.33,ratio,S1/S5,B\n",
    )
    write_text(
        run_dir / "processed_data" / "section_4" / "cost_scenario_table.csv",
        "tier,cost_release_usd,cost_docs_usd,assumption\n"
        "Sol,1100,1100,100M input + 20M output\n"
        "Terra,550,550,100M input + 20M output\n"
        "Luna,220,165,100M input + 20M output\n",
    )
    write_text(
        run_dir / "processed_data" / "section_4" / "comparison_matrix.md",
        """| 维度 | Sol | Terra | Luna | 工程建议 |
|---|---|---|---|---|
| 能力上限 | 高 | 中高 | 中 | 高价值任务优先 Sol |
| 单位成本 | 高 | 中 | 低 | 默认 Terra，低价值落 Luna |
| 不确定性 | 中 | 中 | 中高（定价口径差异） | Luna需账单校验 |
""",
    )
    write_text(
        run_dir / "processed_data" / "section_5" / "deployment_table.csv",
        "field,sol,terra,luna,source\n"
        "context_window,1M,1M,400K,S2\n"
        "max_output,128K,128K,128K,S2\n"
        "latency_label,Fast,Fast,Faster,S2\n"
        "tool_support,Functions+Web+File+Computer,Functions+Web+File+Computer,Functions+Web+File+Computer,S2\n",
    )
    write_text(
        run_dir / "processed_data" / "section_5" / "deployment_gate_checklist.md",
        """- [ ] 模型可用性：目标账号可见 model ID
- [ ] 成本回归：计划 vs 账单偏差 < 5%
- [ ] 质量门槛：关键任务 >= baseline+8% 或等质量降本 >=20%
- [ ] 性能门槛：P95 不劣于基线 10% 以上
- [ ] 安全门槛：误拦截率在业务可接受区间
""",
    )
    write_text(
        run_dir / "processed_data" / "section_6" / "risk_register.csv",
        "risk,severity,trigger,mitigation\n"
        "release_status_desync,medium,page update mismatch,use account-level availability as source of truth\n"
        "luna_price_mismatch,medium,1/6 vs 0.75/4.5,reconcile with billing exports\n"
        "independent_eval_gap,medium_high,lack of unified third-party reruns,run internal benchmark suite\n"
        "guardrail_false_positive,medium_high,dual-use prompt blocks,add fallback and human review\n"
    )
    write_text(
        run_dir / "processed_data" / "section_7" / "scoring_table.csv",
        "dimension,weight,score,weighted_score,notes\n"
        "Capability signal,0.30,7.5,2.25,official signals strong but third-party gap\n"
        "Cost efficiency,0.25,8.0,2.00,terra/luna show strong economics\n"
        "Availability certainty,0.20,6.0,1.20,channel update desync exists\n"
        "Safety governance,0.15,8.0,1.20,layered safeguards and system card details\n"
        "Ecosystem readiness,0.10,7.0,0.70,tooling documented with rollout caveats\n"
        "Total,1.00,0.0,7.35,conditional recommend zone\n",
    )
    write_text(
        run_dir / "processed_data" / "figures" / "timeline.mmd",
        """timeline
title GPT-5.6 rollout timeline
2026-06-26 : official release (limited preview)
2026-07-08 : dev community update for July 9 public launch
2026-07-09 : docs still show preview/broad-soon language
""",
    )
    write_text(
        run_dir / "processed_data" / "figures" / "pricing_tiers.mmd",
        """flowchart LR
S[Sol: 5/30] --> T[Terra: 2.5/15]
T --> L[Luna: 1/6 or 0.75/4.5]
""",
    )
    write_text(
        run_dir / "processed_data" / "figures" / "risk_flow.mmd",
        """flowchart TD
A[Need production decision] --> B[Run PoC gate checks]
B --> C{All gates pass?}
C -- Yes --> D[Gradual rollout]
C -- No --> E[Stay on fallback model]
""",
    )
    write_text(
        run_dir / "processed_data" / "figures" / "plot_benchmark.py",
        """# Optional plotting script for benchmark_table.csv
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("section_3/benchmark_table.csv")
plt.bar(df["metric"], df["value"])
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig("figures/benchmark_bar.png", dpi=200)
""",
    )
    write_text(
        run_dir / "processed_data" / "gaps.md",
        """§1 模型全景 — ✅ 齐全
§2 技术拆解 — ✅ 齐全
§3 能力评测 — ⚠️ 缺少统一第三方可复算基线
§4 横向对标 — ✅ 齐全
§5 部署分析 — ✅ 齐全（待账户实测）
§6 生态与开放性 — ✅ 齐全
§7 结论与建议 — ✅ 齐全

严重缺口判定: 否（无需回退 Step 3），但 §3 必须在 PoC 阶段补齐内部复现数据。
""",
    )

    # Step 5: report
    report = build_report(ts)
    write_text(run_dir / "report.md", report)

    # Step 6: review
    review = """# 复核清单（mr-step6-review）

## 维度 1：事实性检查
- [x] 所有关键数字附来源（S1-S6）
- [x] 官方与第三方口径区分
- [x] 不确定口径已显式标注（Luna价格）
- [x] 引用格式统一

## 维度 2：完整性检查
- [x] 覆盖 §1-§7 全部章节
- [x] 每章回答核心问题
- [x] 数据缺失已在 gaps.md 标注
- [x] 结论包含场景化推荐

## 维度 3：读者视角检查
- [x] 术语有解释，目标读者可读
- [x] 结论可转化为决策动作
- [x] 篇幅达到“详实报告”标准

## 维度 4：逻辑一致性检查
- [x] §1-§6 分析支撑 §7 结论
- [x] 局限声明充分
- [x] 对比口径差异已披露

## 维度 5：写作质量检查
- [x] 开篇非背景套话
- [x] 关键数字后有解读
- [x] 结论明确不含空泛措辞

结论：通过（PASS）  
修正建议：PoC 阶段补齐 §3 的统一第三方可复算基线。
"""
    write_text(run_dir / "review_checklist.md", review)

    # Step 7: output
    write_text(run_dir / "output" / "report.md", report)
    write_minimal_pdf(run_dir / "output" / "report.pdf")
    write_text(
        run_dir / "output" / "executive_summary.md",
        """# Executive Summary — GPT-5.6

一句话结论：**有条件推荐**，可入 PoC，不建议直接全量上线。

核心发现：
1. GPT-5.6 形成 Sol/Terra/Luna 三档能力与成本分层，具备路由价值。  
2. 官方能力信号较强，但第三方可复算同口径验证仍不足。  
3. Luna 在公开渠道存在价格口径差异（1/6 vs 0.75/4.5），需账单回归确认。  
4. 系统卡显示 Cyber/Bio 均为 High，安全治理要求应作为上线门槛。  
5. 推荐默认 Terra，复杂任务升级 Sol，成本敏感任务使用 Luna 并设置质量阈值。

推荐意见：完成两周 PoC（质量、成本、延迟、安全四项门禁）后逐步放量。
""",
    )
    # publish figure assets
    for figure_name in ("timeline.mmd", "pricing_tiers.mmd", "risk_flow.mmd"):
        content = (run_dir / "processed_data" / "figures" / figure_name).read_text(encoding="utf-8")
        write_text(run_dir / "output" / "figures" / figure_name, content)
    write_text(run_dir / "output" / "slides" / "placeholder.txt", "slides to be generated from report sections\n")

    manifest = {
        "workflow_id": "model-report-orchestrator",
        "run_name": "gpt-5.6-full",
        "generated_at": now.isoformat(),
        "model_name": "GPT-5.6",
        "data_cutoff": date_only,
        "artifact_summary": {
            "tables": 8,
            "figure_specs": 3,
            "sections": 7,
            "source_count": 6,
        },
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
            "output/figures/",
        ],
    }
    write_json(run_dir / "run_manifest.json", manifest)

    summary = {
        "status": "PASS",
        "workflow_id": "model-report-orchestrator",
        "run_dir": str(run_dir),
        "decision": "conditional_recommend",
        "tables": 8,
        "figure_specs": 3,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
