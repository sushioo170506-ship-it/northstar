# Credibility & Confidence Rubric

Shared vocabulary for grading evidence and annotating claims across the
external-model-research skill suite. Use these exact labels for consistency.

## Credibility tiers (source trust)

| Tier | Meaning | Examples | How to treat |
|---|---|---|---|
| **A** | Verified independent / first-hand | Independent benchmark, audit, academic reproduction, **your own hands-on test** | Highest trust |
| **B** | First-party factual | Official docs, spec sheet, pricing page, license, changelog | Reliable for *stated* facts & policies |
| **C** | First-party performance / marketing | Vendor-reported benchmarks, launch blog, sales deck | Interested party — discount, verify before use |
| **D** | Community / anecdotal | Forums, social posts, personal blogs | Leads only — verify before relying |

## Confidence levels (verification status)

| Label | Meaning |
|---|---|
| **Confirmed** | Corroborated by ≥2 genuinely independent sources (or a first-hand test) |
| **Disputed** | Credible sources disagree; both sides recorded |
| **Unconfirmed** | Single source only; report with low confidence |

## Flags to raise on evidence

- **⚠ COI** — conflict of interest (who benefits if this is believed?).
- **⚠ Cherry-pick** — selective/favorable-only baselines or benchmarks.
- **⚠ Contamination** — public benchmark the model may have trained on.
- **⚠ Stale** — date/version behind the current release.

## Golden rules

1. No conclusion without a source or a first-hand test.
2. Separate **Fact** (verifiable) from **Assessment** (your inference).
3. Name the unknowns — a documented gap is a finding.
4. Never accept a vendor performance number at face value.
5. Stamp every claim with a date and model version.
