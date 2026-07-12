---
name: pressure-test
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
