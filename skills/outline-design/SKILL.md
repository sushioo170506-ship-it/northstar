---
name: outline-design
description: 根据证据包设计章节、论证目标、证据需求与篇幅预算。
license: MIT
version: 1.0.0
---

# Outline Design

独立实现：`research_workflow.skills.outline.OutlineSkill`。

输入 `requirements_analysis`、已确认 `issue_tree` 及统一 `ReportConfig`，在调研前先确定
最终写作框架。输出 `artifact_type="outline"` 的 JSON，章节包含稳定 ID、标题、目标篇幅、
目的、对应议题和证据需求，并记录受众、文风、产出类型、内容边界对齐信息。

```python
result = OutlineSkill(generator=None).execute(request)
```

主编排器必须在本节点后触发 `outline_confirmation`。修改大纲会失效大纲及所有后代，
但保留研究证据包。
