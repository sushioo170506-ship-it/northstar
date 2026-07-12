---
name: outline-design
description: 根据证据包设计章节、论证目标、证据需求与篇幅预算。
license: MIT
version: 1.0.0
---

# Outline Design

独立实现：`research_workflow.skills.outline.OutlineSkill`。

输入 `SkillRequest.inputs["research"]`（`evidence_pack` JSON）及统一 `ReportConfig`。
输出 `artifact_type="outline"` 的 JSON，章节包含稳定 ID、标题、目标篇幅、目的和证据需求。
不读取检索 Skill 内部状态。

```python
result = OutlineSkill(generator=None).execute(request)
```

主编排器必须在本节点后触发 `outline_confirmation`。修改大纲会失效大纲及所有后代，
但保留研究证据包。
