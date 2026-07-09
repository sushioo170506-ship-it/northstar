---
name: capability-profiling
description: >-
  Builds a capability PROFILE of an external model rather than quoting a single
  benchmark number — interpreting what each benchmark actually measures and its
  limits, mapping strengths/weaknesses to the user's real workload, and grounding
  claims in qualitative evidence (transcripts/examples). Use in the deep-analysis
  phase, after the evidence base is verified, whenever a report must say what the
  model can actually do for the specific use case. Produces a per-dimension
  capability profile with benchmark literacy, domain-fit judgments, and
  representative examples.
---

# Capability Profiling

A single score ("88.8%, SOTA") is not analysis. Produce the **shape** of the
model's capability and what it means **for this workload**.

## Inputs
- Verified claims from `cross-verification`; the workload profile and weighted
  criteria from `decision-framing`.

## Steps

1. **Benchmark literacy — decode every score.** For each cited benchmark:
   - What skill does it actually measure, and how (harness, scaffold, metric)?
   - Is it relevant to our workload, or a proxy? Note the gap.
   - Contamination/overfitting risk (public benchmark the model may have trained on)?
   - Self-reported vs independently reproduced? Record the delta if both exist.
   - Config sensitivity (reasoning effort, tools, temperature) that inflates scores.

2. **Map to the workload.** Translate benchmark and claim evidence into
   statements about *our* task types: "strong at X-type tasks; weak/unproven at
   Y." Fill the requirements→capability rows with met/partial/unmet + confidence.

3. **Build the capability shape.** Summarize strengths, weaknesses, and unproven
   areas across the decision's dimensions — not one scalar. Note where capability
   depends on mode/config (e.g., extended reasoning, agentic scaffolding).

4. **Ground in qualitative evidence.** Collect representative examples/transcripts
   (from testing or credible sources) that illustrate the profile — good and bad.
   A concrete example is worth more than a rounded percentage.

5. **Flag what only first-hand testing can settle** and hand those to
   `hands-on-probing`.

## Output (hand to `comparison-synthesis`, feeds `hands-on-probing`)
- Per-dimension capability profile (strength / weakness / unproven) with
  confidence and workload relevance.
- Decoded benchmark table: what it measures, relevance, self-vs-independent, caveats.
- Filled requirements→capability fit rows.
- Representative qualitative examples.
- List of claims needing first-hand verification.

## Quality checks
- No benchmark is reported without stating what it measures and its limits.
- Findings are expressed in terms of the user's workload, not generic prowess.
- Self-reported and independent numbers are distinguished.
