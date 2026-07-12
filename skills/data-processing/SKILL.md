---
name: data-processing
description: 工作流数据处理阶段 — 生成论断账本、提取数字、三角验证、证据分级和可选数据锚点评分。
license: MIT
version: 1.0.0
---

# Data Processing

## 职责边界

只处理已采集数据，不搜索新来源、不决定文章章节、不撰写正文、不凭主观印象补分。

## 输入与输出

- INPUT：research、evidence_governance、issue_tree、outline。
- OUTPUT：`processed_research_data`。
- 核心字段：claims、data_points、evidence_grades、triangulation、scoring。

## Claim Ledger 规则

每条 claim 必须含 claim_id、原子陈述、source_ids、独立来源数、issue_ids、section_ids、
critical、A+/A/B/C/D 级、confidence、conflicts、status。

- A+：至少两个独立来源一致；
- A：多源且至少一个独立来源；
- B：单一可追溯独立来源；
- C：仅利益相关方或弱来源；
- D：不可追溯，不得支撑核心判断。

关键论断必须有至少两个独立来源且无未解决冲突。冲突不得平均消除，应保留双方口径。

## 评分规则

评分仅在配置 5–10 个候选和 4–6 个维度时适用。每维度必须提供权重、实测 values、
10 分锚点、5 分锚点、方向和来源。公式：

`score = clamp(5 + 5 × (value-anchor_5)/(anchor_10-anchor_5), 0, 10)`

缺数据记为 null；禁止推断补齐。未配置时输出 `not_applicable`，而不是生成主观排名。

## MUST / MUST NOT

- MUST：提取数字上下文、时间和来源；记录冲突；输出评分边界。
- MUST NOT：把来源摘要当成已验证事实；用模型印象打分；跨品类比较综合分。
- ON_FAIL：论断映射问题退回 data_processing；来源不足退回 research；红线退回
  evidence_governance。
