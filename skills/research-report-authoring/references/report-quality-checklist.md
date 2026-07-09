# Report Quality Checklist (Definition of Done)

The bar for a **decision-grade** external-model research report. The orchestrator
loads this at the start; the author self-audits against it before delivery. A
report value = defensible, reproducible evidence that de-risks and accelerates a
specific decision.

## The three底线 (any failure = not acceptable)
- [ ] **Decision-grounded** — every section maps to the decision / a requirement
      ("so what for us?"). No orphan facts.
- [ ] **Defensible** — claims are source-graded, cross-verified, Fact separated
      from Assessment, uncertainty stated.
- [ ] **Reproducible** — methodology disclosed; first-hand tests repeatable.

## The four questions are answered with evidence
- [ ] **① Can it do the job?** — capability profile (not a lone score),
      requirements→fit matrix, first-hand proof, failure modes.
- [ ] **② Cost & operability?** — TCO modeled on real workload
      (cost-per-successful-task), production readiness assessed.
- [ ] **③ What could go wrong?** — technical + business + compliance risk register
      with mitigations and residual ratings.
- [ ] **④ Should we, vs alternatives?** — competitive positioning + conditional
      recommendation + evidence quality.

## Element-level checks
- [ ] Decision, options, workload profile, and weighted criteria are explicit.
- [ ] Every benchmark states what it measures, its limits, and self- vs
      independent scores; contamination/config caveats noted.
- [ ] ≥1 first-hand test with documented protocol — or an explicit statement of
      why none and that performance claims are second-hand.
- [ ] Failure modes (reward-hacking, hallucination, over-autonomy, injection,
      drift, boundaries) documented with triggers + mitigations.
- [ ] TCO model present: token estimate, cost-per-successful-task, scale scenarios,
      assumptions; reasoning/agentic amplification and caching accounted for.
- [ ] Operational readiness covered incl. rate limits, availability, and
      versioning/deprecation; hard blockers flagged.
- [ ] Risk register covers data-use/training terms and output IP.
- [ ] Positioning compares alternatives (incl. status quo) on the same weighted axes.
- [ ] Recommendation is conditional and actionable, with a pilot plan + guardrails
      + what-would-flip-it.

## Epistemic & delivery checks
- [ ] Every key claim carries credibility tier + confidence + date + model version.
- [ ] Vendor-supplied numbers are flagged (⚠).
- [ ] Known unknowns and disputed claims have their own section.
- [ ] Weighted score shows its inputs and weight-sensitivity (aid, not truth).
- [ ] Layered: executive summary + deep technical detail; tables/figures used.
- [ ] Temporal validity: "current as of" date, re-check/expiry date, and watch-list.
- [ ] Output language matches the user's request.
