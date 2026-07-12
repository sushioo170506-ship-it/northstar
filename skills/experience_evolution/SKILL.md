---
name: experience_evolution
description: 从用户修改与评论中提取通用经验，生成待验证学习提案和季度自进化复盘。
license: MIT
version: 1.0.0
---

# Experience Evolution

## 职责与安全边界

负责经验提取、分类、频次和有效性评估；不得未经审批直接改生产Skill。

## 输入输出

- WHEN：publish之后，每轮必执行。
- INPUT：用户操作审计、quality_gate、publish、skill_research。
- OUTPUT：`evolution_report`，包含period、proposals、effectiveness和policy。

## 提取规则

- 只处理modify、comment、route_revision、update_sources。
- 按大纲、调研、数据、图表、写作、引用、格式、质量门和编排分类。
- “每次、以后、默认、所有、通用、应该”等表达标记general_signal。
- 相同规范化经验累计frequency。

## 有效性验证

- 质量门通过，并且经验重复出现≥2次或明确声明为通用规则，才成为validated_candidate。
- 其他提案保持pending_validation。
- 每项记录目标Skill、原始规则、频次、置信度、证据操作和审批要求。

## 受控写入

`apply_approved_learning`只允许：

1. validated_candidate；
2. 明确approved_by；
3. canonical Skill目录；
4. `MANAGED_LEARNINGS`受控区；
5. 幂等写入和操作审计。

默认automatic_repo_write=false。季度报告汇总工作流数、提案数、已验证候选和平均质量分。
