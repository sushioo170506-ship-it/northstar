# skill_06_review

name: MR-review  
description: 外部模型调研报告 Step 6 — 执行事实、逻辑、一致性、完整性与可用性复核。

## 目标
把“可读初稿”升级成“可交付终稿候选”，通过质量门禁。

## 职责边界
- **做**：问题识别、分级、修订建议、修订稿输出。
- **不做**：最终发布与格式转换。

## 输入
- `output/draft.md`
- `output/decision.json`
- `output/outline.json`
- `output/evidence_base.json`

## 输出
- `output/review_report.json`
- `output/revised_draft.md`

## 复核维度
1. 事实性：数据、日期、来源、版本是否准确。
2. 一致性：结论是否由正文证据支持。
3. 完整性：是否覆盖大纲必答项。
4. 可用性：目标读者能否据此做决策。
5. 风险披露：是否遗漏关键限制条件。

## 严重级别
- `critical`: 事实错误/关键结论无证据/结论与证据冲突。
- `major`: 逻辑链不完整、章节漏项、风险披露不足。
- `minor`: 语义可优化、表达冗余、格式细节。

## 质量卡口
- `critical` 必须为 0 才能进入发布。
- `major` > 0 时必须返修后再审。

## 回路规则
- 表达和逻辑问题 -> 回 `skill_05_write_decide`
- 证据缺口问题 -> 回 `skill_03_evidence`

