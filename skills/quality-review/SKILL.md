---
name: review
description: 对格式化报告执行证据、结构、篇幅、语言和格式审核并保守润色。
license: MIT
version: 1.0.0
---

# Quality Review

独立实现：`research_workflow.skills.review.ReviewSkill`。

输入 requirements_analysis、formatting、research、evidence_governance、data_processing、
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

- 真实性：全部来源链接仍存在；厂商/社区立场已标注。
- 需求：受众、文风、篇幅、格式、禁止边界。
- 结构：大纲章节、核心判断、局限和结论闭合。
- 数据：数字三要素、claim grade、评分状态与正文一致。
- 外发：图表引用、标题、来源、Markdown/HTML/JSON/text 结构。

## 错误与路由

issues 必须带位置、严重度、修复节点。事实/链接→research；claim/评分→data_processing；
章节→outline；行文→writing；格式→formatting；图表→visualization。Review 不通过时仍保存
候选稿和 issues，由 quality_gate 统一阻断。
