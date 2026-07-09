# skill_04_orchestration

name: MR-orchestration  
description: 外部模型调研报告 Step 4 — 信息处理与编排：证据映射、可视化规划、写作输入包生成。

## 目标
在写正文前完成“先编排后写作”，防止资料堆砌。

## 职责边界
- **做**：证据映射章节、图表/表格/流程图规划、段落级写作包。
- **不做**：完整正文生成与终稿润色。

## 输入
- `output/outline.json`
- `output/evidence_base.json`

## 输出
- `output/section_mapping.json`
- `output/asset_plan.json`
- `output/writing_pack.json`

## 执行步骤
1. 将证据按章节映射，区分主证据/辅证据。
2. 标记冲突证据与不确定证据。
3. 决定表达形式：正文、表格、图表、流程图、时间线。
4. 生成可视化资产计划（标题、字段、来源证据 ID）。
5. 生成段落级写作包（判断句、证据句、解读句）。

## 质量卡口
- 每章至少 1 条高可信主证据。
- 每个核心判断必须绑定证据 ID。
- 可视化资产字段必须可回溯到证据来源。
- 存在冲突证据时必须在写作包中显式提示。

## 交接
将 `output/writing_pack.json` 与 `output/asset_plan.json` 交给 `skill_05_write_decide`。

