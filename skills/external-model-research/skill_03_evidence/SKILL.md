# skill_03_evidence

name: MR-evidence  
description: 外部模型调研报告 Step 3 — 多源采集、关键 claim 交叉验证、可信度分级。

## 目标
构建结构化证据库，确保关键结论有来源、有时间、有版本。

## 职责边界
- **做**：采集、去重、核验、分级、缺口标注。
- **不做**：正文叙事与最终结论裁决。

## 输入
- `output/brief.json`
- `output/outline.json`

## 输出
- `output/evidence_base.json`
- `output/references.bib`（可选）

建议字段：
- `evidence_items[]`: `id/type/value/unit/timestamp/source/source_url/confidence`
- `claim_checks[]`: `claim/independent_sources/status`
- `data_gaps[]`: `gap/attempts/impact`

## 采集优先级
官方文档/模型卡/论文 > 第三方独立评测 > 社区实测 > 媒体转载

## 执行步骤
1. 按大纲逐章列出证据需求清单。
2. 对每条需求进行多源采集并结构化记录。
3. 同指标去重并执行交叉验证。
4. 对关键 claim 打 `verified/partially_verified/conflicted/unverified`。
5. 对数据点标注可信度等级（A+/A/B/C/D）。
6. 记录无法验证项与数据缺口。

## 质量卡口
- 每个核心 claim 至少 2 个独立来源（不足要显式标注）。
- 每个关键数字首次记录时必须有“数字+时间+来源”。
- 采信证据中 A+/A/B 比例建议 >= 80%（不足需说明原因）。
- 保留冲突数据，不允许简单删除。

## 交接
将 `output/evidence_base.json` 交给 `skill_04_orchestration`。

