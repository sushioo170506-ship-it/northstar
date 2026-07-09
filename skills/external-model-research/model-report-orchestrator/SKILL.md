# model-report-orchestrator

name: model-report-orchestrator  
description: 外部模型调研报告自动生成工作流 — 输入模型名称，按"定调→搭大纲→采素材→加工素材→写正文→复核→输出"七步输出完整报告。

## 职责边界
本 skill 是编排器，只做一件事：按正确顺序串联子 skill、传递中间产物、执行质量卡口。  
如何写大纲、如何采集数据、如何加工、如何写正文，由各子 skill 独立负责。

## 执行流程

```text
Step 1: 定调        -> 报告企划书（读者画像 + 报告类型 + 结论形式）
Step 2: 搭大纲      -> 章节大纲（含素材需求标注）
Step 3: 采素材      -> raw_data/（原始素材，按章节分类）
Step 4: 加工素材    -> processed_data/（结构化内容块：表格/图表/要点）
                        (缺素材则回退 Step 3)
Step 5: 写正文      -> report.md（报告初稿）
Step 6: 复核        -> 复核清单（通过/不通过）
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
- 每个 Step 必须输出标准产物，缺失则不得进入下一步。
- Step 4 若 `gaps.md` 判定素材严重缺失，必须回退 Step 3 补采。
- Step 6 若事实性/逻辑一致性不通过，必须回退，不允许带病发布。

## 防“浅报告”硬门槛（必须执行）
- 任何 `长篇详实` 报告若未达到以下最低标准，直接判定不通过：
  1. `raw_data/` 中可追溯来源总数 `< 12`。
  2. 直接竞品 `< 3`。
  3. benchmark 指标 `< 8`（含通用 + 专项）。
  4. `processed_data/` 可直接引用表格 `< 6`。
  5. `processed_data/figures/` 图表规格 `< 3`。
  6. 正文缺少“结论 -> 数据 -> 解读 -> 局限”链路。
- Step 6 复核时出现以下任一情况，必须回退且不得进入 Step 7：
  - 核心结论无证据编号或来源链接；
  - 关键对比口径不一致且未声明；
  - 结论章节无场景化推荐表；
  - 风险章节无“风险-影响-缓解”映射。

## 回退规则
- Step 4 -> Step 3：缺素材、关键对标数据不齐、图表数据不足
- Step 6 -> Step 3：事实性问题（来源不明、数字不可追溯）
- Step 6 -> Step 4：内容块缺失（章节素材未加工到位）
- Step 6 -> Step 5：写作风格、读者视角、逻辑一致性问题
- Step 7 -> Step 6：格式转换后发现信息丢失或错位

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

