---
name: research-report-workflow
description: Run, resume, review, revise, and export the local Northstar research-report workflow. Use when the user asks to test or generate a research report, inspect an issue tree or outline, continue a saved workflow, revise a report, or export Markdown, Word, PPT, HTML, PDF, or Feishu output.
---

# Research Report Workflow

Use the repository's deterministic workflow engine. Do not imitate the workflow
with free-form prose when the local engine is available.

## Locate the launcher

This skill is copied into several agent-specific directories. Set `SKILL_DIR`
to the directory containing this file, then invoke:

```bash
python3 "$SKILL_DIR/scripts/workflow.py" --help
```

The launcher finds the repository root and always uses the repository-local
`.research-workflow` state directory. Never silently switch to another data
directory when resuming an existing workflow.

If optional Office dependencies are missing and the user requests DOCX/PPTX,
run:

```bash
bash "$SKILL_DIR/scripts/setup.sh"
```

## Create a workflow

1. Gather the topic, audience, report type, desired length, output format,
   profile, boundaries, prior judgments, confidentiality, and available
   sources.
2. Never invent sources. If the agent has authorized web/research tools, gather
   sources first and preserve title, original URL, publication time, content,
   category, and issue IDs. Otherwise disclose that the quality gate may block.
3. Write a complete JSON config outside the Skill directory. Follow
   `references/CONFIG.md`.
4. Create the workflow:

```bash
python3 "$SKILL_DIR/scripts/workflow.py" create-config /path/to/config.json
```

Capture and retain the returned `workflow_id`.

## Run and confirm

Run exactly one step sequence at a time:

```bash
python3 "$SKILL_DIR/scripts/workflow.py" run WORKFLOW_ID
```

When `waiting_at` is returned, inspect the corresponding artifact:

| Waiting checkpoint | Artifact to present |
|---|---|
| `issue_tree_confirmation` | `issue_tree` |
| `outline_confirmation` | `outline` |
| `draft_confirmation` | `compose` |
| `pre_review_confirmation` | `formatting` |

```bash
python3 "$SKILL_DIR/scripts/workflow.py" artifact WORKFLOW_ID NODE
```

Present the artifact in readable form and ask the user to confirm or request a
change. Do not confirm on the user's behalf. After explicit confirmation:

```bash
python3 "$SKILL_DIR/scripts/workflow.py" \
  confirm WORKFLOW_ID CHECKPOINT --comment "用户确认"
python3 "$SKILL_DIR/scripts/workflow.py" run WORKFLOW_ID
```

Repeat until completed or blocked.

## Revise or repair

Route natural-language feedback to the earliest affected node:

```bash
python3 "$SKILL_DIR/scripts/workflow.py" \
  revise WORKFLOW_ID "用户的修改意见"
```

For replacement evidence, create `sources.json` with a top-level `sources`
array and run:

```bash
python3 "$SKILL_DIR/scripts/workflow.py" \
  update-sources WORKFLOW_ID sources.json --reason "替换不可追溯来源"
```

After invalidation, run again and respect every newly reopened checkpoint.

If the quality gate rejects publication, inspect:

```bash
python3 "$SKILL_DIR/scripts/workflow.py" \
  artifact WORKFLOW_ID quality_assurance --json
```

Report the concrete failed checks. Fix the earliest responsible node or source;
never bypass or rewrite the gate result.

## Resume in another chat or agent

The chat transcript is not the state store. To resume, the user only needs the
same repository and `workflow_id`:

```bash
python3 "$SKILL_DIR/scripts/workflow.py" status WORKFLOW_ID
```

Continue from the persisted state. Completed nodes must not be rerun.

## Export

Once completed:

```bash
python3 "$SKILL_DIR/scripts/workflow.py" final WORKFLOW_ID
python3 "$SKILL_DIR/scripts/workflow.py" \
  export WORKFLOW_ID /absolute/path/report.docx
```

Return actual file paths for binary or non-previewable outputs. Do not claim a
file or Feishu document exists unless the renderer returned success.

## Safety and quality rules

- Never place model, retrieval, Feishu, or other secrets in config JSON.
- Do not silently lower `deep` or `regulatory` profiles.
- Do not fabricate URLs, citations, benchmark numbers, or source text.
- Preserve the four human confirmation semantics.
- Treat `quality_assurance` as the only release decision.
- Use `references/PLATFORMS.md` when installing or troubleshooting discovery.
