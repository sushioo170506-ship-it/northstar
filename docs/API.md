# API 与独立调用指南

## 配置

| 字段 | 类型 | 规则 |
|---|---|---|
| `topic` | string | 必填，去除多余空白，1–500 字符 |
| `expected_length` | integer | 500–500000，默认 5000 |
| `style` | string | 默认“专业、客观、证据驱动” |
| `output_format` | string | markdown/html/json/text；支持 md/htm/txt 别名 |
| `language` | string | 默认 zh-CN |
| `output_type` | string | 具体产出形态，默认 research_report |
| `audience` | string | 目标受众，默认通用专业读者 |
| `content_boundaries` | string[] | 内容禁止项、范围和合规边界 |
| `prior_thoughts` | string | 用户对问题的前置判断或假设 |
| `extra` | object | 可包含 `sources` 等适配器参数 |

## Python API

```python
orchestrator = ResearchReportOrchestrator(data_dir)
workflow_id = orchestrator.create(config)
outcome = orchestrator.run(workflow_id)
orchestrator.confirm(workflow_id, outcome.waiting_at, "同意")
affected = orchestrator.modify(workflow_id, "writing", "补充反方证据")
affected = orchestrator.update_sources(workflow_id, new_sources, "修复证据红线")
target, affected = orchestrator.request_revision(workflow_id, "补充图表并调整架构图")
snapshot = orchestrator.state.snapshot(workflow_id)
report = orchestrator.final_report(workflow_id)
```

`run` 返回 `RunOutcome(workflow_id, status, waiting_at, final_artifact_id)`。确认节点依次为
`issue_tree_confirmation`、`outline_confirmation`、`draft_confirmation`、
`pre_review_confirmation`。允许修改的产物节点：
`capability_sweep`、`requirements_analysis`、`skill_research`、`issue_tree`、`outline`、`research`、
`evidence_governance`、`data_processing`、`material_integration`、`visualization`、`writing`、
`pressure_test`、`formatting`、`review`、`quality_gate`、`publish`。

质量门缺少产业/学术/实景任一支柱、原始链接/claim/素材/图表不足、触发红线、需求不合规
或总分低于 24/35 时，`run` 抛出
`QualityGateRejected`，但评分产物已持久化。
修改上游问题并重新确认后，可按 DAG 选择性重跑；工作流完成前 `final_report` 拒绝返回内容。
工作流完成后 `final_report` 读取 `publish` 的 `published_report`，而不是未过门的 review 候选稿。

`skill_research` 默认使用已核验目录。设置 `extra.live_skill_research=true` 后追加 GitHub
Search API 实时检索；`extra.skill_candidates` 可注入 OpenClaw Hub 或其他仓库候选，每项必须
提供 name、source_url、author、license、version、channel。改造结果仅生成
`pending_human_review` 规范，不会在同一工作流动态执行远程代码。

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

调研适配器实现 `SourceRetriever.retrieve(topic, questions, categories)`；research 会分别以
industry、academic、social_media 单类别调用三次。每个返回项至少应含 id、title、category、url、
published_at、content、issue_ids；内置模式没有检索器时仅整理用户 sources。

```json
{"sources": [
  {"id": "S1", "title": "官方/产业原文", "category": "industry",
   "url": "https://example.org/official", "published_at": "2026-07-01",
   "content": "...", "issue_ids": ["ISSUE-01"]}
]}
```

## CLI

```bash
research-workflow --data-dir ./data create \
  --topic "AI 治理" --length 8000 --style "政策研究" --format markdown \
  --output-type "决策研究报告" --audience "企业管理层" \
  --boundary "不得包含：未标明来源的数据" --prior-thoughts "需平衡创新与风险"
research-workflow --data-dir ./data run WORKFLOW_ID
research-workflow --data-dir ./data confirm WORKFLOW_ID outline_confirmation
research-workflow --data-dir ./data modify WORKFLOW_ID writing "补充风险情景"
research-workflow --data-dir ./data revise WORKFLOW_ID "图表需要改为流程图"
research-workflow --data-dir ./data update-sources WORKFLOW_ID sources.json \
  --reason "替换不可追溯来源"
research-workflow --data-dir ./data status WORKFLOW_ID
research-workflow --data-dir ./data final WORKFLOW_ID > report.md
```

所有 CLI 结构化结果为 JSON，错误写入 stderr 并返回退出码 2。
