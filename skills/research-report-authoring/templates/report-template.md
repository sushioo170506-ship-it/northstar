# External Model Research Report: <Model / Comparison Name>

- **Prepared for (audience):** <engineers / leadership / legal>
- **Decision this supports:** <adopt vs not / A vs B vs status quo / compliance>
- **Recommendation (one line):** <what to do> — conditional on <preconditions>
- **Author:** <name>
- **Information current as of:** <YYYY-MM-DD> · **Re-check by:** <YYYY-MM-DD>
- **Models & versions in scope:** <model @ version, ...>

> Credibility — A: verified independent / first-hand · B: first-party factual ·
> C: vendor/marketing claim · D: community/anecdotal.
> Confidence — Confirmed (≥2 independent) · Disputed · Unconfirmed (single source).
> ⚠ = vendor-supplied — discount and verify.

---

## 1. Executive Summary (for decision-makers)
- **Recommendation & rationale:** <what to do, why> — **conditional on** <preconditions>.
- **This changes if:** <what would flip it> (see Watch-list, §12).
- **Weighted verdict:** <score/ranking + the 1–2 factors that drove it>.
- **Top findings:** 1) … `[tier][conf]` 2) … 3) …
- **Top risks / unknowns:** <the few that matter most>.
- **Pilot plan (next step):** <what to test, success metric, guardrails>.

## 2. Decision Frame & Method
- Decision, options, and "good enough" bar.
- Workload/use-case profile evaluated against.
- Weighted criteria (sum to 100%).
- **Methodology:** what was researched and **first-hand tested**, and what was
  **not** (scope of confidence / reproducibility).

## 3. Requirements → Capability Fit Matrix
<insert fit matrix from comparison-table.md: requirement · met/partial/unmet · evidence · confidence>

## 4. Capability Profile (not just scores)
- Strengths / weaknesses / unproven, mapped to our workload.
- **Benchmark decode:** what each cited benchmark measures, relevance, self- vs
  independent scores, contamination/config caveats. `[tier][conf][date]`
- Representative qualitative examples (good and bad).

## 5. First-hand Test Results
- Protocol (tasks, metric, n, params/version), environment, raw results,
  transcripts, and how they confirm/contradict prior claims. `[A]`
- *(If no access: state that explicitly and mark all performance claims second-hand.)*

## 6. Failure Modes & Boundaries
- Catalog: failure mode · trigger · likelihood · impact · evidence · mitigation · residual.
- Impact on benchmark trust (e.g., reward-hacking → scores need corroboration).

## 7. Cost & TCO
<insert tco-model.md: per-task, monthly-at-scale, cost-per-successful-task, scenarios, assumptions>

## 8. Operational Readiness
- Latency (p50/p95), throughput, rate limits, availability/regions, data
  residency, SLA, versioning/deprecation, access/onboarding, support, vendor
  stability. Ready / caveated / blocker per dimension; hard blockers called out.

## 9. Risk & Compliance Register
- Risk · evidence · likelihood · impact · mitigation · residual. Showstoppers flagged.
- Data-use/training terms and output IP explicitly addressed.

## 10. Competitive Positioning
- Trade-off frontier vs alternatives (incl. status quo).
- "Choose this when … / choose <alternative> when …".

## 11. Weighted Comparison
<insert weighted comparison table; show inputs and weight-sensitivity note>

## 12. Known Unknowns, Disputes & Watch-list
- **Unknowns:** important things no source answered.
- **Disputed:** claim — side 1 vs side 2 — which is more credible & why.
- **Watch-list:** signals that would change the recommendation (new independent
  evals, GA, price/version changes, roadmap moves).

## 13. Recommendation & Next Steps
- Decision-ready, conditional recommendation; pilot plan with success metrics and
  guardrails; vendor due-diligence questions to resolve open items.

## 14. Sources
- Numbered: title — author/org — URL — tier — date accessed.
