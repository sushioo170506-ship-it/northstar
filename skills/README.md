# Model Report Workflow — Agent Skill Suite

这是一套用于**外部模型调研报告自动生成**的 Agent Skills。输入模型名称后，由主编排器按七步流水线输出完整报告：

```text
定调 -> 搭大纲 -> 采素材 -> 加工素材 -> 写正文 -> 复核 -> 输出
```

每个 skill 是一个文件夹，内部包含 `SKILL.md`。Agent 通过 frontmatter 中的 `name` 和 `description` 判断何时调用。

## 主入口

从 **`model-report-orchestrator`** 开始。它只做编排：
- 按正确顺序串联子 skill。
- 传递中间产物。
- 执行质量卡口。
- 在卡口不通过时回退到对应步骤。

## 七步工作流

```text
model-report-orchestrator
│
├─ Step 1: mr-step1-scope
│   定调：读者画像 + 报告类型 + 结论形式
│   输出：report_scope.md
│
├─ Step 2: mr-step2-outline
│   搭大纲：章节结构 + 每章核心问题 + 素材需求 + 图表需求
│   输出：outline.md
│
├─ Step 3: mr-step3-collect
│   采素材：从官方、论文、榜单、社区、新闻等渠道采集原始信息
│   输出：raw_data/
│
├─ Step 4: mr-step4-process
│   加工素材：信息归位、表格化、图表化、要点提炼、缺失检测
│   输出：processed_data/
│
├─ Step 5: mr-step5-write
│   写正文：把内容块组装为连贯 report.md
│   输出：report.md
│
├─ Step 6: mr-step6-review
│   复核：事实性、完整性、读者视角、逻辑一致性、写作质量检查
│   输出：review_checklist.md
│
└─ Step 7: mr-step7-output
    输出：Executive Summary、目标格式转换、归档
    输出：output/ + archive/
```

## 回退规则

| 问题类型 | 回退步骤 |
|---|---|
| 读者画像、报告类型、结论形式不清 | Step 1 |
| 大纲结构/素材需求不合理 | Step 2 |
| 原始素材缺失或来源不足 | Step 3 |
| 素材未加工成可写内容块 | Step 4 |
| 风格不符、数字无解读、结论模糊 | Step 5 |
| 复核不通过 | 按 Step 6 的问题类型回退 |
| 输出格式/摘要/归档不完整 | Step 7 |

## Skills index

| Skill | 一句话职责 | 输入 | 输出 | 回退 |
|---|---|---|---|---|
| `model-report-orchestrator` | 串联七步并执行质量卡口 | 模型名称 + 用户目标 | 完整交付件 | 按问题类型 |
| `mr-step1-scope` | 确定读者画像、报告类型、结论形式 | 模型名称 + 用户回答 | `report_scope.md` | - |
| `mr-step2-outline` | 构建报告骨架，标注素材需求 | `report_scope.md` | `outline.md` | Step 1 |
| `mr-step3-collect` | 按大纲采集原始信息 | `outline.md` + 模型名称 | `raw_data/` | Step 2 |
| `mr-step4-process` | 原始素材 -> 结构化内容块 | `raw_data/` | `processed_data/` | Step 3 |
| `mr-step5-write` | 内容块 -> 连贯报告 | `processed_data/` + 大纲 + 企划书 | `report.md` | Step 4 |
| `mr-step6-review` | 质量检查并决定是否回退 | `report.md` + 企划书 | `review_checklist.md` | 按问题类型 |
| `mr-step7-output` | 格式转换 + 交付归档 | 复核通过的 `report.md` | `output/` + `archive/` | Step 6 |
