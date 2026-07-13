---
name: requirements_analysis
description: 完整提取报告产出形态、主题、文风、受众、篇幅、格式、边界、资料和前置思考。
license: MIT
version: 1.0.0
---

# Requirements Analysis

实现：`research_workflow.skills.requirements_analysis.RequirementsAnalysisSkill`。

输入为统一 `ReportConfig`，输出 `artifact_type="requirements_brief"`，包含 deliverable、
topic、style、audience、content_boundaries、reference_inventory、prior_thoughts 和
missing_or_defaulted。所有后续节点使用该简报，不再从隐式会话猜测需求。

离线实现会显式标记默认受众、空边界和缺失资料；注入 TextGenerator 时仍必须输出完整 JSON
字段，缺少任一核心需求维度都会校验失败。

## WHEN / SKIP / 边界

- WHEN：capability_sweep 完成后；每个工作流必跑一次。
- SKIP：never。
- 只提取和标准化需求；不得拆问题、设计章节、检索或代替用户补充限制。

## 执行步骤

1. 识别产出类型、主题、目标受众和使用决策。
2. 统一篇幅、语言、文风、格式和内容边界。
3. 记录workflow_profile（quick/standard/deep/regulatory）并明确确认与质量门级别。
4. 盘点用户资料：数量、类别、URL 是否存在；不判断真实性。
5. 原样保留 prior_thoughts，并区分用户观点与已证事实。
6. 把默认值和缺失维度写入 missing_or_defaulted。

## MUST / MUST NOT / ON_FAIL

- MUST：九类需求字段齐全；默认值显式；边界保持原文。
- MUST NOT：将缺失信息虚构为用户要求；把 prior_thoughts 当成结论。
- ON_FAIL：字段类型错误直接 failed；用户变更主题/受众/边界时从本节点失效全部后代。

## 统一输出格式约束

凡本Skill输出、改写或传递Markdown/报告正文，必须遵守：业务流程、逻辑链路和路径走向使用结构化Mermaid流程图；每张统计或说明表后附字段定义、数据逻辑与结论依据；同层有序列表连续递增、子层独立编号，禁止重复“1.”；外部链接保留可点击Markdown语法并由`content_optimization`生成文末全量链接索引。JSON-only产物也不得破坏下游执行这些规则所需的数据和URL。
