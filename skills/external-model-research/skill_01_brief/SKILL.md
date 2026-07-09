# skill_01_brief

name: MR-brief  
description: 外部模型调研报告 Step 1 — 明确读者、决策任务与交付约束，产出报告企划。

## 目标
将用户输入的模型名，转成可执行的调研任务定义（不是直接开写正文）。

## 职责边界
- **做**：任务定调、读者画像、决策问题定义、输出格式约束。
- **不做**：数据采集、内容写作、评分打分。

## 输入
- `model_name`（必填）
- `report_type`（默认 `tech-selection`）
- `audience`（默认 `tech-lead`）
- `decision_goal`（可选）
- `depth`（`quick/standard/deep`）
- `output_formats`（默认 `md,pdf`）
- `time_window`（默认 `last_12_months`）

## 输出
写入 `output/brief.json`，建议结构：

```json
{
  "model_name": "xxx",
  "report_type": "tech-selection",
  "audience": "tech-lead",
  "decision_questions": [
    "是否可用于生产环境主力方案？",
    "相对现有方案的收益与风险是什么？"
  ],
  "conclusion_format": "recommend|conditional_recommend|not_recommend",
  "risk_preference": "balanced",
  "out_of_scope": ["不做内部私有数据效果验证"]
}
```

## 执行步骤
1. 识别模型歧义（同名版本、开源/闭源、发布时间）。
2. 明确“谁看、看完做什么、最担心什么”。
3. 生成最多 3 个可决策问题。
4. 设定结论表达格式和交付格式。
5. 明确不评估边界并输出 brief。

## 质量卡口
- 必须有明确决策动作（看完报告后要做的事）。
- 必须有结论表达格式。
- 必须有不评估边界（避免范围失控）。

## 交接
将 `output/brief.json` 交给 `skill_02_outline`。

