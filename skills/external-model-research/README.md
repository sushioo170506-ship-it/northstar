# External Model Research Skills

本目录提供“外部模型调研报告自动化工作流”的主编排 Skill + 7 个子 Skill。

## Orchestrator

- [model-report-orchestrator](./model-report-orchestrator/SKILL.md)

## Step Skills

1. [mr-step1-scope](./skill_01_brief/SKILL.md)
2. [mr-step2-outline](./skill_02_outline/SKILL.md)
3. [mr-step3-collect](./skill_03_evidence/SKILL.md)
4. [mr-step4-process](./skill_04_orchestration/SKILL.md)
5. [mr-step5-write](./skill_05_write_decide/SKILL.md)
6. [mr-step6-review](./skill_06_review/SKILL.md)
7. [mr-step7-output](./skill_07_publish/SKILL.md)

## Shared Standards

- 评分标准（rubric）：[model-report-rubric.yaml](./model-report-rubric.yaml)
- 模块清单（playbook）：[model-report-playbook.md](./model-report-playbook.md)
- 文档风格规范（style guide）：[skills-style-guide.md](./skills-style-guide.md)
- 风格检查脚本：`python3 /workspace/scripts/check_external_model_skills_style.py`

## Recommended Workflow

`scope -> outline -> collect -> process -> write -> review -> output`

回路规则：
- `step4 -> step3`（素材缺失）
- `step6 -> step3`（事实性问题）
- `step6 -> step4`（完整性问题）
- `step6 -> step5`（风格/逻辑/可读性问题）

质量底线（长篇）：
- 来源 >= 25（官方 >= 8，第三方 >= 10）
- benchmark 指标 >= 25（覆盖维度 >= 8）
- 竞品 >= 5
- 表格 >= 12
- 图表规格 >= 4
- 参考文献 >= 30
- 复核总分 >= 90（关键维度 >= 18）

