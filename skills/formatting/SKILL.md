---
name: formatting
description: 统一术语、标题、段落和输出格式，不改变报告事实含义。
license: MIT
version: 1.0.0
---

# Format and Style

独立实现：`research_workflow.skills.formatting.FormattingSkill`。

输入 `inputs["writing"]` 和全局 `style`、`output_format`，输出
`artifact_type="formatted_draft"`。内置格式为 `markdown`、`html/webpage`、`feishu`、
`json`、`text`；`docx/word` 与 `pdf` 输出 canonical Markdown 并交给发布渲染器。

```python
result = FormattingSkill(generator=None).execute(request)
```

格式器只做结构与表示转换；不得新增事实。输出后必须经过 `pre_review_confirmation`。
若需 DOCX/PDF，应以独立发布适配器消费终稿，避免在本 Skill 引入硬依赖。

## WHEN / MUST / MUST NOT

- WHEN：draft_confirmation=completed。
- MUST：保持所有来源 URL、标题层级、表格和代码块语义；记录目标格式与样式。
- MUST NOT：润色事实、改写评分、删除局限、声称 Mermaid/Vega 已渲染。

## 格式规则

- Markdown：规范空行和标题，不破坏链接。
- HTML：转义不可信文本；代码块保持可识别；自包含状态由 publish 判断。
- JSON：保留 title/style/content_markdown。
- text：仅移除 Markdown 标题标记，URL 不得丢失。
- feishu：保留飞书文档可导入的标题、列表、表格和内联链接，不引用本地文件路径。
- docx/pdf：只生成规范化中间稿；不得冒充已完成的二进制文件。

格式解析失败节点 failed；目标格式改变从 formatting 失效。DOCX/PDF/PNG 属于 publish 外部
适配器，不在此处执行。
