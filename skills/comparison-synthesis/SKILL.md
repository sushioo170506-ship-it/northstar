---
name: comparison-synthesis
description: >-
  Integrates verified claims and first-hand test results into a structured
  comparison (model × dimension) plus a narrative analysis, keeping facts
  separate from inference and carrying credibility/date annotations. Use after
  verification (and optional probing) and before report authoring, whenever
  scattered findings must become a coherent, comparable picture — especially for
  multi-model selection. Produces a filled comparison table and the analysis
  that supports the recommendation.
---

# Comparison Synthesis

Assemble the pieces into a structured, comparable picture. This is where
fragments become insight.

## Inputs
- Verified claims (Confirmed/Disputed/Unconfirmed) from `cross-verification`.
- First-hand measurements from `hands-on-probing` (if run).
- Evaluation dimensions from `research-scoping`.

## Steps

1. **Build the comparison table**: rows = candidate models (or the single model
   vs. its alternatives/baselines), columns = the evaluation dimensions. See the
   `comparison-table.md` template in `research-report-authoring`.
2. **Fill each cell with a finding + annotation**: value, credibility tier
   (A–D), confidence (Confirmed/Disputed/Unconfirmed), and date/version.
   Empty cells become explicit "unknown" entries — never leave them blank and
   ambiguous.
3. **Separate fact from inference.** Present verifiable findings first; clearly
   mark your analysis/interpretation as such (e.g., "Fact:" vs "Assessment:").
4. **Analyze trade-offs.** Highlight where candidates differ, where one wins,
   and where the choice depends on the user's priorities/weights.
5. **Tie back to the decision.** Map findings onto the P0 questions from scoping
   so the synthesis directly informs the recommendation.
6. **Carry forward unknowns and disputes** so the report can state them.

## Output (hand to `research-report-authoring`)
- A filled, annotated comparison table.
- A narrative analysis of trade-offs, keyed to the decision.
- The consolidated known-unknowns / disputed list.

## Quality checks
- Every cell is comparable across candidates and annotated.
- Fact and inference are visually distinct.
- The analysis clearly points toward (but does not yet state) a recommendation.
