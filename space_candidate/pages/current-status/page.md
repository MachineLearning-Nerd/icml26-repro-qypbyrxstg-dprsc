# Current verification status

**All five scientific claims are currently BLOCKED.** Exact source contracts now replace the rejected historical ontology. No source-only check is presented as scientific verification.

Fixed command on every experiment node:

```bash
uv run --frozen python repro/src/run_campaign.py
```

Paper source: [archived ar5iv HTML](evidence/claim-5/source/2606.08179.html), SHA-256 `9387c720239542f024ef31654e84ced6e2687818f8f17703945aa114aab02a5b`, retrieved `2026-07-25T06:41:27Z`.

## Visibility matrix

| Claim | Canonical page | Code visible | Data inline | Raw link | Checker | Control | Exact claim tested | Reviewer verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | [Claim 1](#/current-claim-1) | Yes | Source facts | Yes | Source scope only | Quantifier omission fails | Contract yes; proof pending | BLOCKED |
| 2 | [Claim 2](#/current-claim-2) | Yes | Source facts | Yes | Source scope + historical partial SMT | GS substitution fails | Contract yes; imported lemmas pending | BLOCKED |
| 3 | [Claim 3](#/current-claim-3) | Yes | Source facts | Yes | Source scope only | Average-for-maximum substitution fails | Contract yes; proof pending | BLOCKED |
| 4 | [Claim 4](#/current-claim-4) | Yes | Source facts | Yes | Source scope only | Skipping EstimateHS fails | Contract yes; EstimateHS/proof pending | BLOCKED |
| 5 | [Claim 5](#/current-claim-5) | Yes | Source result inline | Yes | Two source checkers pass | Exit 2 confirmed | Source contract yes; experiments pending | BLOCKED |

This matrix is intentionally incomplete as scientific evidence. Publication remains blocked until every row contains a final VERIFIED, FALSIFIED, or rigorously routed BLOCKED result and evaluator-visible run evidence.
