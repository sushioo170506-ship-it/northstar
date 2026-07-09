# External Model Research — Agent Skill Suite

A set of composable [Agent Skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills)
that let an AI agent research an **external / third-party model** (one it does
not own) and **deliver a decision-ready report** — driven by second-hand
information plus optional black-box testing.

Each skill is a folder with a `SKILL.md` (YAML frontmatter `name` + `description`,
then instructions). The agent reads the `description`s to decide when to invoke
a skill, and the orchestrator chains them into a workflow.

## How the skills compose

```
external-model-research   ← orchestrator: chains the stages below
        │
        ├─ 1. research-scoping           goal → prioritized questions + dimensions
        ├─ 2. layered-sourcing           tiered info gathering (+ source & date)
        ├─ 3. source-credibility-grading grade each source A–D, flag COI/staleness
        ├─ 4. cross-verification         corroborate ≥2 sources; confirm/dispute
        ├─ 5. hands-on-probing           optional first-hand API/weights testing
        ├─ 6. comparison-synthesis       model × dimension table + trade-off analysis
        └─ 7. research-report-authoring  layered report + recommendation + stamps
```

Start the agent with **`external-model-research`**; it sequences and delegates to
the rest. The sub-skills are also usable standalone.

## Design principles baked into every skill

1. **Everything is a claim with a source** — no conclusion without attribution
   or a first-hand test.
2. **Separate fact from inference.**
3. **Name the unknowns** — a documented gap is a finding.
4. **Distrust vendor benchmarks** — watch for cherry-picking and contamination.
5. **Stamp date + model version** — external models change fast.

## Shared assets

Under `research-report-authoring/`:
- `templates/report-template.md` — the report skeleton.
- `templates/comparison-table.md` — the model × dimension table.
- `references/credibility-rubric.md` — the A–D tiers + confidence labels used
  consistently across all skills.

## Skills index

| Skill | Stage | Output |
|---|---|---|
| `external-model-research` | orchestrator | the finished report |
| `research-scoping` | 1. scope | question list + dimensions |
| `layered-sourcing` | 2. source | evidence pool w/ provenance |
| `source-credibility-grading` | 3. grade | graded evidence base |
| `cross-verification` | 4. verify | confirmed/disputed claims + unknowns |
| `hands-on-probing` | 5. probe | first-hand measurements (tier A) |
| `comparison-synthesis` | 6. synthesize | comparison table + analysis |
| `research-report-authoring` | 7. author | delivered report |
