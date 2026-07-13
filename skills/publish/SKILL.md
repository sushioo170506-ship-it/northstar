---
name: publish
description: 工作流最终发布阶段 — 仅组装已通过质量门的候选稿，并披露渲染能力与交付限制。
license: MIT
version: 1.0.0
---

# Publish

## 职责边界

只发布，不修改事实、结论、评分或图表数据。质量门未通过时必须拒绝。

## 输入与输出

- WHEN：quality_gate=completed 且 passed=true。
- INPUT：review、quality_gate、visualization、capability_sweep、skill_research、writing_standards。
- OUTPUT：`published_report`，正文保持不变；metadata.publish_manifest 描述交付状态。

## 发布清单

必须记录：目标格式、字符数、可视化数量、使用/未配置的 Mermaid/Vega/Pandoc 渲染器、
self_contained、raster_exported、第三方候选审查数、待人工审批改造数和 limitations。

## HTML / SVG / PNG 规则

- 没有真实渲染器时不得声称 SVG 已内联或 PNG 已导出。
- Mermaid/Vega-Lite 仅有规范时，HTML 标记 self_contained=false。
- require_png=true 但无渲染产物时，必须披露限制，不得生成空占位图。
- 配置 Mermaid/Vega/Pandoc 后，适配器输出仍须校验标签平衡、资源完整性和渲染成功率。

## 多格式发布

- 飞书：必须注入FeishuDocumentRenderer；正文转Docx块，GFM表格转内嵌原生Sheet Block，
  写值、样式、冻结首行并回读。返回文档URL和Sheet token，不返回伪造Markdown。
- 网页：输出 HTML；只有图表资源真实内联后才能标记 self_contained=true。
- Word：必须注入 DocumentRenderer（如经审查的 Pandoc/Word适配器），保存 DOCX payload/URI。
- PDF：必须注入 DocumentRenderer（如 Typst/Pandoc适配器），保存 PDF payload/URI。
- PPTX：注入SlidesRenderer，输出可编辑16:9 PowerPoint和slide_count。
- Slides HTML：注入SlidesRenderer，输出自包含HTML、键盘翻页和页码。
- Slides HTML必须是可直接保存/打开的单文件，不得要求先解压ZIP；采用frontend-slides固定
  1920×1080画布整体缩放、预设化视觉系统、内容预算、无溢出/重叠和键盘/触摸导航规范。
- renderer 缺失或未返回 `rendered=true` 时，Feishu/DOCX/PDF发布失败，不得静默改成Markdown。
- secret/confidential/top_secret禁止飞书发布；internal必须有目标租户和数据驻留审批。

仓库提供 `PandocDocumentRenderer`：以固定参数和超时调用本机Pandoc，成功后返回base64
payload、MIME、字节数和renderer元数据；Pandoc或PDF engine缺失时明确失败。

## 错误处理

- quality passed=false：失败，退回 quality_gate 指示的最早节点。
- 格式不支持：失败，退回 formatting。
- 渲染器缺失：Markdown 可降级发布；强制 HTML/PNG 时失败，不静默降级。

## 统一输出格式约束

凡本Skill输出、改写或传递Markdown/报告正文，必须遵守：业务流程、逻辑链路和路径走向使用结构化Mermaid流程图；每张统计或说明表后附字段定义、数据逻辑与结论依据；同层有序列表连续递增、子层独立编号，禁止重复“1.”；外部链接保留可点击Markdown语法并由`content_optimization`生成文末全量链接索引。JSON-only产物也不得破坏下游执行这些规则所需的数据和URL。
