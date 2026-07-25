# Current verification status

**Claim 3 is VERIFIED, Claim 4 is FALSIFIED, and Claims 1, 2, and 5 remain
BLOCKED.** Exact source contracts now replace the rejected historical ontology.
No source-only check is presented as scientific verification.

Fixed command on every experiment node:

```bash
uv run --frozen python repro/src/run_campaign.py
```

Paper source: [archived ar5iv HTML](evidence/claim-5/source/2606.08179.html), SHA-256 `9387c720239542f024ef31654e84ced6e2687818f8f17703945aa114aab02a5b`, retrieved `2026-07-25T06:41:27Z`.

## Visibility matrix

| Claim | Canonical page | Code visible | Data inline | Raw link | Checker | Control | Exact claim tested | Reviewer verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | [Claim 1](#/current-claim-1) | Yes | Source facts | Yes | Source scope only | Quantifier omission fails | Contract yes; proof pending | BLOCKED |
| 2 | [Claim 2](#/current-claim-2) | Yes | Primary-source hashes and exact recursion ratios | Yes | Reconstruction SMT + exact-rational recursion + independent checker | Omitted rounds, squared-error promotion, and GS substitution fail | Exact contract; written same-exponent partial-discrepancy step is unproved | BLOCKED |
| 3 | [Claim 3](#/current-claim-3) | Yes | Proof obligations and exact counts inline | Yes | General analytic + exhaustive + independent Decimal | Average/max, tied boundary, and under-noised controls fail | Exact Algorithm 1–3 chain and Theorem 3.3 | VERIFIED |
| 4 | [Claim 4](#/current-claim-4) | Yes | Counterexample and formal run inline | Yes | Analytic + implementation + independent Decimal | Clipped repair rejects counterexample | Exact named Algorithm 4/5 chain | FALSIFIED |
| 5 | [Claim 5](#/current-claim-5) | Yes | Source result inline | Yes | Two source checkers pass | Exit 2 confirmed | Source contract yes; experiments pending | BLOCKED |

Claim 2 has completed three distinct verification routes plus the mandatory
fourth falsification route; no valid counterexample was found. It is a
rigorously routed BLOCKED result. Publication remains blocked by Claims 1 and
5 and by the remaining release gates.
