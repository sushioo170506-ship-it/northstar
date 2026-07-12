---
name: requirements-analysis
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
