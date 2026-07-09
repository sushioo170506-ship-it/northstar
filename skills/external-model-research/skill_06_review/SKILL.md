# mr-step6-review

name: mr-step6-review
description: Step 6 — 按 rubric 进行最终复核，输出量化评分与回退建议。

## 定位与作用
本步骤是“发布前闸门层”。  
它把主观“看起来不错”转为客观“是否达标”，确保报告能被复用和审计。

## 输入
- `archive/report.md`
- `archive/scope.md`
- `archive/outline.md`
- `skills/external-model-research/model-report-rubric.yaml`

## 输出
- `archive/review_checklist.md`

## 复核框架
按 rubric 维度评分并给出扣分理由：
- problem_framing
- evidence_traceability
- technical_depth
- benchmark_and_comparison
- governance_and_safety
- limitations_and_risks
- decision_actionability
- structure_and_readability
- reproducibility

## 通过阈值
- 总分 >= 90；
- evidence_traceability >= 18；
- logic_consistency（映射逻辑一致性检查） >= 18；
- decision_actionability >= 18。

## 一票否决项
- 核心结论无证据编号/来源链接；
- 对比口径不一致且未声明；
- 结论缺少“定位/能力/场景/边界/启示”；
- 风险章节无“风险-影响-缓解”映射；
- 缺少评分卡或 90 天路线图；
- 长篇未达到表图与文献门槛。

## 输出格式要求
`review_checklist.md` 必须包含：
1. 评分总览（总分/是否通过）
2. 维度得分与扣分说明
3. 一票否决检查
4. 回退建议（Step2/3/4/5）
5. 最终判定（PASS/FAIL）

## 回退策略
- 事实性问题 -> 回 Step3；
- 结构与完整性问题 -> 回 Step2 或 Step4；
- 逻辑/可读性/结论表达问题 -> 回 Step5。

## 质量卡口
- 已按 rubric 输出总分与维度得分；
- 关键维度阈值与一票否决检查已执行；
- 回退建议具体到目标步骤；
- 最终 PASS/FAIL 结论明确且可追溯。

## 交接
通过后将 `archive/report.md` 与 `archive/review_checklist.md` 交给 `mr-step7-output`。

