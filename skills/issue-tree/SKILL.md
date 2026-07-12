---
name: issue-tree
description: 将研究主题拆成 3-7 个可由证据回答的子问题，并在人工确认后进入证据治理。
license: MIT
version: 1.0.0
---

# Issue Tree

实现：`research_workflow.skills.issue_tree.IssueTreeSkill`。

输入 `inputs["research"]`，输出 `artifact_type="issue_tree"` 的 JSON，包含主问题、子问题、
初始假设、证据需求和覆盖检查。Skill 校验子问题数量必须为 3-7。

```python
result = IssueTreeSkill(generator=None).execute(request)
```

编排器在本节点后强制触发 `issue_tree_confirmation`。修改议题树会失效证据治理、大纲、
写作、压力测试、排版、审核和质量门，但保留原始 research 产物。
