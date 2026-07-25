# Current verification — Claim 3

**Verdict: BLOCKED.**

Theorem 3.3 concerns the exact chain Algorithm 1 `Proj` → Algorithm 2 `TreeConst` → Algorithm 3 `PDP_RSC`. For every \(\varepsilon>0\), it claims pure \(\varepsilon\)-DP and maximum absolute error

`O(GS_fH * sqrt(log(n|Q|)) * log^(3d)(n) / epsilon)`

with probability at least `1 - 1/n`, hiding constants `c^O(d)`.

- [Exact contract](evidence/claim-3/claim_contract.json)
- [Source audit](evidence/claim-3/source_audit.md)
- [Raw source facts](evidence/claim-3/raw_source_facts.json)
- [Source verifier](evidence/verify_claim_sources.py)
- [Method](evidence/claim-3/method.md)
- [Limitations](evidence/claim-3/limitations.md)

The average-error-for-maximum-error negative control exits nonzero. Complete projection, range-tree, privacy-composition, and concentration certificates remain pending.
