---
name: source-credibility-grading
description: >-
  Assigns a credibility tier to each collected piece of evidence and flags
  conflicts of interest, cherry-picking, and staleness. Use after
  layered-sourcing and before cross-verification whenever evidence about an
  external model must be weighted by trustworthiness. Produces a graded evidence
  base so that stronger claims carry more weight in synthesis and the final
  report can annotate confidence.
---

# Source Credibility Grading

Rate how much each piece of evidence can be trusted. This is the core
value-add of external research: distinguishing "officially stated",
"independently verified", and "heard on a forum".

## Inputs
- The evidence pool from `layered-sourcing`.

## Grading rubric

Assign each item a tier (see also `references/credibility-rubric.md` in
`research-report-authoring`):

- **A — Verified independent / first-hand.** Reputable independent test,
  audit, academic reproduction, or your own hands-on measurement.
- **B — First-party factual.** Official docs/specs/pricing/license — reliable
  for *stated* facts and policies (not for self-graded performance).
- **C — First-party performance / marketing claim.** Vendor-reported benchmarks
  and launch claims — interested party, discount heavily, verify before use.
- **D — Community / anecdotal.** Forums, blogs, social posts — treat as leads
  only.

## Steps

1. Tag every evidence item A–D.
2. **Flag conflicts of interest**: who benefits if this claim is believed?
   Mark vendor-authored performance data explicitly.
3. **Flag cherry-picking / contamination risks**: selective baselines,
   favorable-only benchmarks, or public benchmarks the model may have trained on.
4. **Flag staleness**: mark items whose date/version is behind the current one.
5. Downgrade any item that fails these checks and note why.

## Output (hand to `cross-verification`)
- The evidence base, each item carrying: tier (A–D), COI flag, cherry-pick/
  contamination flag, staleness flag.

## Quality checks
- Every item has a tier.
- Vendor performance claims are never left at face value.
- Rationale is recorded for any downgrade.
