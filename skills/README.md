# External Model Research — Agent Skill Suite

A set of composable [Agent Skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills)
that let an AI agent produce a **decision-grade research report** about an
**external / third-party model** (one it does not own), driven by second-hand
information plus rigorous first-hand testing.

Each skill is a folder with a `SKILL.md` (YAML frontmatter `name` + `description`,
then instructions). The agent reads the `description`s to decide when to invoke a
skill; the orchestrator chains them into a workflow.

## What "decision-grade" means

Report value = **defensible, reproducible evidence that de-risks and accelerates
a specific decision.** A link-aggregation summary is a failure. Every report must
answer four questions with evidence:

1. **Can it do the job?** (capability, fit, first-hand proof, failure modes)
2. **Cost & operability?** (TCO, production readiness)
3. **What could go wrong?** (technical, business, compliance risk)
4. **Should we, vs alternatives — and how do we know?** (positioning,
   recommendation, evidence quality)

The bar is codified in
[`research-report-authoring/references/report-quality-checklist.md`](research-report-authoring/references/report-quality-checklist.md).

## Architecture

```
external-model-research   ← orchestrator: enforces the quality bar, chains phases
│
├─ Phase A — Frame the decision
│   └─ decision-framing            decision · workload profile · weighted criteria · fit matrix
│
├─ Phase B — Trustworthy evidence base
│   ├─ evidence-sourcing           tiered sourcing + provenance (source/date/version)
│   ├─ source-credibility-grading  grade A–D · flag COI / cherry-pick / staleness
│   └─ cross-verification          corroborate ≥2 sources → confirm / dispute / unknown
│
├─ Phase C — Deep analysis (the value core)
│   ├─ capability-profiling        capability shape · benchmark literacy · domain fit · examples
│   ├─ hands-on-probing            rigorous, reproducible first-hand testing
│   ├─ failure-mode-analysis       reward-hacking · hallucination · over-autonomy · boundaries
│   ├─ cost-tco-modeling           real token economics · cost-per-successful-task · scale
│   ├─ operational-readiness       latency · limits · availability · versioning · vendor stability
│   └─ risk-compliance-review      safety · security · legal/IP · privacy · lock-in · regulatory
│
└─ Phase D — Synthesize & deliver
    ├─ competitive-positioning     trade-off frontier vs alternatives · when-to-choose-which
    ├─ comparison-synthesis        weighted fit scoring + annotated comparison table
    └─ research-report-authoring   layered report + conditional recommendation + pilot plan + expiry
```

Start the agent with **`external-model-research`**; it sequences and delegates to
the rest and iterates as findings demand. Sub-skills are also usable standalone.

## Design principles baked into every skill

1. Everything is a claim with a source or a first-hand test — no orphan claims.
2. Separate **Fact** (verifiable) from **Assessment** (inference).
3. Name the unknowns — a documented gap is a finding.
4. Distrust vendor benchmarks (cherry-picking, contamination).
5. Stamp every claim with model version + date.
6. Prefer depth over coverage: rigorous on P0 beats shallow on everything.

## Shared assets (under `research-report-authoring/`)
- `templates/report-template.md` — the 14-section decision-grade report skeleton.
- `templates/comparison-table.md` — fit matrix + weighted comparison.
- `templates/tco-model.md` — cost/TCO scenario model.
- `references/credibility-rubric.md` — A–D tiers + confidence labels.
- `references/report-quality-checklist.md` — the definition of done.

## Skills index

| Skill | Phase | Output |
|---|---|---|
| `external-model-research` | orchestrator | the finished decision-grade report |
| `decision-framing` | A | decision · workload · weighted criteria · fit matrix |
| `evidence-sourcing` | B | provenance-stamped evidence pool |
| `source-credibility-grading` | B | graded evidence base |
| `cross-verification` | B | confirmed/disputed claims + unknowns |
| `capability-profiling` | C | capability profile + benchmark decode |
| `hands-on-probing` | C | first-hand measurements (tier A) + transcripts |
| `failure-mode-analysis` | C | prioritized failure-mode catalog |
| `cost-tco-modeling` | C | TCO model + cost-per-successful-task |
| `operational-readiness` | C | production-readiness assessment |
| `risk-compliance-review` | C | risk register + due-diligence questions |
| `competitive-positioning` | D | trade-off frontier + when-to-choose guidance |
| `comparison-synthesis` | D | scored fit matrix + comparison table |
| `research-report-authoring` | D | delivered report |
