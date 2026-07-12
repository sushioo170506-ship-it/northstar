---
name: quality-gate
description: 按 D1-D7 评分并根据证据红线作出允许或阻断发布的最终决定。
license: MIT
version: 1.0.0
---

# Quality Gate

实现：`research_workflow.skills.quality_gate.QualityGateSkill`。

输入 `requirements_analysis`、`review`、`evidence_governance`、`pressure_test`，输出
`artifact_type="quality_gate"`，包含：

- D1 事实准确性
- D2 逻辑严密性
- D3 事实与观点分离
- D4 结构完整性
- D5 So What
- D6 时效性与边界感
- D7 量级感
- 红线、问题、必需修复项和发布决定

默认通过线为 24/35。缺少 official、academic、social_media 任一来源类别、原始 URL 覆盖
不足 100%、终稿未包含全部来源链接、违反内容边界、篇幅不足、任一红线或总分不足，都会
持久化评估产物并阻断发布。质量门还会从证据 issue_ids 和章节 linked_issue 重新计算素材
挂载覆盖率，并要求至少一个结构完整的可视化资产，不能只信任上游自报指标。
