---
name: hands-on-probing
description: >-
  Runs small, targeted first-hand tests against an external model via its API or
  open weights to verify vendor claims and break the black box. Use when the
  model is reachable and key claims are vendor-only, disputed, or decision-
  critical — especially after cross-verification flags them. Produces first-hand
  measurements, which are the highest-credibility evidence in the report.
  Optional: skip when no API/weights access exists, and note that limitation.
---

# Hands-on Probing

When you can actually call the model, do it. A small, well-designed first-hand
test outweighs any vendor benchmark and directly attacks benchmark
contamination and cherry-picking.

## Preconditions & safety
- Only proceed if you have legitimate access (API key, open weights, sanctioned
  account) and doing so respects the provider's terms.
- Never send secrets or sensitive/proprietary data to a third-party model
  during probing. Use synthetic or non-sensitive inputs.
- Keep tests small and cheap; respect rate limits and budget.

## Inputs
- The prioritized "should test first-hand" list from `cross-verification`.
- The evaluation dimensions from `research-scoping`.

## Steps

1. **Pick what to test.** Focus on claims that are (a) decision-critical and
   (b) only vendor-supported or disputed. Don't re-test what independents
   already confirmed.
2. **Design a minimal protocol.** Define inputs that mirror the user's real
   scenarios, the metric, and how many trials. Fix parameters (temperature,
   version, seed if available) so results are reproducible.
3. **Record the environment.** Model version/endpoint, date, parameters — so the
   result is stamped and repeatable.
4. **Run and capture raw results**, including failures and edge cases (probe
   where it breaks, not just where it works).
5. **Compare to the claim.** State whether the first-hand result supports,
   contradicts, or nuances the vendor/third-party claim.

## Output (hand to `comparison-synthesis`)
- First-hand measurements tagged Tier A, each with protocol + environment +
  date so they are reproducible.
- Any claims now upgraded/downgraded based on testing.

## Quality checks
- Tests map to real user scenarios, not toy cases.
- Parameters and version are recorded for reproducibility.
- No sensitive data was exposed to the external model.
