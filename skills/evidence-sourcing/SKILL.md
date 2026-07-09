---
name: evidence-sourcing
description: >-
  Systematically collects evidence about an external model in credibility tiers
  — first-party authoritative, independent third-party, community/practitioner,
  and vendor marketing — recording source, capture date, and model version for
  every item, and prioritizing primary documents (system/model cards, papers,
  docs, pricing, changelogs) plus independent evaluations. Use after
  decision-framing and before grading/analysis whenever gathering information on
  a model the agent does not own. Produces a structured, provenance-stamped
  evidence pool and an explicit list of information gaps.
---

# Evidence Sourcing

Gather evidence deliberately, tier by tier, always capturing provenance. Aim for
primary sources and independent evaluations over aggregator summaries.

## Inputs
- The decision contract, weighted criteria, and P0/P1 questions from `decision-framing`.

## Source tiers (search top-down; prefer higher tiers)
1. **First-party authoritative** — model/system card, technical report, paper,
   docs, pricing page, changelog, license, deprecation policy. Best for *stated*
   specs/policies; treat performance claims skeptically.
2. **Independent third-party** — public leaderboards, independent benchmarks,
   academic reproductions, red-team/eval orgs (e.g., independent evaluators),
   audits, credible analyst deep-dives. Best for *validated* claims.
3. **Community / practitioner** — forums, issue trackers, engineering blogs,
   social posts. Leads and real-world signal only; verify before use.
4. **Vendor marketing** — launch blogs, decks, self-reported benchmarks. Capture
   claims but tag as interested party.

## Steps
1. For each P0/P1 question, search tiers top-down until coverage is adequate;
   drop tiers only to fill gaps.
2. **Prioritize primary documents**: always pull the system/model card, pricing
   page, and any independent evaluation before relying on secondary write-ups.
3. For **every** item, record `{claim, source(url/author), tier, capture_date,
   model_version, question_id}`.
4. Chase the deep specifics the report needs: benchmark methodology, latency
   figures, rate limits, data-use/retention terms, license restrictions,
   deprecation timelines, safety/eval disclosures.
5. Log **information gaps** where no credible source answers a question — gaps
   are outputs, not failures.
6. Track recency; flag stale sources and superseded versions.

## Output (hand to `source-credibility-grading`)
- Evidence pool with full provenance per item.
- Information-gap list (candidates for hands-on-probing or vendor questions).

## Quality checks
- No item lacks a source, date, and (where relevant) model version.
- Primary docs (card/pricing/license) and ≥1 independent eval were sought for P0s.
- Vendor vs independent sources are already distinguishable.
