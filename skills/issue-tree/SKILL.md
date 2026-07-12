---
name: issue-tree
description: 将研究主题拆成 3-7 个可由证据回答的子问题，并在人工确认后进入证据治理。
license: MIT
version: 1.0.0
---

# Issue Tree

实现：`research_workflow.skills.issue_tree.IssueTreeSkill`。

输入 `inputs["requirements_analysis"]`，输出 `artifact_type="issue_tree"` 的 JSON，包含
确认主题候选、3–7 个一级问题、二级问题、初始假设、证据需求、必要性、写作价值、保留状态
和排除项。Skill 校验每个保留问题必须说明必要性和价值。

```python
result = IssueTreeSkill(generator=None).execute(request)
```

编排器在本节点后强制触发 `issue_tree_confirmation`。修改议题树会失效大纲、调研、证据
治理、素材、可视化、写作和复核后代，但保留 requirements_analysis。
