---
name: content-writing
description: 按已确认大纲和证据包分节生成研究报告初稿。
license: MIT
version: 1.0.0
---

# Content Writing

独立实现：`research_workflow.skills.writing.WritingSkill`。

输入需求简报、议题树、最终大纲、调研包、证据账本、章节素材和可视化资产，输出
`SkillResult(artifact_type="draft")`。写作必须区分事实、分析和建议，只使用治理后的来源；
每个事实章节附原始 URL，以 Mermaid/Vega-Lite 代码块嵌入可视化规范。资料不足使用显式缺口
标记。实现按章节生成，可处理十万字级目标。

```python
result = WritingSkill(generator=my_generator).execute(request)
```

模型适配器应支持按章节设置 token 上限。输出后进入 `draft_confirmation`；针对初稿的
修改仅重跑写作、排版、审核及中间确认。
