# skill_05_write_decide

name: MR-write-decide  
description: 外部模型调研报告 Step 5 — 基于写作包生成正文，并同步形成决策结论。

## 目标
将结构化证据转化为可读正文，并产出可执行结论。

## 职责边界
- **做**：章节写作、结论分级、行动建议。
- **不做**：新增未经核验的数据、发布归档。

## 输入
- `output/brief.json`
- `output/writing_pack.json`
- `output/asset_plan.json`
- `output/evidence_base.json`

## 输出
- `output/draft.md`
- `output/decision.json`

## 写作规则
1. 每节先给判断，再给证据，再给解释（judgment -> evidence -> implication）。
2. 关键数字必须带时间和来源标注。
3. 明确适用边界与不推荐场景。
4. 结论避免模糊表述，必须可执行。

## 执行步骤
1. 按 `writing_pack` 逐节生成正文。
2. 插入可视化占位（来自 `asset_plan`）。
3. 汇总证据和风险，输出结论分级。
4. 写出行动建议（PoC、验收指标、回滚条件）。

## 质量卡口
- 所有核心结论可追溯到证据 ID。
- `decision.json` 必须包含 `decision/rationale/risks/action_plan`。
- 结论与正文不能冲突。

## 交接
将 `output/draft.md` 与 `output/decision.json` 交给 `skill_06_review`。

