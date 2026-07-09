# mr-step4-process

name: mr-step4-process
description: Step 4 — 将原始素材加工为可写作、可复核、可决策的证据包。

## 定位与作用
本步骤是“证据加工层”。  
它把 Step3 的散点素材转为结构化内容块，确保 Step5 可以直接写作而非临时拼接。

## 输入
- `archive/raw_data/`
- `archive/outline.md`
- `skills/external-model-research/model-report-playbook.md`

## 输出
写入 `archive/processed_data/`，重点产物包括：
- 分章节证据块（`section_*`）
- 图表规格（`figures/`）
- 核心表格（`tables/`）
- 证据索引（`evidence_map.csv`、`evidence_ledger.csv`）
- 缺口报告（`gaps.md`）

## 必备中间产物（长篇）
- `benchmark_master_table.md`
- `competitor_matrix.md`
- `risk_register.md`
- `decision_scorecard.md`
- `roadmap_90d.md`
- `tech_route_3layer.md`
- `capability_governance_dualtrack.md`

## 加工动作
1. 按章节归位素材；
2. 将关键参数、benchmark、对标信息表格化；
3. 生成图表规格与要点卡；
4. 建立 claim->source 证据回链；
5. 输出缺失分级（P0/P1/P2）。

## 差异化说明
本步骤的核心价值是“把信息变成写作资产”，不是重复采集。  
所有高层判断都应能在本步骤找到对应证据块与回链记录。

## 质量卡口
- 表格 >= 12、图表规格 >= 4（长篇）；
- `evidence_map` 与 `evidence_ledger` 字段完整；
- `risk_register` 至少包含 risk/impact/mitigation/owner；
- 若出现 P0 缺失，必须回退 Step3 补采。

## 交接
将 `archive/processed_data/` 交给 `mr-step5-write`。

