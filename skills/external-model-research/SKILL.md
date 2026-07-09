---
name: external-model-research
description: >-
  Orchestrates an end-to-end research report about an EXTERNAL / third-party
  model (LLM APIs, open-weight models, or vendor/commercial models) that the
  agent does NOT own and can only study through public/second-hand information
  plus optional black-box testing. Use this whenever the user asks to
  "research", "survey", "evaluate", "compare", "do due diligence on", or "write
  a report about" one or more models they did not build themselves — especially
  for adoption/selection, competitive analysis, or compliance decisions. This
  skill sequences and delegates to the sub-skills research-scoping,
  layered-sourcing, source-credibility-grading, cross-verification,
  hands-on-probing, comparison-synthesis, and research-report-authoring to
  deliver a finished, decision-ready report.
---

# External Model Research (Orchestrator)

You are producing a research report about a model you do **not** own. Your job
is not to document what *you* built, but to **gather external information,
judge how trustworthy it is, verify it where possible, and synthesize it into a
decision-ready deliverable**. Treat every claim as second-hand until proven
otherwise.

## When to use this skill

Trigger on requests like:
- "Research / survey / evaluate model X."
- "Compare model X vs Y vs Z for <use case>."
- "Should we adopt X? Do due diligence."
- "Write a competitive analysis / vendor report on X."

If the user instead wants to document a model **they trained themselves**, this
skill does not apply — that is internal model-card work.

## Core principles (apply throughout)

1. **Everything is a claim with a source.** No conclusion may appear in the
   final report without an attributable source or a first-hand test.
2. **Separate fact from inference.** Mark what is verifiable vs. your analysis.
3. **Name the unknowns.** "We could not find X" is a valid, valuable finding.
4. **Distrust the vendor's own benchmarks.** Watch for cherry-picking and
   benchmark contamination; prefer independent evals and your own tests.
5. **Stamp everything with a date and model version.** External models change
   fast; an unstamped claim is worthless.

## Workflow (delegate to sub-skills in order)

Run these stages. Each maps to a dedicated sub-skill — invoke that skill for the
detailed procedure, then carry its output to the next stage.

1. **Scope** → `research-scoping`
   Turn the vague goal into a prioritized question list, target audience, and
   the decision the report must support. Output: question list + evaluation
   dimensions.

2. **Source** → `layered-sourcing`
   Systematically collect information in tiers (first-party authoritative →
   independent third-party → community/rumor → vendor marketing). Output: an
   evidence pool where every item has a URL and a capture date.

3. **Grade** → `source-credibility-grading`
   Assign each piece of evidence a credibility tier and flag conflicts of
   interest. Output: a graded evidence base.

4. **Verify** → `cross-verification`
   Corroborate key claims across ≥2 independent sources; surface contradictions
   and open questions. Output: verified claims + a "disputed / unknown" list.

5. **Probe (optional but high-value)** → `hands-on-probing`
   If an API or open weights are reachable, run small first-hand tests on the
   scenarios the user cares about to break the black box. Output: first-hand
   measurements (highest-credibility evidence).

6. **Synthesize** → `comparison-synthesis`
   Integrate everything into a structured comparison (model × dimension) and
   analysis. Output: filled comparison table + narrative analysis.

7. **Author & recommend** → `research-report-authoring`
   Produce the final layered report: executive summary + detailed findings +
   explicit recommendation with preconditions + credibility/date annotations +
   a review/expiry date. Output: the delivered report.

## Adapting the workflow

- **Single quick lookup:** you may compress stages 2–4, but never skip source
  attribution or the date stamp.
- **No API/weights access:** skip stage 5, but explicitly note in the report
  that all conclusions are second-hand and unverified by first-hand testing.
- **Multi-model comparison:** run stages 2–5 per model, then a single stage 6/7
  across all of them.

## Definition of done

The report is complete only when:
- [ ] Every key claim is attributed and credibility-graded.
- [ ] Facts are separated from your inferences.
- [ ] Known unknowns are listed explicitly.
- [ ] Any vendor-supplied numbers are flagged as such.
- [ ] There is a clear, conditional recommendation.
- [ ] The report carries an "information current as of <date>" stamp and a
      recommended re-check date.
- [ ] Output language matches the user's request.
