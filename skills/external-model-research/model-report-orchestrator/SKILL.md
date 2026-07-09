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

## 输入
- 模型名称与任务目标（来自用户输入）
- 工作流配置（`external-model-research-workflow.yaml`）
- 评分标准与模块清单（rubric + playbook）

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

## 输出
- 各步骤执行状态（通过/失败/回退）
- 回退指令与修正方向（回退到对应 step）
- 最终交付完整性结论（是否允许发布）

## 逻辑链条总则（必须）
为避免“只有结论”或“只有过程”，全流程必须执行双向闭环：

1. 结论闭环（CERV）  
   `结论 -> 证据 -> 推导 -> 价值/边界`  
   - 结论：明确判断句，不用空泛形容词替代判断；  
   - 证据：来源编号、关键数据、时间口径；  
   - 推导：说明为何由这些证据得到该结论；  
   - 价值/边界：说明对决策的价值与适用边界。

2. 过程闭环（PEVC）  
   `过程 -> 成果 -> 价值 -> 对应结论`  
   - 过程：执行了什么分析动作；  
   - 成果：产出了什么可复核结果；  
   - 价值：该成果提升了什么决策质量；  
   - 对应结论：最终支撑了哪些结论 ID。

3. 双向映射产物（Step4/Step5 必交）  
   - `conclusion_evidence_reasoning_map.md`（CERV 映射）  
   - `process_outcome_value_map.md`（PEVC 映射）

## 高丰富度硬门槛（必须执行）
对 `长篇详实` 报告，任一项不达标即失败：
1. `raw_data/` 来源 `< 25`，且官方 `< 8` 或第三方 `< 10`；
2. 直接竞品 `< 5`；
3. benchmark 指标 `< 25` 或覆盖维度 `< 8`；
4. 可引用表格 `< 12`；
5. 图表规格 `< 4`；
6. 参考文献 `< 30`；
7. 缺少 CERV 或 PEVC 双向映射；
8. 任一核心结论无来源编号或无推导说明；
9. 任一关键分析过程未沉淀明确成果与对应结论。

## 长篇必备中间产物
- `benchmark_master_table.*`
- `competitor_matrix.*`
- `risk_register.*`
- `decision_scorecard.*`
- `roadmap_90d.*`
- `conclusion_evidence_reasoning_map.*`
- `process_outcome_value_map.*`

## 一票否决项（Step 6）
- 核心结论无证据编号或来源链接；
- 关键对比口径不一致且未声明；
- 结论缺少“定位/能力/场景/边界/启示”五要素；
- 风险章节无“风险-影响-缓解-责任”映射；
- 无可执行路线图或评分不可复算；
- 存在“孤立结论”（无法回链证据/推导）；
- 存在“孤立过程”（有过程描述但无成果与结论归属）。

## 回退策略
- Step4 -> Step3：来源不足、关键数据不齐、表图不足；
- Step6 -> Step3：事实性失败（来源不可追溯）；
- Step6 -> Step4：证据块缺失；
- Step6 -> Step5：逻辑/读者适配/结论可执行性不足；
- Step6 -> Step4/5：双向映射存在孤立项或链路断裂；
- Step7 -> Step6：格式转换导致信息丢失或错位。

## 质量卡口
- 已加载 rubric 与 playbook；
- 各 step 的必备产物和门槛均被校验；
- 一票否决项触发时已阻断发布；
- 回退路径明确且可执行；
- 已完成 CERV 与 PEVC 双向闭环检查。

## 交接
- 启动阶段：将任务交给 `mr-step1-scope`；
- 结束阶段：在 Step7 输出通过后交付 `archive/output/`。

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

