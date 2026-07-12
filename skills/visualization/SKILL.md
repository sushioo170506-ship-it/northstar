---
name: visualization
description: 根据议题树和章节素材生成 Mermaid 与 Vega-Lite 可视化资产。
license: MIT
version: 1.0.0
---

# Visualization

实现：`research_workflow.skills.visualization.VisualizationSkill`。

输入 `issue_tree` 与 `material_integration`，输出
`artifact_type="visualization_assets"`。内置实现至少生成：

- Mermaid 多层级研究问题逻辑图；
- Vega-Lite 来源类别构成图；
- 素材存在量化值时生成量化证据分布图。

每个资产包含稳定 ID、类型、格式、标题、适用章节和可直接交给渲染器的 content。Skill 负责
生成可移植规范，不在运行时引入浏览器或图形库；发布适配器负责渲染 PNG/SVG。
