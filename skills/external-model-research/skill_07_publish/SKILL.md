# mr-step7-output

name: mr-step7-output  
description: Step 7 — 按交付渠道转换最终格式，输出可分发交付件并完成归档。

## 作用
将复核通过的 `report.md` 按目标渠道适配，不只是“另存为”。

## 输入
- `archive/report.md`（复核通过）
- `archive/scope.md`（交付渠道、篇幅、风格要求）
- `archive/review_checklist.md`

## 输出
写入 `archive/output/`：

```text
output/
├── report.md
├── report.pdf
├── executive_summary.md
├── figures/
└── slides/    # 如需要
```

## 输出动作
1. **提炼 Executive Summary（<= 300 字）**
   - 一句话结论（<= 50 字）
   - 核心发现 3-5 条
   - 关键对比表
   - 推荐意见
2. **格式转换**
   - PDF：Pandoc / md-to-pdf（中文字体嵌入）
   - HTML：Pandoc + CSS（响应式）
   - PPT：Pandoc 或手工拆页
   - Notion/飞书：检查 Markdown 兼容
3. **素材归档**
   - `archive/scope.md`
   - `archive/outline.md`
   - `archive/raw_data/`
   - `archive/processed_data/`
   - `archive/report.md`
   - `archive/output/`

## 发布前完整性检查（新增）
- `report.md` 至少包含：
  - 章节 §1-§7
  - 引用来源清单
  - 至少 6 张表（长篇）
  - 至少 3 个图表规格或图像资产（长篇）
- `executive_summary.md` 必须包含：
  - 一句话结论
  - 核心发现 3-5 条
  - 推荐意见

## 质量卡口
- Executive Summary 已生成且可独立阅读。
- 目标格式均已转换完成。
- PDF 中文字体正常渲染。
- 图表在目标格式中可见且不失真。
- 中间产物已归档可追溯。
- 若表图数量未达报告深度门槛，禁止标记为“最终交付”。

