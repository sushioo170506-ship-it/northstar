# Agent platform locations

The same Skill bundle is copied to these project-local paths:

| Platform | Path | Explicit invocation |
|---|---|---|
| Cursor | `.cursor/skills/research-report-workflow/` | `/research-report-workflow` |
| Claude Code | `.claude/skills/research-report-workflow/` | `/research-report-workflow` |
| Codex | `.agents/skills/research-report-workflow/` | `$research-report-workflow` |
| Trae | `.trae/skills/research-report-workflow/` | select with `/` |
| Qoder | `.qoder/skills/research-report-workflow/` | `/research-report-workflow` |
| WorkBuddy | `.codebuddy/skills/research-report-workflow/` | select/import Skill |

Restart or reload the agent after first installation if it does not discover the
Skill. Launch the agent in this repository or a child directory. The Skill needs
local file and shell access; a web-only chat without a local execution
environment cannot run the persistent workflow.

To refresh every checked-in adapter after editing the canonical bundle:

```bash
python3 scripts/sync_agent_skill.py
```

The canonical source is:

```text
agent-skills/research-report-workflow/
```

Do not edit generated platform copies directly.
