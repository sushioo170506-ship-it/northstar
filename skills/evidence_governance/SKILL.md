---
name: evidence_governance
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
即使没有红线，缺少 industry、academic、social_media 任一类别或原始 URL 覆盖不足 100%，
质量门仍会阻断。

## WHEN / 边界

- WHEN：research 完成；不得自行联网补来源。
- 只治理 source provenance，不提炼论断、不评分、不写正文；论断级工作属于 data_processing。

## 治理规则

1. 校验主体、标题、URL、发布时间、类别、issue_ids。
2. 标记 primary/independent/stakeholder/community 和利益关系。
3. 建立 issue_coverage 与 original_link_coverage。
4. 对关键来源检查独立验证；冲突只登记，不强行选择。
5. 红线：fabricated；关键来源不可追溯；关键判断仅由单一利益方支撑。

## 错误处理

- URL/时间缺失：保留来源并降级，不自动补写。
- 来源类别错误：归一化失败则标 unknown，质量门阻断。
- 明示 fabricated：保存审计证据后触发红线。
- 模型分析仅为辅助字段，不能覆盖确定性指标和红线。
