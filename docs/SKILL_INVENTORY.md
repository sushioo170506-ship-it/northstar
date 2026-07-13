# Skill 唯一清单

本文件是人类可读镜像；代码事实源为
`research_workflow.integrations.BUILTIN_SKILL_ORDER`。检查规则要求目录名、SKILL.md
frontmatter `name`、Python `Skill.name`、DAG node id 四者一致。

## 计数口径

- 主编排 Skill：1 个，不作为 DAG 功能节点执行；
- 可执行 Skill：12 个，全部出现在 DAG；
- 其中条件节点：1 个（`experience_evolution`，无反馈操作时跳过）；
- 主路径常驻 Skill：11 个；
- SKILL.md 总数：13 个。

内部模块（不再单独出现在 DAG）：`capability_sweep`、`skill_research`、
`source_snapshot`、`evidence_governance`、`claim_verification`、
`quant_finance_research`、`material_integration`、`visualization`、`writing`、
`citation_management`、`content_optimization`、`writing_finalize`、`pressure_test`、
`review`、`quality_gate`。

## 主编排 Skill

| # | Canonical name | 路径 |
|---:|---|---|
| M1 | `research_report_orchestrator` | `skills/research_report_orchestrator/SKILL.md` |

## 可执行 Skill

| # | Canonical name | DAG 顺序 | 路径 |
|---:|---|---:|---|
| 1 | `requirements_analysis` | 1（内含 capability_sweep） | `skills/requirements_analysis/SKILL.md` |
| 2 | `writing_standards` | 2（内含 skill_research） | `skills/writing_standards/SKILL.md` |
| 3 | `issue_tree` | 3 | `skills/issue_tree/SKILL.md` |
| 4 | `outline` | 4 | `skills/outline/SKILL.md` |
| 5 | `research` | 5 | `skills/research/SKILL.md` |
| 6 | `evidence_pipeline` | 6 | `skills/evidence_pipeline/SKILL.md` |
| 7 | `data_processing` | 7（内含 claim_verification） | `skills/data_processing/SKILL.md` |
| 8 | `compose` | 8 | `skills/compose/SKILL.md` |
| 9 | `formatting` | 9 | `skills/formatting/SKILL.md` |
| 10 | `quality_assurance` | 10 | `skills/quality_assurance/SKILL.md` |
| 11 | `publish` | 11 | `skills/publish/SKILL.md` |
| 12 | `experience_evolution` | 12（条件） | `skills/experience_evolution/SKILL.md` |

四个确认节点不是 Skill，不计入上表：

`issue_tree_confirmation`、`outline_confirmation`、`draft_confirmation`、
`pre_review_confirmation`。
