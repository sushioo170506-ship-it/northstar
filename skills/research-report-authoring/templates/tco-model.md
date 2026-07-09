# Cost / TCO Model Template

Model the real cost for the workload — not the sticker price. Express economics
per unit of value (cost-per-successful-task), and show assumptions.

## 1. Pricing structure (facts)

| Item | Model A | Model B | Source | Tier |
|---|---|---|---|---|
| Input $/1M | | | | |
| Output $/1M | | | | |
| Cache write / read $/1M | | | | |
| Reasoning/thinking tokens billing | | | | |
| Batch discount | | | | |
| Priority / fast-mode surcharge | | | | |
| Regional / data-residency uplift | | | | |
| Minimums / commitments | | | | |

## 2. Per-task token estimate (from real workload)

| Component | Tokens/task | Basis (measured / estimated) |
|---|---|---|
| Prompt + context | | |
| Output | | |
| Hidden reasoning tokens | | |
| Agentic/subagent fan-out (if any) | | |
| Retries (× failure rate) | | |
| **Effective tokens/task** | | |

## 3. Cost-per-successful-task

`cost_per_success = cost_per_task / success_rate`  (success_rate from capability/failure analysis)

| Model / tier | $/task | Success rate | **$/successful task** |
|---|---|---|---|
| | | | |

## 4. Monthly cost at scale (scenarios)

| Scenario | Volume (tasks/mo) | Caching | Mode (std/extended/ultra) | Est. monthly $ |
|---|---|---|---|---|
| Typical | | | | |
| Peak | | | | |

## 5. Assumptions, sensitivities & hidden costs
- Key assumptions (with confidence): …
- Sensitivity: which assumption most moves the number? …
- Hidden/likely-underestimated: retries, long-context re-sends, eval/monitoring,
  egress, data-residency uplift, throughput ceilings under rate limits.
- ⚠ Vendor-only pricing terms flagged: …
