# Fit Matrix & Weighted Comparison Templates

## A. Requirements → Capability Fit Matrix

Maps the decision's requirements to evidence. `Status`: Met / Partial / Unmet / Unknown.

| Requirement (from decision-framing) | Priority | Status | Evidence | Tier | Confidence |
|---|---|---|---|---|---|
| <hard requirement 1> | P0 | | | | |
| <hard requirement 2> | P0 | | | | |
| <nice-to-have 1> | P1 | | | | |

## B. Weighted Comparison Table

Rows = candidates/tiers (include the incumbent / status quo). Columns = weighted
criteria from decision-framing. Cell = `finding [tier][conf] (date/ver)` and, for
scoring, a 1–5 rating. Never leave blank; use `unknown [—]`.

Cell example: `128k ctx [B][Confirmed] (2026-06) — rating 4`.

| Criterion (weight) | Model A | Model B | Incumbent / Status quo |
|---|---|---|---|
| Capability fit (35%) | | | |
| Cost per successful task (20%) | | | |
| Reliability / ops (15%) | | | |
| Risk / compliance (15%) | | | |
| Integration effort (10%) | | | |
| Support / roadmap (5%) | | | |
| **Weighted total** | | | |

> Show the rating inputs, not just the total. Add a note on how sensitive the
> ranking is to the weights. Treat the score as a decision aid, not truth.

## C. Detailed evidence table (optional, for the technical appendix)

| Dimension | Model A | Model B | Notes / caveats |
|---|---|---|---|
| Independent benchmark | | | |
| Vendor-reported benchmark ⚠ | | | |
| First-hand test result [A] | | | |
| Context window | | | |
| Latency p50/p95 | | | |
| Rate limits | | | |
| Data handling / training-on-your-data | | | |
| License / output IP | | | |
| Deprecation policy | | | |
| Known failure modes | | | |
