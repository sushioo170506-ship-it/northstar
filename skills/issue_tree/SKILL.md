---
name: issue_tree
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

## WHEN / 边界

- WHEN：requirements_analysis 完成。
- 只定义研究问题、初始刺点和检验路径；不搭章节、不搜索、不下最终结论。

## 必须输出

- confirmed_topic_candidate；
- 3–7 个一级问题及必要二级问题；
- 每个问题的 necessity、value、evidence_required、included；
- provisional_thesis：判断、反对意见、证伪条件、行动价值；
- ≥3 个 competitive_hypotheses：行业共识、反共识假说、检验数据；
- excluded_issues 及删除理由。

## 质量与错误

- 问题必须互不重复、共同覆盖目标、可由证据回答。
- 无法改变最终判断或行动的问题必须排除。
- 信仰式、不可证伪问题不通过。
- 主题歧义返回 requirements_analysis；问题重叠在本节点修订；人工未确认不得进入 outline。
