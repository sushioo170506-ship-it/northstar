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
- excluded_issues 及删除理由。

`competitive_hypotheses` 不是默认字段。仅当用户明确要求因果研究、争议命题检验或设置
`extra.enable_competitive_hypotheses=true` 时才生成；普通行业研究不得强行加入。

## 质量与错误

- 问题必须互不重复、共同覆盖目标、可由证据回答。
- 无法改变最终判断或行动的问题必须排除。
- 信仰式、不可证伪问题不通过。
- 主题歧义返回 requirements_analysis；问题重叠在本节点修订；人工未确认不得进入 outline。

## 统一输出格式约束

凡本Skill输出、改写或传递Markdown/报告正文，必须遵守：业务流程、逻辑链路和路径走向使用结构化Mermaid流程图；每张统计或说明表后附字段定义、数据逻辑与结论依据；同层有序列表连续递增、子层独立编号，禁止重复“1.”；外部链接保留可点击Markdown语法并由`content_optimization`生成文末全量链接索引。JSON-only产物也不得破坏下游执行这些规则所需的数据和URL。
