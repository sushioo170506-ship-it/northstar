---
name: format-style
description: 统一术语、标题、段落和输出格式，不改变报告事实含义。
license: MIT
version: 1.0.0
---

# Format and Style

独立实现：`research_workflow.skills.formatting.FormattingSkill`。

输入 `inputs["writing"]` 和全局 `style`、`output_format`，输出
`artifact_type="formatted_draft"`。内置格式为 `markdown`、`html`、`json`、`text`
（别名 `md`、`htm`、`txt` 在配置中心标准化）。

```python
result = FormattingSkill(generator=None).execute(request)
```

格式器只做结构与表示转换；不得新增事实。输出后必须经过 `pre_review_confirmation`。
若需 DOCX/PDF，应以独立发布适配器消费终稿，避免在本 Skill 引入硬依赖。
