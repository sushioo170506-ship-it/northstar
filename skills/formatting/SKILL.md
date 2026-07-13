---
name: formatting
description: 统一术语、标题、段落和输出格式，不改变报告事实含义。
license: MIT
version: 1.0.0
---

# Format and Style

独立实现：`research_workflow.skills.formatting.FormattingSkill`。

输入 `inputs["citation_management"]` 和全局 `style`、`output_format`，输出
`artifact_type="formatted_draft"`。内置格式为`markdown`、`html/webpage`、`json`、`text`；
`feishu`、`docx/word`、`pdf`、`pptx/ppt`、`slides_html`和`slides_zip/slides`输出canonical Markdown并交给
对应发布渲染器。

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
- feishu：保持标题、列表、GFM表格和内联链接；publish必须将表格创建为内嵌Sheet Block，
  不得把Markdown或截图冒充原生电子表格。
- docx/pdf：只生成规范化中间稿；不得冒充已完成的二进制文件。
- pptx/slides_html：按汇报逻辑生成16:9演示稿；PPTX保持元素可编辑，HTML必须可离线翻页。

格式解析失败节点 failed；目标格式改变从 formatting 失效。Feishu/DOCX/PDF/PNG 属于 publish 外部
适配器，不在此处执行。

## 统一输出格式约束

凡本Skill输出、改写或传递Markdown/报告正文，必须遵守：业务流程、逻辑链路和路径走向使用结构化Mermaid流程图；每张统计或说明表后附字段定义、数据逻辑与结论依据；同层有序列表连续递增、子层独立编号，禁止重复“1.”；外部链接保留可点击Markdown语法并由`content_optimization`生成文末全量链接索引。JSON-only产物也不得破坏下游执行这些规则所需的数据和URL。
