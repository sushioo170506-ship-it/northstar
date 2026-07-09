# model-report-orchestrator

name: model-report-orchestrator
description: 外部模型调研报告自动生成工作流（高丰富度版）— 输入模型名称，按“定调→搭大纲→采素材→加工素材→写正文→复核→输出”七步产出可决策报告。

## 职责边界
本 skill 仅负责编排和卡口，不负责具体写作细节。  
目标不是“能写完”，而是“达到你已验证的长篇深度标准（以 Claude Mythos 5 完整稿为参考标尺）”。

## 标准配置（必须加载）
- 评分标准：`skills/external-model-research/model-report-rubric.yaml`
- 可复用模块：`skills/external-model-research/model-report-playbook.md`
- 执行规则：
  - Step 6 必须按 rubric 维度打分并输出扣分理由；
  - Step 2/4/5 必须落地 playbook 的结构、双轨分析、决策模块。

## 执行流程

```text
Step 1: 定调        -> 报告企划书（读者、决策目标、丰富度门槛）
Step 2: 搭大纲      -> 章节大纲（含每章证据/表图下限）
Step 3: 采素材      -> raw_data/（带来源、时间、口径）
Step 4: 加工素材    -> processed_data/（证据账本、矩阵、图表规格）
                        (缺素材则回退 Step 3)
Step 5: 写正文      -> report.md（结构化初稿）
Step 6: 复核        -> review_checklist.md（评分+一票否决）
                        (不通过回退对应步骤)
Step 7: 输出        -> output/（最终交付件）
```

## 子 Skill 编排顺序
1. `mr-step1-scope`
2. `mr-step2-outline`
3. `mr-step3-collect`
4. `mr-step4-process`
5. `mr-step5-write`
6. `mr-step6-review`
7. `mr-step7-output`

## 强制卡口策略
- 每个 Step 必须产出标准文件，缺失不得流转。
- Step 4 若 `gaps.md` 出现 P0 缺失，必须回退 Step 3 补采。
- Step 6 若事实性或逻辑一致性失败，必须回退，不得带病发布。

## 高丰富度硬门槛（必须执行）
对 `长篇详实` 报告，以下任一项不达标即判定失败：
1. `raw_data/` 可追溯来源总数 `< 25`（其中官方 `< 8` 或第三方 `< 10` 也判失败）。
2. 直接竞品 `< 5`。
3. benchmark 指标 `< 25`，或覆盖维度 `< 8`（代码/推理/长上下文/Agent/多模态/行业场景/安全/成本）。
4. `processed_data/` 可直接引用表格 `< 12`。
5. `processed_data/figures/` 图表规格 `< 4`。
6. 参考文献与来源清单 `< 30`。
7. 正文缺少“结论 -> 数据 -> 解读 -> 局限 -> 行动建议”链路。

## 强制产物（长篇详实）
Step 4 或 Step 5 至少包含以下内容块：
- `benchmark_master_table.*`
- `competitor_matrix.*`
- `risk_register.*`（风险-影响-缓解-责任）
- `decision_scorecard.*`（加权评分）
- `roadmap_90d.*`（分阶段行动计划）

## 样稿沉淀模块（必须落地到 skill）
- 技术拆解采用“三段式”：现象/观测 -> 学术溯源 -> 本质分析
- 分析采用“双轨”：能力轨 + 治理轨
- 结论包含“适用场景 + 不适用边界 + 行动路径”

## Step 6 一票否决项
出现任一项，必须回退且不得进入 Step 7：
- 核心结论无证据编号或来源链接；
- 关键对比口径不一致且未声明；
- 结论章节无“定位/能力/场景/边界/启示”五要素；
- 风险章节无“风险-影响-缓解-责任人”映射；
- 未给出可执行路线图（如 30/60/90 天计划）；
- 未给出量化评分或评分不可复算。

## 回退规则
- Step 4 -> Step 3：来源不足、关键对标数据不齐、表图数据不足
- Step 6 -> Step 3：事实性问题（来源缺失、数字不可追溯）
- Step 6 -> Step 4：证据块缺失（矩阵/风险表/评分卡不完整）
- Step 6 -> Step 5：写作逻辑、读者视角、结论可执行性不足
- Step 7 -> Step 6：格式转换后出现内容丢失、图表错位、引用断链

## 交付目录约定

```text
archive/
├── scope.md
├── outline.md
├── raw_data/
├── processed_data/
├── report.md
└── output/
```

