---
name: visualization
description: 根据议题树和章节素材生成 Mermaid 与 Vega-Lite 可视化资产。
license: MIT
version: 1.0.0
---

# Visualization

实现：`research_workflow.skills.visualization.VisualizationSkill`。

输入 `issue_tree`、`material_integration` 与 `data_processing`，输出
`artifact_type="visualization_assets"`。内置实现至少生成：

- Mermaid 多层级研究问题逻辑图；
- Vega-Lite 来源类别构成图；
- 素材存在量化值时生成量化证据分布图。

每个资产包含稳定 ID、类型、格式、标题、适用章节和可直接交给渲染器的 content。Skill 负责
生成可移植规范，不在运行时引入浏览器或图形库；发布适配器负责渲染 PNG/SVG。

## 图表选择规则

- 比较：≤6 对象、≤2 指标用分组柱；≥3 指标用雷达/热力；更多对象用排序条形。
- 趋势：1–5 序列用折线；更多用 small multiples；构成变化用堆叠面积。
- 分布：直方/箱线/散点；第三变量只能映射气泡面积。
- 关系：散点+回归、相关热力、网络/桑基。
- 禁止饼图、3D、无来源装饰图和误导性双 Y 轴。

## 数量和类型卡口

- 默认生成 6–10 项；少于 6 项应标记数据不足，不用假数据凑图。
- 至少一项多维对比、一项结构分化、一项时间线。
- 每个标题必须是结论句；每个图含 source_ids、样本/口径（如有）和审稿风险。
- 色盲友好、灰阶可分；主色≤3；图表规范统一使用 Mermaid/Vega-Lite。

## 输出与错误

本 Skill 输出规范，不声称已渲染。空数据保留 schema 和 limitations；非法数值不得绘图。
渲染失败属于 publish/外部 Mermaid、Vega 适配器，不回写数据。
