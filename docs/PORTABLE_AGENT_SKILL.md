# 跨 Agent 本地调用

本项目不要求部署服务即可在 Cursor、Claude Code、Codex、Trae、Qoder 和 WorkBuddy 中复用。
推荐形态是：

```text
一个对外 Agent Skill
        ↓
本地 CLI / Python 工作流
        ↓
12个 DAG 节点 + SQLite 状态 + 本地文件
```

Agent Skill 是入口和操作手册，不是工作流实现本身。完整代码仍由本地Python执行，工作流状态
保存在仓库根目录`.research-workflow/`。因此更换对话或Agent后，只要打开同一仓库并提供
`workflow_id`即可恢复。

## 项目级安装位置

仓库已包含以下同步副本：

| Agent | 路径 |
|---|---|
| Cursor | `.cursor/skills/research-report-workflow/` |
| Claude Code | `.claude/skills/research-report-workflow/` |
| Codex | `.agents/skills/research-report-workflow/` |
| Trae | `.trae/skills/research-report-workflow/` |
| Qoder | `.qoder/skills/research-report-workflow/` |
| WorkBuddy | `.codebuddy/skills/research-report-workflow/` |

规范源位于`agent-skills/research-report-workflow/`。修改规范源后运行：

```bash
python3 scripts/sync_agent_skill.py
```

同步脚本会覆盖各平台副本；不得直接分别维护六份内容。首次安装后应重启或刷新Agent，使其重新
扫描Skill目录。各平台通常支持自动触发，也可以显式调用：

```text
Cursor/Claude/Qoder: /research-report-workflow
Codex: $research-report-workflow
Trae/WorkBuddy: 从“/”或Skill面板选择
```

## 一次本地调用

Skill会引导Agent创建完整配置并调用统一启动器：

```bash
python3 .cursor/skills/research-report-workflow/scripts/workflow.py \
  create-config /path/to/config.json
```

运行到确认点：

```bash
python3 .cursor/skills/research-report-workflow/scripts/workflow.py \
  run WORKFLOW_ID
```

查看议题树、大纲或草稿：

```bash
python3 .cursor/skills/research-report-workflow/scripts/workflow.py \
  artifact WORKFLOW_ID outline
```

用户明确确认后继续：

```bash
python3 .cursor/skills/research-report-workflow/scripts/workflow.py \
  confirm WORKFLOW_ID outline_confirmation --comment "用户确认"
```

其他平台只需替换启动脚本前缀，命令行为一致。

## 跨对话恢复

在新对话中输入：

```text
/research-report-workflow
继续工作流 <workflow_id>，先显示当前状态，不要重建任务。
```

Agent调用：

```bash
python3 <skill-dir>/scripts/workflow.py status WORKFLOW_ID
```

聊天记录不会跨软件共享，但SQLite状态、不可变产物、确认和修改记录会保留。不要删除
`.research-workflow/`，也不要在恢复时更换仓库副本。

## 环境与边界

- 需要Python 3.11+、本地文件和Shell权限；纯网页聊天无法执行。
- Markdown/HTML基础路径不要求第三方依赖；Word/PPTX运行Skill内`setup.sh`安装Office依赖。
- 默认离线实现不会自行联网。Agent必须用其获授权的研究工具准备来源，或接入SourceRetriever。
- API Key、Cookie、飞书Token不得写入配置或Skill。
- 各Agent模型表现可能不同，但DAG、确认、状态恢复和质量门由确定性代码保证。
