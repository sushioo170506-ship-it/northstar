---
name: research-report-orchestrator
description: 持久化编排研究报告的检索、大纲、撰写、排版和审核流程，支持人工确认与断点续改。
license: MIT
version: 1.0.0
---

# Research Report Orchestrator

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

1. `requirements_analysis`
2. `issue_tree`
3. `issue_tree_confirmation`（主题与多层级问题确认）
4. `outline`
5. `outline_confirmation`（最终大纲确认）
6. `research`（确认大纲后调研）
7. `evidence_governance`
8. `material_integration`
9. `visualization`
10. `writing`
11. `pressure_test`
12. `draft_confirmation`（强制人工确认）
13. `formatting`
14. `pre_review_confirmation`（强制人工确认）
15. `review`
16. `quality_gate`（三类来源、链接、D1–D7 与红线发布阻断）

`run()` 在确认点返回 `waiting_confirmation`。调用
`confirm(workflow_id, checkpoint_id, comment)` 后再次 `run()`。不得跳过确认。
质量门拒绝时抛出 `QualityGateRejected`，保留评分产物，且终稿不可读取。

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
- 终稿：仅当 `review` 和 `quality_gate` 完成且工作流状态为 `completed` 时可读取。

## 内置调度 Prompt

```text
你是研究报告主编排器。必须严格依据 workflow_id={workflow_id} 的持久化状态执行：
1. 只运行依赖已完成且当前未完成的节点；
2. 所有 Skill 只接收标准 SkillRequest，不读取隐式会话状态；
3. 在 issue_tree_confirmation、outline_confirmation、draft_confirmation、
   pre_review_confirmation 停止并等待人工确认；
4. 修改 {target_node} 时，仅失效该节点及其 DAG 后代，保留其他有效产物；
5. 每次调用前按 workflow_id、依赖节点、主题检索上下文，并校验产物 checksum；
6. quality_gate 触发证据红线或低于阈值时必须阻断发布；
7. 失败时记录错误，恢复后从失败节点继续，禁止重复已完成节点。
统一参数：{config_json}
```

生产环境可向 `SkillRegistry` 注入独立部署的 Skill RPC 代理；协议保持不变。
