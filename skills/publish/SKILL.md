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
- INPUT：review、quality_gate、visualization、capability_sweep、skill_research。
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

- 飞书：发布飞书兼容 Markdown/块结构，保留正文内联 URL。
- 网页：输出 HTML；只有图表资源真实内联后才能标记 self_contained=true。
- Word：必须注入 DocumentRenderer（如经审查的 Pandoc/Word适配器），保存 DOCX payload/URI。
- PDF：必须注入 DocumentRenderer（如 Typst/Pandoc适配器），保存 PDF payload/URI。
- renderer 缺失或未返回 `rendered=true` 时，DOCX/PDF发布失败，不得静默改成Markdown。

## 错误处理

- quality passed=false：失败，退回 quality_gate 指示的最早节点。
- 格式不支持：失败，退回 formatting。
- 渲染器缺失：Markdown 可降级发布；强制 HTML/PNG 时失败，不静默降级。
