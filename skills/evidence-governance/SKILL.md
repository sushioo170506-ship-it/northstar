---
name: evidence-governance
description: 审核来源可追溯性、利益相关性、独立验证和关键证据红线。
license: MIT
version: 1.0.0
---

# Evidence Governance

实现：`research_workflow.skills.evidence_governance.EvidenceGovernanceSkill`。

输入 `research` 与已确认 `issue_tree`，输出 `artifact_type="evidence_ledger"`，包括来源账本、
议题覆盖、来源类别、原始链接覆盖率、可追溯率、关键来源独立覆盖率、一般问题和红线。

当前确定性红线：

- 来源显式标记 `fabricated=true`；
- `critical=true` 的来源无法追溯；
- 关键论断仅依赖 stakeholder 来源且无 `independent_verification`。

无法验证不会自动等同于虚假；非关键缺失信息作为问题披露。质量门消费红线并阻断发布。
即使没有红线，缺少 official、academic、social_media 任一类别或原始 URL 覆盖不足 100%，
质量门仍会阻断。
