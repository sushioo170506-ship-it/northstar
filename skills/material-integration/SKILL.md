---
name: material-integration
description: 将治理后的调研素材按最终大纲章节挂载并计算覆盖率。
license: MIT
version: 1.0.0
---

# Material Integration

实现：`research_workflow.skills.material_integration.MaterialIntegrationSkill`。

输入 `outline`、`research`、`evidence_governance`，输出
`artifact_type="section_materials"`。每项材料保留 source_id、类别、原始 URL、内容摘要和
用途，并根据 issue_ids 与 outline.linked_issue 映射到章节；摘要、风险和结论等综合章节引用
全部来源。

`mount_coverage < 1.0` 会被压力测试和复核标记，不能作为完整素材包发布。
