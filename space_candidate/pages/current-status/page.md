# Current verification status

**Claim 3 is VERIFIED, Claim 4 is FALSIFIED, and Claims 1, 2, and 5 remain
BLOCKED.** Exact source contracts now replace the rejected historical ontology.
No source-only, toy, proxy, or finite asymptotic calibration is presented as
scientific verification.

Fixed command on every experiment node:

```bash
uv run --frozen python repro/src/run_campaign.py
```

Paper source: [archived ar5iv HTML](evidence/claim-5/source/2606.08179.html), SHA-256 `9387c720239542f024ef31654e84ced6e2687818f8f17703945aa114aab02a5b`, retrieved `2026-07-25T06:41:27Z`.

## Visibility matrix

| Claim | Canonical page | Code visible | Data inline | Raw link | Checker | Control | Exact claim tested | Reviewer verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | [Claim 1](#/current-claim-1) | Yes | Four-route results and exact counterexample point | Yes | Primary + independent Decimal | Three semantic controls exit nonzero | Exact Theorem 1.3 quantifiers; witness flaw does not falsify existential theorem | BLOCKED |
| 2 | [Claim 2](#/current-claim-2) | Yes | Primary-source hashes and exact recursion ratios | Yes | Reconstruction SMT + exact-rational recursion + independent checker | Omitted rounds, squared-error promotion, and GS substitution fail | Exact contract; written same-exponent partial-discrepancy step is unproved | BLOCKED |
| 3 | [Claim 3](#/current-claim-3) | Yes | Proof obligations and exact counts inline | Yes | General analytic + exhaustive + independent Decimal | Average/max, tied boundary, and under-noised controls fail | Exact Algorithm 1–3 chain and Theorem 3.3 | VERIFIED |
| 4 | [Claim 4](#/current-claim-4) | Yes | Counterexample and formal run inline | Yes | Analytic + implementation + independent Decimal | Clipped repair rejects counterexample | Exact named Algorithm 4/5 chain | FALSIFIED |
| 5 | [Claim 5](#/current-claim-5) | Yes | 144 accuracy comparisons and 9 runtime rows inline | Yes | Source + accuracy + runtime independent checkers | Query-budget and biased-sampler controls exit nonzero | Exact Section 5 accuracy and runtime protocols | BLOCKED |

Claims 1 and 2 each completed exactly three materially different verification
routes plus the mandatory fourth falsification route. Neither fourth route
falsified the exact theorem: Claim 1 is existential over algorithms, and Claim
2's recursion countermodel attacks a proof inference rather than constructing
a box-incidence/DP counterexample. They are rigorously documented BLOCKED
results.

Claim 5 completed the full released-data protocol. Its accuracy ordering holds
in all 144 matched comparisons. The runtime trend is strong but the literal
3–4-order statement is not uniform on this hardware, and insufficient
hardware detail prevents a valid falsification. It therefore remains BLOCKED
with MEDIUM confidence.

## Reproducibility surface

- [Fixed command entrypoint](evidence/reproduction/repro/src/run_campaign.py)
- [Locked project definition](evidence/reproduction/pyproject.toml)
- [Exact dependency lock](evidence/reproduction/uv.lock)
- [Released algorithms](evidence/reproduction/upstream/ourAlg.py)
- [Released range tree](evidence/reproduction/upstream/range_tree.py)
- [Released baselines](evidence/reproduction/upstream/baseline.py)
- [Release report and score forecast](#/release-report)
- [Evaluator-blind red-team record](#/red-team)

The full text-only evidence tree includes all three released datasets, every
runner and independent checker needed by the fixed command, raw run records,
seeds, controls, compute estimates, actual CPU allocations, runtimes, and
limitations. Terminal HF `cpu-upgrade` run
`7749e3aa-7f7d-44cd-ba3f-c25f5784b525` used Git SHA
`ff86be4c06d2a8f8b65c735478830e0c42db5e8a`, exposed 64 logical CPUs, and
completed in 11m40s. Published revision
`0af4a5487541cbfa8e85a687a24483a1075c3454` passed an exact-download manifest
check and evaluator traversal. The paper is awaiting the live judge; the
previous live score remains 5/10.
