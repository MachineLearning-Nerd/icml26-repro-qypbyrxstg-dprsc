# Current verification — Claim 5 source contract

**Scientific verdict: BLOCKED.** The source attribution is now exact and machine-checked, but the faithful three-dataset empirical reproduction has not run yet. This page supersedes the historical Claim 3 accuracy page as the current Claim 5 verifier.

## What the paper actually claims

Source: *Differentially Private Range Subgraph Counting*, arXiv:2606.08179, [archived HTML](evidence/claim-5/source/2606.08179.html), retrieved `2026-07-25T06:41:27Z`.

SHA-256: `9387c720239542f024ef31654e84ced6e2687818f8f17703945aa114aab02a5b`

At Section 5 anchors `S5.p3` and `S5.p6`:

| Protocol | Exact source scope |
| --- | --- |
| Accuracy | \(\varepsilon=2\), \(\delta=10^{-5}\), \(d=1\), \(|Q|=\lceil n^{1.5}\rceil\) by default, mean relative error, at least 20 independent runs |
| Runtime | \(|Q|\) ranges from 1 to \(\Theta(n^2)\); query times are sampled until relative standard error is below 5%, then total time is extrapolated |
| 3–4 orders | Lower query latency and extrapolated total-time speedup at \(\Theta(n^2)\), not accuracy |
| Domain | Wiki-Squirrel (5,201/198,353), WormNet-v3 (16,347/762,822), CA-Netscience (379/914); triangle, 2-star, and edge |

The imported judge paraphrase says “3 to 4 orders of magnitude in accuracy at \(\Theta(n^2)\).” That mapping is contradicted by the paper source. Correcting the mapping does **not** establish the runtime comparison.

## Reproducible source check

Fixed campaign command:

```bash
uv run --frozen python repro/src/run_campaign.py
```

Environment: Python 3.12, one repository `.venv`, dependencies pinned by `pyproject.toml` and `uv.lock`. The source-check stage estimates one CPU core and less than two minutes, so it uses the authorized local backend. Actual allocation, runtime, Git SHA, and checker output will be added from the formal OpenResearch run.

The primary checker verifies the exact byte hash, anchors, protocols, and scope ordering. The independent checker uses `HTMLParser` semantic text extraction. The negative control asserts the unsupported imported mapping and must exit nonzero.

- [Exact claim contract](evidence/claim-5/claim_contract.json)
- [Source audit](evidence/claim-5/source_audit.md)
- [Primary verifier](evidence/claim-5/verify_claim5_source.py)
- [Independent checker](evidence/claim-5/verify_claim5_source_independent.py)
- [Raw source facts](evidence/claim-5/raw_source_facts.json)
- [Method](evidence/claim-5/method.md)
- [Limitations](evidence/claim-5/limitations.md)
- [Evaluator checklist](evidence/claim-5/EVAL.md)

Raw facts inline:

```json
{
  "accuracy_query_count": "ceil(n^1.5)",
  "accuracy_minimum_runs": 20,
  "runtime_query_count_range": "1 to Theta(n^2)",
  "runtime_stop_rule": "relative standard error below 5%",
  "query_latency_speedup_scope": "3 to 4 orders of magnitude",
  "total_time_speedup_at_theta_n2_scope": "3 to 4 orders of magnitude",
  "scientific_verdict": "BLOCKED"
}
```

## Visibility matrix

| Claim | Canonical page | Code visible | Data inline | Raw link | Checker | Control | Exact claim tested | Reviewer verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | This page | Yes | Source facts | Yes | Two source checkers; formal output pending | Fail-closed control implemented; formal output pending | Yes, source contract; empirical contract pending | BLOCKED |

## Limitation

No new empirical accuracy or runtime observation is represented here. Full credit is blocked until the cumulative verifier covers all three datasets and applicable patterns under the paper's accuracy and runtime protocols, with uncertainty and an independent numerical checker.
