---
name: quality-review
description: 对格式化报告执行证据、结构、篇幅、语言和格式审核并保守润色。
license: MIT
version: 1.0.0
---

# Quality Review

独立实现：`research_workflow.skills.review.ReviewSkill`。

输入 `inputs["formatting"]`、`inputs["research"]`、`inputs["outline"]`，输出
`artifact_type="final_report"`。元数据包含 `quality_passed`、`issues` 和逐项检查结果。
没有来源时保留资料缺口风险，不以虚构引文“修复”问题。

```python
result = ReviewSkill(generator=None).execute(request)
```

审核前必须已经完成人工 `pre_review_confirmation`。Skill 可独立升级；只要维持
`SkillRequest -> SkillResult` 契约，主编排器无需修改。
