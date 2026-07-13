# Skill 唯一清单

本文件是人类可读镜像；代码事实源为
`research_workflow.integrations.BUILTIN_SKILL_ORDER`。检查规则要求目录名、SKILL.md
frontmatter `name`、Python `Skill.name`、DAG node id 四者一致。

## 计数口径

- 主编排 Skill：1 个，不作为 DAG 功能节点执行；
- 可执行 Skill：23 个，全部出现在 DAG；
- SKILL.md 总数：24 个。

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
| 8 | `source_snapshot` | 8 | `skills/source_snapshot/SKILL.md` |
| 9 | `evidence_governance` | 9 | `skills/evidence_governance/SKILL.md` |
| 10 | `data_processing` | 10 | `skills/data_processing/SKILL.md` |
| 11 | `claim_verification` | 11 | `skills/claim_verification/SKILL.md` |
| 12 | `quant_finance_research` | 12 | `skills/quant_finance_research/SKILL.md` |
| 13 | `material_integration` | 13 | `skills/material_integration/SKILL.md` |
| 14 | `visualization` | 14 | `skills/visualization/SKILL.md` |
| 15 | `writing` | 15 | `skills/writing/SKILL.md` |
| 16 | `citation_management` | 16 | `skills/citation_management/SKILL.md` |
| 17 | `content_optimization` | 17 | `skills/content_optimization/SKILL.md` |
| 18 | `pressure_test` | 18 | `skills/pressure_test/SKILL.md` |
| 19 | `formatting` | 19 | `skills/formatting/SKILL.md` |
| 20 | `review` | 20 | `skills/review/SKILL.md` |
| 21 | `quality_gate` | 21 | `skills/quality_gate/SKILL.md` |
| 22 | `publish` | 22 | `skills/publish/SKILL.md` |
| 23 | `experience_evolution` | 23 | `skills/experience_evolution/SKILL.md` |

四个确认节点不是 Skill，不计入上表：

`issue_tree_confirmation`、`outline_confirmation`、`draft_confirmation`、
`pre_review_confirmation`。
