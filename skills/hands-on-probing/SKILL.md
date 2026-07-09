---
name: hands-on-probing
description: >-
  Runs rigorous, reproducible first-hand tests against an external model via its
  API or open weights to verify claims and produce original evidence — with a
  documented protocol (representative tasks, metric, sample size, fixed
  parameters/version) rather than ad-hoc prompts. Use in the deep-analysis phase
  when the model is reachable and claims are vendor-only, disputed, or
  decision-critical. Produces first-hand measurements (the highest-credibility
  evidence in the report) plus transcripts. Skip only when no access exists, and
  flag that limitation prominently.
---

# Hands-on Probing

First-hand testing is what turns a literature review into a research report. Do
it whenever access exists, and do it **rigorously and reproducibly**.

## Preconditions & safety
- Only with legitimate access (API key, open weights, sanctioned account) and
  respecting the provider's terms.
- Never send secrets or sensitive/proprietary data to a third-party model; use
  synthetic or sanctioned non-sensitive inputs.
- Keep tests small and cost-aware; respect rate limits and budget.

## Inputs
- Claims to verify from `capability-profiling`/`cross-verification`; the workload
  profile from `decision-framing`.

## Steps

1. **Design a real protocol, not ad-hoc prompts.** Define:
   - a task set that mirrors the actual workload (include hard/edge cases),
   - the metric and a clear rubric for pass/fail or quality scoring,
   - sample size / number of trials for signal (not n=1),
   - fixed parameters (model version, temperature, reasoning mode, tools, seed).
2. **Include comparison baselines** where feasible — the same tasks on the
   incumbent or a rival model, so results are relative, not absolute.
3. **Record the environment** for reproducibility: version/endpoint, date,
   parameters, harness, cost per run.
4. **Capture raw outputs and transcripts**, especially failures and edge cases —
   probe where it breaks, not only where it works. Coordinate with
   `failure-mode-analysis` to include adversarial/reward-hacking probes.
5. **Log cost & latency observed** during runs (feeds `cost-tco-modeling` and
   `operational-readiness`).
6. **Compare results to the claims** — confirm, contradict, or nuance vendor and
   third-party numbers; record the delta.

## Output (feeds `comparison-synthesis`, `cost-tco-modeling`, `operational-readiness`, `failure-mode-analysis`)
- First-hand measurements (Tier A) with full protocol + environment + date.
- Transcripts of representative successes and failures.
- Observed cost/latency data points.
- Claims upgraded/downgraded based on testing.

## Quality checks
- Protocol is documented and repeatable by someone else.
- Tasks reflect the real workload; sample size gives more than anecdote.
- No sensitive data exposed; version/params recorded.
