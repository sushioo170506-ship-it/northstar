---
name: external-model-research
description: >-
  Orchestrates an in-depth, decision-grade research report about an EXTERNAL /
  third-party model (LLM APIs, open-weight models, or vendor/commercial models)
  the agent does NOT own and can only study through public/second-hand
  information plus first-hand black-box testing. Use whenever the user asks to
  "research", "survey", "evaluate", "deep-dive", "compare", "do due diligence
  on", or "write a report about" one or more models they did not build — for
  adoption/selection, competitive analysis, or compliance decisions. Enforces a
  quality bar (see references/report-quality-checklist.md) and sequences the
  sub-skills: decision-framing, evidence-sourcing, source-credibility-grading,
  cross-verification, capability-profiling, hands-on-probing,
  failure-mode-analysis, cost-tco-modeling, operational-readiness,
  risk-compliance-review, competitive-positioning, comparison-synthesis, and
  research-report-authoring.
---

# External Model Research (Orchestrator)

You are producing a **decision-grade** report about a model you do **not** own.
The value of the report = using **defensible, reproducible evidence** to
**de-risk and accelerate a specific decision**. A link-aggregation summary is a
failure; a report that changes what the reader does — with justification — is
the goal.

## When to use

Trigger on "research / evaluate / deep-dive / compare / due-diligence / write a
report on" one or more models the user did not build. If the user wants to
document a model **they trained**, this does not apply (that is model-card work).

## The quality bar (non-negotiable)

A report is only acceptable if it answers, with evidence, four questions:

1. **Can it do the job?** — capability profile, requirement fit, first-hand
   proof, failure modes.
2. **What will it really cost and can we operate it?** — TCO, production
   readiness.
3. **What could go wrong?** — technical, business, and compliance risk.
4. **Should we, vs. the alternatives — and how do we know?** — positioning,
   conditional recommendation, evidence quality.

Three底线 apply to every section:
- **Decision-grounded** — every finding maps back to the decision ("so what for
  us?"). No orphan facts.
- **Defensible** — source-graded, cross-verified, fact separated from inference,
  uncertainty stated.
- **Reproducible** — methodology disclosed; first-hand tests repeatable.

Load `research-report-authoring/references/report-quality-checklist.md` at the
start and treat it as the definition of done.

## Core principles

1. Everything is a claim with a source or a first-hand test — no orphan claims.
2. Separate **Fact** (verifiable) from **Assessment** (your inference).
3. Name the unknowns — a documented gap is a finding.
4. Distrust vendor benchmarks (cherry-picking, contamination); prefer
   independent evals and your own tests.
5. Stamp every claim with model version + date; models change fast.
6. Prefer depth over coverage: a rigorous answer on the P0 questions beats a
   shallow pass over everything.

## Workflow

Run in phases. Each stage delegates to a dedicated sub-skill; carry outputs
forward. Iterate — later findings often send you back to source or test more.

### Phase A — Frame the decision
1. **`decision-framing`** → the decision, use-case profile, weighted criteria,
   and a requirements→capability fit matrix. Everything downstream inherits this.

### Phase B — Build a trustworthy evidence base
2. **`evidence-sourcing`** → tiered evidence pool with provenance (source + date + version).
3. **`source-credibility-grading`** → grade A–D; flag COI / cherry-pick / staleness.
4. **`cross-verification`** → confirm / dispute / unknown across independent sources.

### Phase C — Deep analysis (the value core — do NOT skip on P0 dimensions)
5. **`capability-profiling`** → capability shape, benchmark literacy, domain-fit, qualitative evidence.
6. **`hands-on-probing`** → rigorous first-hand testing on representative tasks (if reachable).
7. **`failure-mode-analysis`** → adversarial behavior, reward-hacking, hallucination, boundaries.
8. **`cost-tco-modeling`** → realistic token economics, cost-per-successful-task, cost at scale.
9. **`operational-readiness`** → latency/throughput/limits/availability/versioning/SLA/vendor stability.
10. **`risk-compliance-review`** → safety/security/legal/IP/privacy/lock-in/regulatory + mitigations.

### Phase D — Synthesize & deliver
11. **`competitive-positioning`** → trade-off frontier vs alternatives; when-to-choose-which.
12. **`comparison-synthesis`** → weighted fit scoring + integrated comparison table.
13. **`research-report-authoring`** → layered report + conditional recommendation + pilot plan + expiry.

## Adapting scope
- **Quick lookup:** compress Phase B–C, but never drop source attribution, date
  stamps, or the fact/inference split.
- **No API/weights access:** skip stage 6; explicitly flag that all performance
  claims are second-hand and unverified by first-hand testing.
- **Multi-model comparison:** run Phase C per model, then a single Phase D across all.
- **Prioritize by P0:** invest the deep-analysis pillars where the decision is
  most sensitive; go lighter on P2 dimensions.

## Definition of done
Passes every item in `report-quality-checklist.md`, including: four questions
answered; recommendation is conditional with a pilot plan; ≥1 first-hand test or
an explicit note of why none; failure modes and known unknowns documented;
vendor numbers flagged; TCO modeled on realistic load; every key claim graded
and dated; output language matches the user's request.
