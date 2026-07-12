---
name: content-writing
description: 按已确认大纲和证据包分节生成研究报告初稿。
license: MIT
version: 1.0.0
---

# Content Writing

独立实现：`research_workflow.skills.writing.WritingSkill`。

输入为 `inputs["outline"]` 和 `inputs["research"]`，输出
`SkillResult(artifact_type="draft")`。写作必须区分事实、分析和建议，只使用证据包中的
来源；资料不足使用显式缺口标记。实现按章节生成，可处理十万字级目标，不要求一次将
全部历史上下文装入模型窗口。

```python
result = WritingSkill(generator=my_generator).execute(request)
```

模型适配器应支持按章节设置 token 上限。输出后进入 `draft_confirmation`；针对初稿的
修改仅重跑写作、排版、审核及中间确认。
