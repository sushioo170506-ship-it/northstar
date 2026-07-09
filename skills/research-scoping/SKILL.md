---
name: research-scoping
description: >-
  Turns a vague model-research goal into a structured, prioritized question list
  plus the target audience and the concrete decision the research must support.
  Use at the START of any external model research or comparison task, before
  collecting information, to prevent aimless gathering. Produces the question
  list and the evaluation dimensions that drive sourcing and the final
  comparison table.
---

# Research Scoping

Convert an ambiguous request ("look into model X") into an explicit research
contract. Do this FIRST; everything downstream inherits from it.

## Inputs
- The user's raw goal and any constraints (budget, deadline, must-have features).
- The model(s) or category in scope.

## Steps

1. **Identify the decision.** Ask/infer: what decision will this report drive?
   (Adopt vs not, pick vendor A vs B, pass compliance, benchmark our own work.)
   The decision determines what "good enough" evidence looks like.

2. **Identify the audience.** Engineers, product/leadership, legal/compliance?
   This sets depth and how much to translate jargon.

3. **Decompose into a prioritized question list.** Convert the goal into
   concrete, answerable questions, each tagged P0/P1/P2. Draw from these common
   dimensions (keep only the relevant ones):
   - **Capability / quality** — task performance, benchmarks, known strengths/weaknesses.
   - **Cost** — pricing model, token/compute cost, rate limits, hidden fees.
   - **Latency / throughput / context window / limits.**
   - **Integration** — API surface, SDKs, deployment options, ecosystem.
   - **Data & privacy** — data handling, retention, training-on-your-data policy.
   - **Licensing & compliance** — license terms, usage restrictions, region/legal.
   - **Reliability / support / roadmap / vendor stability.**
   - **Safety & risk** — known failures, misuse potential, bias issues.

4. **Define the evaluation dimensions** = the columns of the eventual comparison
   table. These should map 1:1 onto the P0/P1 questions.

5. **State out-of-scope explicitly** to bound the effort.

## Output (hand to `layered-sourcing`)
- A prioritized question list (P0/P1/P2).
- Named audience + the target decision.
- The evaluation dimensions / comparison-table columns.
- Explicit out-of-scope list.

## Quality checks
- Every question is concrete and answerable, not "is it good?".
- Dimensions are comparable across candidates (for multi-model tasks).
- Nothing critical to the decision is missing.
