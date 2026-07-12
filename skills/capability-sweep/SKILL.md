---
name: capability-sweep
description: 工作流 Step 0 — 全量遍历内置 Skill 与外部集成目录，记录适用性、配置和跳过原因。
license: MIT
version: 1.0.0
---

# Capability Sweep

## 职责边界

只做能力盘点和执行计划，不调用检索、写作或渲染程序，不把“已发现”写成“已执行”。

## WHEN / INPUT / OUTPUT

- WHEN：每个新工作流第一个执行；不得跳过。
- INPUT：ReportConfig.extra.enabled_integrations / disabled_integrations。
- OUTPUT：`capability_manifest`，含全部内置 Skill、外部集成、许可证、星数快照、状态和理由。

## 执行规则

1. 内置 Skill 必须与 `BUILTIN_SKILL_ORDER` 完全一致并标记 scheduled。
2. 外部目录逐项标记 configured、disabled_by_config 或 reviewed_not_configured。
3. 配置不等于执行；对应业务节点必须在产物元数据中另行记录实际调用。
4. 无明确许可证、认证失败或不适用的能力不得为满足遍历要求而强行执行。

## 质量卡口与错误

- 外部目录遍历数必须等于目录总数。
- 内置 Skill 少一项即失败。
- 未配置能力必须给 reason；静默跳过即失败。
- 目录损坏或 schema 不完整：节点 failed，从 capability_sweep 重试。
