---
name: layered-sourcing
description: >-
  Systematically collects information about an external model in credibility
  tiers — first-party authoritative, independent third-party, community/rumor,
  and vendor marketing — recording a URL and capture date for every item. Use
  after research-scoping and before grading/verification, whenever gathering
  evidence about a model the agent does not own. Produces a structured evidence
  pool that downstream grading and cross-verification depend on.
---

# Layered Sourcing

Gather evidence deliberately, tier by tier, and capture provenance as you go.
Never collect a fact without its source link and the date you saw it.

## Inputs
- The prioritized question list + evaluation dimensions from `research-scoping`.

## Source tiers (search top-down)

1. **First-party authoritative** — official model card, technical report, paper,
   docs, pricing page, changelog, license, system card. Best for *stated*
   specs and policies; still treat performance claims skeptically.
2. **Independent third-party** — reputable public leaderboards, independent
   benchmarks, academic reproductions, audits, well-known analyst write-ups.
   Best for *validated* capability claims.
3. **Community / practitioner** — forums, issue trackers, blogs, social posts.
   Use as leads and "real-world feel" only; must be verified before use.
4. **Vendor marketing** — launch blogs, sales decks, self-reported benchmarks.
   Capture the claims, but tag them as interested parties (discount heavily).

## Steps

1. For each P0/P1 question, search the tiers top-down until you have enough
   coverage. Prefer higher tiers; drop to lower tiers only to fill gaps.
2. For **every** item captured, record:
   - the claim (concise),
   - the exact source (URL/title/author),
   - the **capture date** and, if available, the **model version** it refers to.
3. Note when a question yields **no** credible source — that gap is an output,
   not a failure.
4. Watch recency: prefer the newest authoritative info; flag stale sources.

## Output (hand to `source-credibility-grading`)
- An evidence pool: list of `{claim, source, tier, date, model_version, question_id}`.
- A list of unanswered questions (information gaps).

## Quality checks
- No item lacks a source and a date.
- Each P0 question has at least one attempted source across tiers.
- Vendor vs independent sources are already distinguishable.
