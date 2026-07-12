# API 与独立调用指南

## 配置

| 字段 | 类型 | 规则 |
|---|---|---|
| `topic` | string | 必填，去除多余空白，1–500 字符 |
| `expected_length` | integer | 500–500000，默认 5000 |
| `style` | string | 默认“专业、客观、证据驱动” |
| `output_format` | string | markdown/html/json/text；支持 md/htm/txt 别名 |
| `language` | string | 默认 zh-CN |
| `extra` | object | 可包含 `sources` 等适配器参数 |

## Python API

```python
orchestrator = ResearchReportOrchestrator(data_dir)
workflow_id = orchestrator.create(config)
outcome = orchestrator.run(workflow_id)
orchestrator.confirm(workflow_id, outcome.waiting_at, "同意")
affected = orchestrator.modify(workflow_id, "writing", "补充反方证据")
affected = orchestrator.update_sources(workflow_id, new_sources, "修复证据红线")
snapshot = orchestrator.state.snapshot(workflow_id)
report = orchestrator.final_report(workflow_id)
```

`run` 返回 `RunOutcome(workflow_id, status, waiting_at, final_artifact_id)`。确认节点依次为
`issue_tree_confirmation`、`outline_confirmation`、`draft_confirmation`、
`pre_review_confirmation`。允许修改的产物节点：
`research`、`issue_tree`、`evidence_governance`、`outline`、`writing`、
`pressure_test`、`formatting`、`review`、`quality_gate`。

质量门没有可追溯来源、触发红线或总分低于 24/35 时，`run` 抛出
`QualityGateRejected`，但评分产物已持久化。
修改上游问题并重新确认后，可按 DAG 选择性重跑；工作流完成前 `final_report` 拒绝返回内容。

## Skill 接口

```python
@dataclass(frozen=True)
class SkillRequest:
    workflow_id: str
    node_id: str
    config: ReportConfig
    inputs: dict[str, Any]
    context: tuple[ContextItem, ...]
    feedback: tuple[str, ...]

@dataclass(frozen=True)
class SkillResult:
    content: str
    artifact_type: str
    metadata: dict[str, Any]
```

Skill 实现 `name`、`version`、`execute(request)`，经 `SkillRegistry.register()` 注入。远程部署
时可实现一个 RPC Proxy Skill：序列化同一请求，调用独立服务并反序列化同一结果。

## CLI

```bash
research-workflow --data-dir ./data create \
  --topic "AI 治理" --length 8000 --style "政策研究" --format markdown
research-workflow --data-dir ./data run WORKFLOW_ID
research-workflow --data-dir ./data confirm WORKFLOW_ID outline_confirmation
research-workflow --data-dir ./data modify WORKFLOW_ID writing "补充风险情景"
research-workflow --data-dir ./data update-sources WORKFLOW_ID sources.json \
  --reason "替换不可追溯来源"
research-workflow --data-dir ./data status WORKFLOW_ID
research-workflow --data-dir ./data final WORKFLOW_ID > report.md
```

所有 CLI 结构化结果为 JSON，错误写入 stderr 并返回退出码 2。
