---
name: cost-tco-modeling
description: >-
  Models the real total cost of ownership of an external model for a specific
  workload — not the sticker per-token price — including cost-per-successful-task,
  reasoning/agentic token amplification, prompt caching and batch discounts,
  effective throughput under rate limits, and hidden or regional fees. Use in the
  deep-analysis phase whenever cost affects the decision. Produces a defensible
  cost model with scenarios and per-unit-of-value economics that feed the
  weighted comparison and recommendation.
---

# Cost & TCO Modeling

Sticker price ($/1M tokens) is not cost. Model what the workload will actually
cost, and express it per unit of value.

## Inputs
- Pricing facts from `evidence-sourcing`; the workload profile (volume, task
  shapes) from `decision-framing`; observed token/latency data from `hands-on-probing`.

## Steps
1. **Gather the full pricing structure**: input/output rates, cache write/read
   rates and minimum cache life, batch discounts, reasoning/thinking-token
   billing, tool-call costs, priority/fast-mode surcharges, regional/data-residency
   uplifts, minimums/commitments.
2. **Estimate tokens per task from the real workload** — prompt + context +
   output + (crucially) hidden reasoning tokens and, for agentic modes, subagent
   fan-out. Use first-hand measurements where available, not guesses.
3. **Compute cost-per-successful-task, not per-token.** Combine token cost with
   the success rate from capability/failure analysis: a cheaper model that fails
   more can cost more per completed job. This is the number that matters.
4. **Model scenarios**: typical vs peak volume; with/without caching; standard vs
   extended-reasoning/`ultra` modes. Show monthly cost at realistic scale.
5. **Account for effective throughput** under rate limits (a low price is moot if
   you can't get the tokens) — coordinate with `operational-readiness`.
6. **Surface hidden/likely-underestimated costs**: retries on failure, long
   context re-sends, eval/monitoring overhead, egress, data-residency uplift.
7. **State assumptions and confidence** for every estimate; flag vendor-only
   pricing terms.

## Output (feeds `comparison-synthesis`, `competitive-positioning`, `research-report-authoring`)
- A cost model: per-task and monthly-at-scale, across scenarios.
- Cost-per-successful-task by model/tier.
- Assumptions, sensitivities, and hidden-cost callouts.

## Quality checks
- Economics are expressed per unit of value, not just per token.
- Reasoning/agentic token amplification and caching are accounted for.
- Every estimate carries its assumptions and confidence.
