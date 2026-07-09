---
name: operational-readiness
description: >-
  Assesses whether an external model can be relied on in production — latency
  distribution, throughput, rate limits and quotas, availability and regional
  coverage, data residency, SLA/uptime, versioning and deprecation policy,
  support, and vendor stability/roadmap. Use in the deep-analysis phase for any
  adoption decision that goes beyond a demo. Produces a production-readiness
  assessment that surfaces operational blockers the capability analysis alone
  would miss.
---

# Operational Readiness

A model that benchmarks well but can't be operated reliably is not adoptable.
Evaluate the model as a production dependency.

## Inputs
- Facts from `evidence-sourcing` (docs, status pages, pricing/limits); observed
  latency from `hands-on-probing`; the workload profile from `decision-framing`.

## Dimensions to assess
- **Latency & throughput** — p50/p95 latency for realistic prompt/output sizes;
  tokens/sec; streaming; batch options. Prefer measured over advertised.
- **Rate limits & quotas** — request/token limits per tier; how to raise them;
  whether they support your peak QPS. Ties into effective cost/throughput.
- **Availability & regions** — general availability vs gated/preview; regional
  endpoints; data-residency options and any uplift.
- **Reliability & SLA** — published uptime/SLA, historical incidents, status-page
  track record.
- **Versioning & deprecation** — version pinning, notice periods, snapshot
  availability, forced-migration history. (Silent version drift is a real risk.)
- **Access & onboarding** — waitlists/approval, KYC/government gating, enterprise
  terms, regional legal restrictions.
- **Support & ecosystem** — SDKs, docs quality, enterprise support, community.
- **Vendor stability & roadmap** — funding/backing, release cadence, strategic
  direction, likelihood of continuity.

## Steps
1. Collect each dimension; prefer measured/independent data over vendor claims.
2. Flag any **hard blockers** for the workload (e.g., no region coverage, quotas
   below peak, gated access, aggressive deprecation).
3. Note where operational facts are **unknown** (common for preview models) and
   route to vendor questions.

## Output (feeds `comparison-synthesis`, `risk-compliance-review`, `research-report-authoring`)
- Production-readiness assessment per dimension with a ready / caveated / blocker rating.
- List of operational blockers and open questions for the vendor.

## Quality checks
- Latency/throughput are measured or clearly marked as advertised.
- Deprecation/versioning policy is addressed (not just current specs).
- Hard blockers for the specific workload are called out explicitly.
