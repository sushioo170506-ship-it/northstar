# model-report-orchestrator

name: model-report-orchestrator
description: 外部模型调研报告总编排器，负责 7 步流程串联、质量卡口执行与回退控制。

## 定位与作用
该 skill 不直接写内容，职责是保障流程可控、质量可验、结论可执行。  
它解决的是“报告能不能稳定达到标准”，而不是“单次能不能写出来”。

## 适用场景
- 需要将模型调研从一次性写作转为标准化生产流程。
- 报告读者包含技术、管理、政府监管沟通、合作、采购与合规等多角色。
- 对信息密度、证据链和结论可执行性有硬门槛要求。

## 标准加载项（必须）
- 评分标准：`skills/external-model-research/model-report-rubric.yaml`
- 模块清单：`skills/external-model-research/model-report-playbook.md`
- 执行要求：
  - Step 6 必须按 rubric 输出维度得分与扣分理由；
  - Step 2/4/5 必须落实 playbook 的结构模块、双轨分析、决策模块。

## 编排流程
1. `mr-step1-scope`：定调（读者/目标/门槛）
2. `mr-step2-outline`：搭大纲（章节/证据/表图计划）
3. `mr-step3-collect`：采素材（来源分层与可追溯）
4. `mr-step4-process`：加工素材（证据账本与结构化产物）
5. `mr-step5-write`：写正文（模型画像与行动结论）
6. `mr-step6-review`：复核（评分+一票否决）
7. `mr-step7-output`：输出（多格式交付）

## 高丰富度硬门槛（必须执行）
对 `长篇详实` 报告，任一项不达标即失败：
1. `raw_data/` 来源 `< 25`，且官方 `< 8` 或第三方 `< 10`；
2. 直接竞品 `< 5`；
3. benchmark 指标 `< 25` 或覆盖维度 `< 8`；
4. 可引用表格 `< 12`；
5. 图表规格 `< 4`；
6. 参考文献 `< 30`；
7. 缺少“结论 -> 数据 -> 解读 -> 局限 -> 行动建议”链路。

## 长篇必备中间产物
- `benchmark_master_table.*`
- `competitor_matrix.*`
- `risk_register.*`
- `decision_scorecard.*`
- `roadmap_90d.*`

## 一票否决项（Step 6）
- 核心结论无证据编号或来源链接；
- 关键对比口径不一致且未声明；
- 结论缺少“定位/能力/场景/边界/启示”五要素；
- 风险章节无“风险-影响-缓解-责任”映射；
- 无可执行路线图或评分不可复算。

## 回退策略
- Step4 -> Step3：来源不足、关键数据不齐、表图不足；
- Step6 -> Step3：事实性失败（来源不可追溯）；
- Step6 -> Step4：证据块缺失；
- Step6 -> Step5：逻辑/读者适配/结论可执行性不足；
- Step7 -> Step6：格式转换导致信息丢失或错位。

## 交付目录
```text
archive/
├── scope.md
├── outline.md
├── raw_data/
├── processed_data/
├── report.md
└── output/
```

