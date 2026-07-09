---
name: cross-verification
description: >-
  Corroborates key claims across two or more independent sources, surfaces
  contradictions, and separates confirmed facts from disputed or unknown items.
  Use after source-credibility-grading and before synthesis, whenever a research
  conclusion about an external model needs to be trustworthy. Produces a set of
  verified claims plus an explicit disputed/unknown list.
---

# Cross-Verification

Turn graded evidence into trustworthy conclusions by checking whether
independent sources agree. A claim confirmed by two independent parties is far
stronger than one repeated by the same interested source.

## Inputs
- The graded evidence base from `source-credibility-grading`.

## Steps

1. **Group evidence by claim** (or by question/dimension).
2. **Check independence.** Two sources that both trace back to the vendor's
   press release are NOT independent. Require genuinely separate origins.
3. **Corroborate P0/P1 claims across ≥2 independent sources** where possible.
   - Agreement → mark **Confirmed** (raise confidence).
   - Disagreement → mark **Disputed**; record each side and which is more
     credible and why.
   - Single-source only → mark **Unconfirmed** (note it needs first-hand testing
     or should be reported with low confidence).
4. **Prioritize claims to probe.** Flag high-impact Confirmed-but-vendor-only or
   Disputed claims as candidates for `hands-on-probing`.
5. **Compile known unknowns.** Anything important that no source answers.

## Output (hand to the Phase C deep-analysis skills, esp. `capability-profiling` and `hands-on-probing`)
- Verified claims tagged Confirmed / Disputed / Unconfirmed with confidence.
- A prioritized "should test first-hand" list.
- An explicit known-unknowns list.

## Quality checks
- "Independent" really means independent origins, not echoes.
- Disputed items retain both sides, not a silent pick.
- Confidence levels are assigned consistently.
