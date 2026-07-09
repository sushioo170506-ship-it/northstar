# mr-step6-review

name: mr-step6-review
description: Step 6 — 按量化标准复核报告质量，执行一票否决并给出明确回退路径。

## 作用
输出前最后一道关。复核不是“再读一遍”，而是按固定清单逐项检查。

## 输入
- `archive/report.md`
- `archive/scope.md`
- `archive/outline.md`（用于核对完整性）
- `skills/external-model-research/model-report-rubric.yaml`（评分标准）

## 输出
- `archive/review_checklist.md`（逐项通过/不通过 + 修正建议）

## 复核维度
1. **事实性检查**：数字有来源；官方与第三方区分；无未核实措辞；引用格式统一。  
2. **完整性检查**：覆盖全部章节；回答章节核心问题；缺失数据有显式标注；结论具体。  
3. **读者视角检查**：目标读者能看懂、能决策、篇幅符合 scope 约束。  
4. **逻辑一致性检查**：正文支持结论；局限声明充分；对比口径公平。  
5. **写作质量检查**：无套话；开篇合规；核心结论短句；无纯过渡段。
6. **信息密度检查**：来源、表图、benchmark、竞品、文献数量达标。
7. **决策可执行性检查**：有评分卡、路线图、风险映射与场景边界。

## 量化评分（新增）
按 `model-report-rubric.yaml` 维度打分（总分 100），并输出每维扣分理由：
- problem_framing
- evidence_traceability
- technical_depth
- benchmark_and_comparison
- governance_and_safety
- limitations_and_risks
- decision_actionability
- structure_and_readability
- reproducibility
- 通过阈值：
  - 总分 >= 90
  - 且 evidence_traceability >= 18
  - 且 logic_consistency（映射到逻辑一致性检查） >= 18
  - 且 decision_actionability >= 18

## 打分输出格式（必须）
`archive/review_checklist.md` 必须包含：
1. 评分总览（总分/是否通过）
2. 各维度得分表（权重、得分、扣分说明）
3. 一票否决检查（逐条）
4. 回退建议（step2/3/4/5）
5. 最终判定（PASS/FAIL）

## 结果处理
- 全部通过 -> 进入 Step 7。
- 事实性不通过 -> 回 Step 3 补采。
- 完整性不通过 -> 回 Step 2 或 Step 4。
- 读者视角不通过 -> 回 Step 5。
- 逻辑一致性不通过 -> 回 Step 5。
- 写作质量不通过 -> 回 Step 5。

## 一票否决项（新增）
- 核心结论无证据编号/来源链接。
- 对标口径明显不一致且未声明。
- 结论章节缺少“定位/能力/场景/边界/启示”五要素。
- 风险章节没有“风险-影响-缓解”映射。
- 未提供加权评分卡（含权重、得分、解释）。
- 未提供 90 天行动路线图（阶段目标、KPI、退出条件）。
- 长篇模式下表格 < 12 或图表 < 4 或参考文献 < 30。
- 出现以上任一项：判定不通过，必须回退。

## 质量卡口
- 复核清单逐项填写，无遗漏。
- 不通过项必须标注问题类型与修正建议。
- 事实性/逻辑一致性严重问题必须标记“必须回退”。
- 量化评分已给出并满足通过阈值（或明确失败原因）。
- 抽检至少 20 条引用回链（claim -> source）且通过率 >= 95%。

## 交接
通过后将 `archive/report.md` 与 `archive/review_checklist.md` 交给 `mr-step7-output`。

