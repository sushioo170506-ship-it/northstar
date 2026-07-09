---
name: mr-step4-process
description: Step 4 -- 把原始素材加工为可直接写入报告的结构化内容块：信息归位、表格化、图表化、提炼要点、缺失检测。输入 raw_data/ 和章节大纲，输出 processed_data/。
---

# Step 4: 加工素材

这是从"收集到的东西"到"能写进报告的东西"的转换层。原始素材是散装的，加工后应变成可以直接粘贴进正文的内容块。

## 输入

- `raw_data/`（Step 3 产出）
- `outline.md`（Step 2 产出）

## 输出目录

生成 `processed_data/`：

```text
processed_data/
├── section_1/
│   ├── info_card.md
│   └── key_points.md
├── section_2/
│   ├── architecture_diagram.md
│   └── tech_highlights.md
├── section_3/
│   ├── benchmark_table.csv
│   └── benchmark_chart.py
├── section_4/
│   ├── comparison_matrix.md
│   └── radar_chart.py
├── section_5/
│   ├── deployment_table.md
│   └── cost_analysis.md
├── section_6/
│   ├── ecosystem_assessment.md
│   └── risk_points.md
├── section_7/
│   └── scoring_table.md
├── figures/
│   ├── benchmark_comparison.png
│   ├── radar_comparison.png
│   └── architecture.png
└── gaps.md
```

根据实际报告类型调整 section 文件名，但必须保持"按章节归类"。

## 加工动作

### 动作 1：信息归位

把 `raw_data/` 中的素材按 `outline.md` 章节分配到 `processed_data/section_X/`。每个 section 至少包含：
- `key_points.md`：本章可写入正文的要点。
- 若本章有表格/图表需求，生成对应表格或图表代码/文件。

### 动作 2：表格化

把散落在论文、官网、榜单中的参数/分数统一成对比表格。

```markdown
| 模型 | MMLU | HumanEval | GSM8K | 上下文长度 | 来源 |
|---|---:|---:|---:|---|---|
| Llama 4 | 87.2 | 72.1 | 89.5 | 128K | R001 |
| DeepSeek-V3 | 88.5 | 73.0 | 90.0 | 128K | R002 |
```

### 动作 3：提炼关键信息

把冗长技术描述提炼为 3-5 条 bullet point：

```markdown
- MoE 架构，总参数量 671B，激活参数 37B。
- 多头潜在注意力（MLA）替代标准注意力。
- 辅助损失系数从 0.01 降至 0.001。
```

### 动作 4：生成图表

根据大纲中标注的图表需求生成：
- 参数/benchmark 对比柱状图。
- 多维度雷达图。
- 架构流程图（Mermaid 或图片）。
- 训练/发布/版本时间线。

数据不足时不要硬画，标注"因数据不足暂缺"并写入 `gaps.md`。

### 动作 5：缺失检测

对照 `outline.md` 的素材需求，生成 `processed_data/gaps.md`：

```markdown
# 缺失检测报告

§1 模型全景 -- ✅ 齐全
§2 技术拆解 -- ⚠️ 缺少推理优化细节（待补采）
§3 能力评测 -- ✅ 齐全
§4 横向对标 -- ⚠️ 缺少竞品 Qwen3 的部署数据
§5 部署分析 -- ❌ 缺少实测延迟数据（需要补采）
§6 生态评估 -- ✅ 齐全
§7 结论 -- 不在此阶段评估
```

## 质量卡口

- [ ] 所有素材已按章节归位。
- [ ] 关键参数/分数已表格化。
- [ ] 论文长篇描述已提炼为 bullet points。
- [ ] 大纲中标注的图表已生成，或标注"因数据不足暂缺"。
- [ ] 缺失检测已完成，`gaps.md` 标注清晰。
- [ ] 如果任何章节素材严重缺失，已标注并返回 Step 3 补采。

未通过时不得进入 Step 5。
