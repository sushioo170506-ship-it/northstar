---
name: research_report_orchestrator
description: 持久化编排研究报告的检索、大纲、撰写、排版和审核流程，支持人工确认与断点续改。
license: MIT
version: 1.0.0
---

# Research Report Orchestrator

## 角色定位与禁止越界

本 Skill 是确定性编排器，不是研究、评分、写作或制图方法论容器。它只负责：读取持久化状态、
按 DAG 调用子 Skill、传递不可变产物、暂停人工确认、执行发布卡口。不得在编排器内补写正文、
伪造来源、替代子 Skill 打分，或为了“遍历”重复调用同一能力。

## 触发条件

当用户要求生成、恢复、修改或审核研究报告时调用。输入必须包含 `topic`，可选
`expected_length`、`style`、`output_format`、`language`、`output_type`、`audience`、
`content_boundaries`、`prior_thoughts` 和 `extra.sources`。

## 标准调用

```python
from research_workflow import ResearchReportOrchestrator

workflow = ResearchReportOrchestrator("/var/lib/research-workflow")
workflow_id = workflow.create({
    "topic": "研究主题",
    "expected_length": 8000,
    "style": "专业、客观、证据驱动",
    "output_format": "markdown",
    "extra": {"sources": [{"id": "S1", "title": "资料", "content": "..."}]},
})
outcome = workflow.run(workflow_id)
```

## 时序与确认

1. `requirements_analysis`（内部执行`capability_sweep`）
2. `writing_standards`（内部执行`skill_research`）
3. `issue_tree` → `issue_tree_confirmation`
4. `outline` → `outline_confirmation`
5. `research`：按场景执行来源pass
6. `evidence_pipeline`（内部执行来源快照与证据治理）
7. `data_processing`（内部执行claim ledger与逐论断验证）
8. `compose`（内部执行素材、可视化、写作、引用、内容优化和压力测试）
   → `draft_confirmation`
9. `output_format_confirmation`：用户选择最终文件/远程文档格式
10. `formatting` → `pre_review_confirmation`
11. `quality_assurance`（内部执行量化条件校验、review与quality_gate）
12. `publish`
13. `experience_evolution`（无反馈操作时条件跳过；不计入常驻主路径）

`run()` 在确认点返回 `waiting_confirmation`。调用
`confirm(workflow_id, checkpoint_id, comment)` 后再次 `run()`。不得跳过确认。
质量门拒绝时抛出 `QualityGateRejected`，保留评分产物，且终稿不可读取。

## 遍历规则

- 12 个DAG Skill均有持久化状态；23项原始职责在合并管道内按固定顺序执行。
- 外部集成先由`requirements_analysis`内的capability_sweep遍历；已配置者交给对应节点调用，未配置者记录
  `reviewed_not_configured` 和原因。禁止静默跳过。
- 条件能力输出结构化`not_applicable`或`conditional_skip`，不得伪造结果。
- “调用全部”不等于“执行全部第三方程序”；无凭证、无许可证或不适用组件不得运行。

## 工作流Profile

| Profile | 人工确认 | 质量分 | 高等级证据 | 最少图表 |
|---|---:|---:|---:|---:|
| quick | 2 | 22 | 60% | 3 |
| standard | 3 | 24 | 75% | 4 |
| deep（默认） | 5 | 24 | 80% | 6 |
| regulatory | 5 | 30 | 90% | 6 |

未启用的确认节点仍写入 completed，并记录 auto_skip_checkpoint 和Profile，不得直接消失。

节点评论通过 `add_comment(..., actor_id=...)` 追加审计，不自动失效产物；需要修改时必须另行
调用 request_revision/modify，避免评论与执行状态混淆。

## 阶段质量卡口

| 阶段 | 卡口 | 失败退回 |
|---|---|---|
| Skill 研究 | 来源、作者、版本、许可证齐全；未知许可拒绝 | writing_standards |
| 议题树 | 3–7 个必要、可证伪、可行动问题 | issue_tree |
| 大纲 | 核心判断、章节结论、锚点、证伪条件齐全 | outline |
| 调研 | industry/academic/social_media 三 pass 均有记录 | research |
| 数据处理 | 论断可追溯、冲突显式、主观评分禁止 | data_processing |
| 成文 | 素材挂载、可视化、引用、结构和压力测试完整 | compose |
| 发布 | 红线、链接、claim、挂载、边界和硬门全通过 | quality_assurance |

## 参数和产物传递

- 全局参数只从持久化的 `ReportConfig` 读取，Skill 不得私自覆盖。
- Skill 输入为 `SkillRequest`，输出为 `SkillResult`。
- 节点通过不可变产物 ID 传递数据；数据库记录输入 ID、输出 ID、版本和 checksum。
- 依赖产物按完整内容传入；语义上下文按 workflow/node 元数据过滤后从向量库增量加载。
- Skill 不读取其他 Skill 的内部实现或隐式对话历史。

## 断点续改

`modify(workflow_id, target_node, feedback)` 通过 DAG 计算目标节点及全部后代，只将这些
节点标记为 `invalidated`，清除受影响的确认，保留其他节点和全部历史产物。下一次
`run()` 从最早失效节点恢复。每次创建、确认和修改都写入用户操作审计表。

## 节点校验

- 调用前：所有依赖必须为 `completed`，每个输入产物通过 SHA-256 校验。
- 调用后：内容和产物类型不得为空，结果写入关系库与向量库后才提交节点完成状态。
- 异常：节点为 `failed` 并持久化错误；重新运行只重试失败节点。
- 终稿：仅当 `publish` 完成且工作流状态为 `completed` 时可读取。

## 内置调度 Prompt

```text
你是研究报告主编排器。必须严格依据 workflow_id={workflow_id} 的持久化状态执行：
1. 只运行依赖已完成且当前未完成的节点；
2. 所有 Skill 只接收标准 SkillRequest，不读取隐式会话状态；
3. 在 issue_tree_confirmation、outline_confirmation、draft_confirmation、
   output_format_confirmation、pre_review_confirmation 停止并等待人工确认；
4. 输出格式确认必须展示允许格式和渲染要求，不得沿用默认值代替用户选择；
5. 修改 {target_node} 时，仅失效该节点及其 DAG 后代，保留其他有效产物；
6. 每次调用前按 workflow_id、依赖节点、主题检索上下文，并校验产物 checksum；
7. requirements_analysis必须遍历内置能力与外部集成目录，跳过必须有理由；
8. quality_assurance触发证据红线时必须阻断publish；
9. 失败时记录错误，恢复后从失败节点继续，禁止重复已完成节点。
统一参数：{config_json}
```

生产环境可向 `SkillRegistry` 注入独立部署的 Skill RPC 代理；协议保持不变。

## 统一输出格式约束

凡本Skill输出、改写或传递Markdown/报告正文，必须遵守：业务流程、逻辑链路和路径走向使用结构化Mermaid流程图；每张统计或说明表后附字段定义、数据逻辑与结论依据；同层有序列表连续递增、子层独立编号，禁止重复“1.”；外部链接保留可点击Markdown语法并由`content_optimization`生成文末全量链接索引。JSON-only产物也不得破坏下游执行这些规则所需的数据和URL。
