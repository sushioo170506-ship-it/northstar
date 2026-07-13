# Skill 唯一清单

本文件是人类可读镜像；代码事实源为
`research_workflow.integrations.BUILTIN_SKILL_ORDER`。检查规则要求目录名、SKILL.md
frontmatter `name`、Python `Skill.name`、DAG node id 四者一致。

## 计数口径

- 主编排 Skill：1 个，不作为 DAG 功能节点执行；
- 可执行 Skill：20 个，全部出现在 DAG；
- 其中条件节点：1 个（`quant_finance_research`，非量化场景快速跳过）；
- 主路径可见 Skill：19 个；
- SKILL.md 总数：21 个。

内部模块（不再单独出现在 DAG）：`source_snapshot`、`evidence_governance`、
`claim_verification`、`citation_management`、`content_optimization`。

## 主编排 Skill

| # | Canonical name | 路径 |
|---:|---|---|
| M1 | `research_report_orchestrator` | `skills/research_report_orchestrator/SKILL.md` |

## 可执行 Skill

| # | Canonical name | DAG 顺序 | 路径 |
|---:|---|---:|---|
| 1 | `capability_sweep` | 1 | `skills/capability_sweep/SKILL.md` |
| 2 | `requirements_analysis` | 2 | `skills/requirements_analysis/SKILL.md` |
| 3 | `skill_research` | 3 | `skills/skill_research/SKILL.md` |
| 4 | `writing_standards` | 4 | `skills/writing_standards/SKILL.md` |
| 5 | `issue_tree` | 5 | `skills/issue_tree/SKILL.md` |
| 6 | `outline` | 6 | `skills/outline/SKILL.md` |
| 7 | `research` | 7 | `skills/research/SKILL.md` |
| 8 | `evidence_pipeline` | 8 | `skills/evidence_pipeline/SKILL.md` |
| 9 | `data_processing` | 9 | `skills/data_processing/SKILL.md` |
| 10 | `quant_finance_research` | 10（条件） | `skills/quant_finance_research/SKILL.md` |
| 11 | `material_integration` | 11 | `skills/material_integration/SKILL.md` |
| 12 | `visualization` | 12 | `skills/visualization/SKILL.md` |
| 13 | `writing` | 13 | `skills/writing/SKILL.md` |
| 14 | `writing_finalize` | 14 | `skills/writing_finalize/SKILL.md` |
| 15 | `pressure_test` | 15 | `skills/pressure_test/SKILL.md` |
| 16 | `formatting` | 16 | `skills/formatting/SKILL.md` |
| 17 | `review` | 17 | `skills/review/SKILL.md` |
| 18 | `quality_gate` | 18 | `skills/quality_gate/SKILL.md` |
| 19 | `publish` | 19 | `skills/publish/SKILL.md` |
| 20 | `experience_evolution` | 20 | `skills/experience_evolution/SKILL.md` |

四个确认节点不是 Skill，不计入上表：

`issue_tree_confirmation`、`outline_confirmation`、`draft_confirmation`、
`pre_review_confirmation`。
