---
name: material_integration
description: 将治理后的调研素材按最终大纲章节挂载并计算覆盖率。
license: MIT
version: 1.0.0
---

# Material Integration

实现：`research_workflow.skills.material_integration.MaterialIntegrationSkill`。

输入 `outline`、`research`、`evidence_governance`、`data_processing`，输出
`artifact_type="section_materials"`。每项材料保留 source_id、类别、原始 URL、内容摘要和
用途，并根据 issue_ids 与 outline.linked_issue 映射到章节；摘要、风险和结论等综合章节引用
全部来源。

`mount_coverage < 1.0` 会被压力测试和复核标记，不能作为完整素材包发布。

## 执行与边界

1. 仅按 issue_ids→linked_issue 映射，不通过关键词猜章节。
2. 综合章节可引用全部来源，但不计入严格 mount_coverage。
3. 每项素材附 claim_ids、evidence_grades、original_url 和 usage。
4. 一个素材可挂多节，但每处必须说明用途；不得复制成多个“独立来源”。

不得修改来源等级、生成评分或撰写正文。错误 issue_id 计为 unmapped，质量门会重新计算而不
信任自报覆盖率。修复映射退回 material_integration；来源本身错误退回 research。

## 统一输出格式约束

凡本Skill输出、改写或传递Markdown/报告正文，必须遵守：业务流程、逻辑链路和路径走向使用结构化Mermaid流程图；每张统计或说明表后附字段定义、数据逻辑与结论依据；同层有序列表连续递增、子层独立编号，禁止重复“1.”；外部链接保留可点击Markdown语法并由`content_optimization`生成文末全量链接索引。JSON-only产物也不得破坏下游执行这些规则所需的数据和URL。
