---
name: failure-mode-analysis
description: >-
  Systematically characterizes HOW and WHERE an external model fails, rather than
  only where it succeeds — covering reward-hacking / specification gaming,
  hallucination and fabrication, unsafe or out-of-intent agentic actions,
  prompt-injection susceptibility, long-horizon drift, and capability boundaries.
  Use in the deep-analysis phase for any decision involving autonomy, reliability,
  or safety. Produces a prioritized failure-mode catalog with triggers,
  likelihood/impact, evidence, and mitigations — turning honest negative findings
  into decision value.
---

# Failure-Mode Analysis

The most decision-relevant findings are often negative. A report that only lists
strengths is incomplete and misleading. Map the failure surface deliberately.

## Inputs
- Verified claims, system/model card disclosures, independent evaluations, and
  any first-hand transcripts from `hands-on-probing`.

## Failure categories to probe (keep those relevant to the decision)
- **Reward-hacking / specification gaming** — exploiting eval bugs, gaming
  metrics, taking shortcuts that inflate scores but not real success. (Critically
  undermines benchmark trust — see the GPT-5.6/METR pattern.)
- **Hallucination / fabrication** — confident wrong answers, invented sources or
  results; calibration of stated confidence.
- **Unsafe or out-of-intent agentic behavior** — acting beyond instructions,
  touching unrelated files, running unrequested commands, over-autonomy.
- **Prompt injection / jailbreak susceptibility** — especially for tool-using or
  RAG deployments.
- **Long-horizon degradation** — drift, context loss, or looping over extended tasks.
- **Robustness** — sensitivity to phrasing, format, adversarial inputs, distribution shift.
- **Capability boundaries** — where competence sharply drops; refusal/over-refusal patterns.

## Steps
1. **Harvest known failures** from the model/system card and independent evals
   (these are high-credibility, often under-reported by vendors).
2. **Probe deliberately** (with `hands-on-probing`) for the categories most tied
   to the decision — e.g., autonomy safety for agentic use.
3. For each failure mode, record: **trigger/conditions, likelihood, impact,
   evidence + credibility, and mitigation** (guardrails, human-in-the-loop,
   constrained scaffolding, config).
4. **Assess the impact on benchmark trust** — if reward-hacking is present, flag
   that reported scores need independent/first-hand corroboration.
5. **Rate residual risk** after mitigations.

## Output (feeds `risk-compliance-review`, `comparison-synthesis`, `research-report-authoring`)
- Prioritized failure-mode catalog (trigger · likelihood · impact · evidence · mitigation · residual).
- A statement on how failure modes affect the reliability of reported metrics.

## Quality checks
- Negative findings are surfaced, not buried.
- Each failure mode has evidence and a concrete mitigation.
- Autonomy/safety-relevant failures are prioritized for agentic use cases.
