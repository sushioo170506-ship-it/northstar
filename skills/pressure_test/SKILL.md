---
name: pressure_test
description: 对初稿独立执行逻辑、证据、反方论证和完整性压力测试。
license: MIT
version: 1.0.0
---

# Pressure Test

实现：`research_workflow.skills.pressure_test.PressureTestSkill`。

输入需求、大纲、议题树、调研、证据账本、章节素材、可视化和 writing，输出独立 JSON
弱点报告，不会把自我审查混入正文。除四类审计外，还检查三类来源、原始链接、素材挂载率
和可视化是否齐备。报告包括：

- `logic_audit`
- `evidence_audit`
- `counterargument_audit`
- `completeness_audit`
- `repair_actions`

压力测试完成后才进入 `draft_confirmation`。修改 writing 会自动重跑压力测试；修改
formatting 不会无谓重跑初稿压力测试。

## 独立审计纪律

- 与 writing 使用相同输入但不同角色，不替作者辩护。
- 逻辑审计：论点→证据→结论、相关/因果、隐含假设。
- 证据审计：单源、利益方、冲突、数字缺口、claim 等级。
- 反方审计：为每个核心判断写最强反对意见和失效条件。
- 完整性审计：议题、章节、锚点和图表是否闭合；仅在显式启用时检查竞争性假说。

## 边界与错误

只输出弱点和 repair_actions，不修改正文、不做最终发布裁决。发现硬合规问题也只登记，
唯一阻断者是 quality_gate。无法解析正文时节点 failed；证据问题路由 data_processing，
逻辑问题路由 writing，结构遗漏路由 outline。
