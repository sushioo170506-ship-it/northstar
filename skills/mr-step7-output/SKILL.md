---
name: mr-step7-output
description: Step 7 -- 按交付渠道转换为最终格式，输出最终交付件。输入复核通过的 report.md 和报告企划书，输出 output/ 及 archive/。
---

# Step 7: 输出

把复核通过的 `report.md` 转换为目标读者需要的格式。输出不是"另存为"，而是按渠道做适配，并归档全过程产物。

## 输入

- `report.md`（Step 6 复核通过）
- `report_scope.md`（Step 1，含读者画像、篇幅、风格和交付渠道）
- `processed_data/figures/`（如有图表）

## 输出目录

```text
output/
├── report.md
├── report.pdf
├── executive_summary.md
├── figures/
└── slides/

archive/
├── scope.md
├── outline.md
├── raw_data/
├── processed_data/
├── report.md
└── output/
```

如果某种格式不需要或工具不可用，必须标注"未生成原因"，但 `report.md` 和 `executive_summary.md` 始终保留。

## 输出动作

### 动作 1：提炼 Executive Summary

从报告中提取可独立阅读的摘要，不超过 300 字：

```markdown
# Executive Summary -- [模型名称]

## 一句话结论
[<= 50 字]

## 核心发现（3-5 条）
1. [发现 1]
2. [发现 2]
3. [发现 3]

## 关键对比
| 维度 | 本模型 | 竞品 | 差距 |
|---|---|---|---|

## 推荐意见
[推荐/有条件推荐/不推荐]
```

### 动作 2：格式转换

| 目标格式 | 工具 | 注意事项 |
|---|---|---|
| PDF | Pandoc / md-to-pdf | 中文字体嵌入、目录自动生成 |
| HTML | Pandoc + 自定义 CSS | 响应式布局，自包含 |
| PPT | Pandoc 或手动搬运 | 每节拆一页，图表单独成页 |
| Notion/飞书 | 直接粘贴 Markdown | 检查格式兼容性 |

转换前先检查工具是否可用；不可用时生成 Markdown 版本并说明缺失工具。

### 动作 3：素材归档

归档本次调研的中间产物，供后续复用：
- `scope.md`
- `outline.md`
- `raw_data/`
- `processed_data/`
- `report.md`
- `output/`

## 质量卡口

- [ ] Executive Summary 已生成，可独立阅读。
- [ ] 目标格式已转换（PDF/HTML/PPT 等），或明确说明未生成原因。
- [ ] 中文字体在 PDF 中正常渲染（如生成 PDF）。
- [ ] 图表在目标格式中正常显示。
- [ ] 中间产物已归档。

未通过时继续 Step 7 修正，不回退前序分析步骤。
