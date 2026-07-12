---
name: quality-gate
description: 按 D1-D7 评分并根据证据红线作出允许或阻断发布的最终决定。
license: MIT
version: 1.0.0
---

# Quality Gate

实现：`research_workflow.skills.quality_gate.QualityGateSkill`。

输入 `review`、`evidence_governance`、`pressure_test`，输出
`artifact_type="quality_gate"`，包含：

- D1 事实准确性
- D2 逻辑严密性
- D3 事实与观点分离
- D4 结构完整性
- D5 So What
- D6 时效性与边界感
- D7 量级感
- 红线、问题、必需修复项和发布决定

默认通过线为 24/35。没有可追溯来源、任一红线或总分不足，都会持久化评估产物、把
quality_gate 和工作流设为 failed，并抛出 `QualityGateRejected`。终稿在工作流重新通过
质量门前不可通过公开 API 或默认状态存储读取。
