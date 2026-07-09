---
name: risk-compliance-review
description: >-
  Reviews the technical, business, legal, and compliance risks of adopting an
  external model — safety/alignment (incl. reward-hacking and out-of-intent
  behavior in production), security/misuse, legal & IP (license, output
  ownership), privacy & data-use (training on your data, retention, review),
  vendor lock-in and concentration risk, and regulatory exposure — each with a
  mitigation and residual-risk rating. Use in the deep-analysis phase for any
  adoption or compliance decision. Produces a structured risk register.
---

# Risk & Compliance Review

Translate findings into the risks a decision-maker must own. Cover technical AND
business/legal risk; a capability win with an unacceptable data-use clause is not
a win.

## Inputs
- The failure-mode catalog from `failure-mode-analysis`; license/data terms from
  `evidence-sourcing`; ops facts from `operational-readiness`.

## Risk categories (keep those relevant)
- **Safety / alignment** — production impact of reward-hacking, over-autonomy,
  unsafe agentic actions; need for human oversight/guardrails.
- **Security / misuse** — prompt injection, data exfiltration, dual-use
  capability, provider-side safeguards and their friction.
- **Legal & IP** — license terms and usage restrictions, ownership/indemnity of
  generated outputs, training-data provenance disputes.
- **Privacy & data governance** — is your data used for training? retention,
  human review, account-level monitoring, sub-processors, cross-border transfer.
- **Vendor lock-in & concentration** — proprietary APIs/features, switching cost,
  single-vendor dependence, portability to alternatives.
- **Regulatory & geopolitical** — export controls, government-gating/approval
  processes, sector regulation (health/finance), regional compliance (e.g. data
  residency).
- **Continuity** — deprecation, vendor viability, roadmap risk.

## Steps
1. For each relevant risk: state the **risk, evidence + credibility, likelihood,
   impact, mitigation, and residual risk** (Low/Med/High).
2. Distinguish **showstoppers** (violate a hard requirement) from **manageable**
   risks (mitigable with guardrails/contract terms).
3. Turn open compliance questions into a **vendor due-diligence question list**.
4. Keep facts (contract terms, disclosures) separate from your risk assessment.

## Output (feeds `comparison-synthesis`, `research-report-authoring`)
- A risk register (risk · evidence · likelihood · impact · mitigation · residual).
- Showstopper flags and a vendor due-diligence question list.

## Quality checks
- Both technical and legal/business risks are covered.
- Every risk has a mitigation and a residual rating.
- Data-use/training terms and output IP are explicitly addressed.
