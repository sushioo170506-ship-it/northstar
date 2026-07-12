# Skill 唯一清单

本文件是人类可读镜像；代码事实源为
`research_workflow.integrations.BUILTIN_SKILL_ORDER`。检查规则要求目录名、SKILL.md
frontmatter `name`、Python `Skill.name`、DAG node id 四者一致。

## 计数口径

- 主编排 Skill：1 个，不作为 DAG 功能节点执行；
- 可执行 Skill：18 个，全部出现在 DAG；
- SKILL.md 总数：19 个。

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
| 4 | `issue_tree` | 4 | `skills/issue_tree/SKILL.md` |
| 5 | `outline` | 5 | `skills/outline/SKILL.md` |
| 6 | `research` | 6 | `skills/research/SKILL.md` |
| 7 | `evidence_governance` | 7 | `skills/evidence_governance/SKILL.md` |
| 8 | `data_processing` | 8 | `skills/data_processing/SKILL.md` |
| 9 | `material_integration` | 9 | `skills/material_integration/SKILL.md` |
| 10 | `visualization` | 10 | `skills/visualization/SKILL.md` |
| 11 | `writing` | 11 | `skills/writing/SKILL.md` |
| 12 | `citation_management` | 12 | `skills/citation_management/SKILL.md` |
| 13 | `pressure_test` | 13 | `skills/pressure_test/SKILL.md` |
| 14 | `formatting` | 14 | `skills/formatting/SKILL.md` |
| 15 | `review` | 15 | `skills/review/SKILL.md` |
| 16 | `quality_gate` | 16 | `skills/quality_gate/SKILL.md` |
| 17 | `publish` | 17 | `skills/publish/SKILL.md` |
| 18 | `experience_evolution` | 18 | `skills/experience_evolution/SKILL.md` |

四个确认节点不是 Skill，不计入上表：

`issue_tree_confirmation`、`outline_confirmation`、`draft_confirmation`、
`pre_review_confirmation`。
