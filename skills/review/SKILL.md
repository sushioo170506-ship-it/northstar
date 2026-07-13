---
name: review
description: 对格式化报告执行证据、结构、篇幅、语言和格式审核并保守润色。
license: MIT
version: 1.0.0
---

# Quality Review

独立实现：`research_workflow.skills.review.ReviewSkill`。

输入 requirements_analysis、writing_standards、formatting、research、evidence_governance、data_processing、
outline、material_integration、visualization、pressure_test，输出候选
`artifact_type="final_report"`。元数据包含 `review_checks_passed`、issues 和逐项检查。
没有来源时保留资料缺口风险，不以虚构引文“修复”问题。

```python
result = ReviewSkill(generator=None).execute(request)
```

审核前必须已经完成人工 `pre_review_confirmation`。Skill 可独立升级；只要维持
`SkillRequest -> SkillResult` 契约，主编排器无需修改。

## 职责边界

Review 是编辑性复核和问题汇总，不是最终发布裁决。它可做确定性、保守的错字/格式修复，但
不得新增事实、替换来源、重新评分或绕过 quality_gate。

## 复核项目

- 真实性：全部来源链接仍存在并内联在对应章节；文末集中引用不能替代正文链接；
  厂商/社区立场已标注。
- 需求：受众、文风、篇幅、格式、禁止边界。
- 结构：大纲章节、核心判断、局限和结论闭合。
- 场景规范：技术/投研/公众号/官方内参的必需结构、参照核验状态和外发安全条件。
- 数据：数字三要素、claim grade、评分状态与正文一致。
- 外发：图表引用、标题、来源、Markdown/HTML/JSON/text 结构。
- 风险：风险章节必须对应研究对象；模型、ETF、产业报告分别检查其专属风险，不接受泛化声明。

## 错误与路由

issues 必须带位置、严重度、修复节点。事实/链接→research；claim/评分→data_processing；
章节→outline；行文→writing；格式→formatting；图表→visualization。Review 不通过时仍保存
候选稿和 issues，由 quality_gate 统一阻断。

## 统一输出格式约束

凡本Skill输出、改写或传递Markdown/报告正文，必须遵守：业务流程、逻辑链路和路径走向使用结构化Mermaid流程图；每张统计或说明表后附字段定义、数据逻辑与结论依据；同层有序列表连续递增、子层独立编号，禁止重复“1.”；外部链接保留可点击Markdown语法并由`content_optimization`生成文末全量链接索引。JSON-only产物也不得破坏下游执行这些规则所需的数据和URL。
