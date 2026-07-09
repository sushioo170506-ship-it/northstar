# skill_07_publish

name: MR-publish  
description: 外部模型调研报告 Step 7 — 多格式输出、摘要提炼与版本归档。

## 目标
输出可直接分发的报告文件，并保留可追溯归档信息。

## 职责边界
- **做**：格式转换、摘要生成、版本归档。
- **不做**：重写核心结论（若需重写应回到上一步）。

## 输入
- `output/revised_draft.md`
- `output/decision.json`
- `output/asset_plan.json`
- `output/review_report.json`

## 输出
- `output/final.md`
- `output/final.pdf`
- `output/final.docx`（可选）
- `output/final.pptx`（可选）
- `output/executive_summary.md`
- `output/archive.json`

## 执行步骤
1. 固化终稿内容与图表引用编号。
2. 生成管理层摘要（可独立阅读）。
3. 输出多格式文件并检查一致性。
4. 写入归档元数据：模型版本、数据截止日、引用快照、产物清单。

## 质量卡口
- 各格式核心结论一致（不得出现版本漂移）。
- 关键图表和引用链接可用。
- `archive.json` 完整可追溯。

## 交付完成条件
存在并可打开：
- `output/final.md`
- `output/final.pdf`
- `output/executive_summary.md`
- `output/archive.json`

