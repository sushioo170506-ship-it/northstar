---
name: research-report-authoring
description: >-
  Produces the final, decision-ready external-model research report: a layered
  document with an executive summary, detailed annotated findings, an explicit
  conditional recommendation, credibility/date stamps, known unknowns, and a
  re-check date. Use as the LAST stage of external model research, after
  synthesis, to turn analysis into the delivered artifact. Bundles a report
  template, a comparison-table template, and a credibility rubric.
---

# Research Report Authoring

Turn the synthesized analysis into a polished deliverable tailored to the
audience and decision defined during scoping.

## Inputs
- The comparison table + analysis from `comparison-synthesis`.
- Audience + decision + question list from `research-scoping`.

## Bundled assets
- `templates/report-template.md` — the report skeleton. Start from this.
- `templates/comparison-table.md` — the model × dimension table format.
- `references/credibility-rubric.md` — the A–D credibility tiers and confidence
  labels, for consistent annotation and a legend in the report.

## Steps

1. **Copy the report template** and fill it in.
2. **Write two layers:**
   - **Executive summary** (for decision-makers): the recommendation, top 3–5
     findings, and the main risks/unknowns — jargon-light.
   - **Detailed findings** (for technical readers): the full comparison table
     and per-dimension analysis with annotations.
3. **Make the recommendation explicit and conditional.** State what to do, under
   what assumptions/preconditions, and what would change the recommendation.
4. **Annotate every key claim** with credibility tier + confidence + date/version
   using the rubric; include the legend so readers can interpret it.
5. **List known unknowns** in their own section — do not bury them.
6. **Flag vendor-supplied numbers** wherever they appear.
7. **Stamp the report**: "Information current as of <date>" and a recommended
   **re-check / expiry date** (external models change fast).
8. **Match the output language** to the user's request.

## Definition of done (final gate)
- [ ] Executive summary + detailed findings both present.
- [ ] Clear, conditional recommendation with preconditions.
- [ ] Every key claim attributed and credibility-graded.
- [ ] Facts separated from inference.
- [ ] Known unknowns listed explicitly.
- [ ] Vendor claims flagged.
- [ ] Date stamp + re-check date included.
- [ ] Comparison table complete (no silent blanks).
