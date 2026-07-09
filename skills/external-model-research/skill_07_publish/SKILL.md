# mr-step7-output

name: mr-step7-output
description: Step 7 — 输出最终交付件并完成归档，确保报告可分发、可复用、可追溯。

## 定位与作用
本步骤是“发布包装层”。  
目标不是简单导出文件，而是确保内容在不同渠道下结构一致、信息不损失。

## 输入
- `archive/report.md`（复核通过）
- `archive/scope.md`
- `archive/review_checklist.md`

## 输出
`archive/output/` 至少包含：
- `report.md`
- `report.pdf`
- `report.docx`
- `executive_summary.md`
- `decision_brief.md`
- `figures/`
- `appendix/`
- `slides/`（如需要）

## 执行动作
1. 生成摘要：一句话结论 + 核心发现 + 禁用边界；
2. 转换格式：MD/PDF/DOCX（必要时 HTML/PPT）；
3. 归档中间产物：scope/outline/raw_data/processed_data/report/output；
4. 导出附录：关键表格包、来源索引、review 快照。

## 发布前检查
- 主稿章节完整（§1-§7）且引用清单存在；
- 长篇达到表图门槛（表 >= 12，图 >= 4）；
- `decision_brief` 包含结论五要素摘要（定位/能力/场景/边界/启示）；
- DOCX 与 MD 结构一致（标题层级、表格、关键段落）。

## 质量卡口
- 摘要可独立阅读；
- 多格式输出无内容丢失；
- 图表在目标格式中可见；
- 归档目录完整可追溯；
- 若一致性检查失败，回退修复后再发布。

## 交接
- 对外交付：`archive/output/` 作为最终可分发目录；
- 对内沉淀：`archive/` 全量归档用于复盘与审计。

