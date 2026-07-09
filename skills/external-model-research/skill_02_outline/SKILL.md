# skill_02_outline

name: MR-outline  
description: 外部模型调研报告 Step 2 — 根据 brief 生成可执行大纲，并标注每章证据需求。

## 目标
产出“可写、可采集、可复核”的结构化大纲，而不是话题列表。

## 职责边界
- **做**：章节结构、核心问题、证据需求、DoD（完成标准）。
- **不做**：真实数据采集与正文写作。

## 输入
- `output/brief.json`

## 输出
写入 `output/outline.json`，建议结构：

```json
{
  "sections": [
    {
      "id": "sec_1",
      "title": "执行摘要",
      "core_question": "最终推荐结论是什么？",
      "evidence_requirements": ["benchmark", "cost_data", "risk"],
      "planned_assets": ["table"],
      "dod": ["给出明确结论分级", "包含关键证据引用"]
    }
  ]
}
```

## 执行步骤
1. 读取 brief 中的报告类型与决策目标。
2. 选择对应章节模板并设定章节权重。
3. 为每章写 1 条核心问题。
4. 标注每章所需证据类型（数据/论文/法规/案例等）。
5. 标注每章 DoD（完成判定）。

## 质量卡口
- 每章必须有 `core_question + evidence_requirements + dod`。
- 各章节可追溯到 brief 的决策问题。
- 章节总量与 depth 相匹配（quick 不宜过多章节）。

## 交接
将 `output/outline.json` 交给 `skill_03_evidence`。

