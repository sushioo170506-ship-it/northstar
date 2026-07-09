---
name: decision-framing
description: >-
  Frames an external-model research task around the decision it must serve:
  defines the decision type, a concrete use-case/workload profile, weighted
  evaluation criteria, and a requirements-to-capability fit matrix. Use FIRST in
  any external model research or comparison, before gathering evidence, so every
  downstream finding maps back to "so what for us?". Produces the decision
  contract, weighted criteria, and fit-matrix skeleton that drive sourcing,
  analysis, scoring, and the final recommendation.
---

# Decision Framing

Turn a vague request ("look into model X") into a **decision contract**. This is
the anchor for the whole report: if a finding doesn't serve the decision or a
requirement, it doesn't belong.

## Inputs
- The user's goal, constraints (budget, latency, compliance, deadline), and the
  candidate model(s) or category.

## Steps

1. **Name the decision precisely.** What action does this report drive, and what
   are the options? (Adopt vs not · pick A vs B vs status quo · pass compliance ·
   set a baseline.) Define what "good enough to decide" looks like.

2. **Profile the real workload.** Don't evaluate in the abstract — describe the
   actual use case(s): task types, input/output shapes, volume/QPS, latency
   tolerance, context sizes, languages/domains, autonomy level (assisted vs
   agentic), and data sensitivity. This profile is what capability-profiling and
   hands-on-probing will test against.

3. **Define weighted evaluation criteria.** List the dimensions that matter and
   assign weights reflecting the decision (e.g., capability 35% / cost 20% /
   reliability 15% / risk 15% / integration 10% / support 5%). Weights force
   explicit trade-offs and drive the final weighted score.

4. **Build the requirements→capability fit matrix (skeleton).** For each hard
   requirement and nice-to-have, create a row to be filled later with:
   evidence, met/partial/unmet, and confidence. This is the "so what for us"
   backbone.

5. **State assumptions, constraints, and out-of-scope** explicitly to bound effort.

6. **Set the P0/P1/P2 question list** derived from the criteria — P0 = would
   change the decision; these get the deep-analysis pillars.

## Output (hand to `evidence-sourcing` and Phase C/D)
- Decision statement + options + "good enough" bar.
- Workload/use-case profile.
- Weighted criteria (sum to 100%).
- Requirements→capability fit-matrix skeleton.
- P0/P1/P2 question list; assumptions; out-of-scope.

## Quality checks
- Weights are explicit and justified by the decision.
- The workload profile is concrete enough to design tests against.
- Every P0 question, if answered, could actually flip the decision.
