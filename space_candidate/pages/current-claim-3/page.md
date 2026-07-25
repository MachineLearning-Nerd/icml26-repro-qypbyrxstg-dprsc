# Current verification — Claim 3

**Verdict: VERIFIED.**

Theorem 3.3 concerns the exact chain Algorithm 1 `Proj` → Algorithm 2 `TreeConst` → Algorithm 3 `PDP_RSC`. For every \(\varepsilon>0\), it claims pure \(\varepsilon\)-DP and maximum absolute error

`O(GS_fH * sqrt(log(n|Q|)) * log^(3d)(n) / epsilon)`

with probability at least `1 - 1/n`, hiding constants `c^O(d)`.

- [Exact contract](evidence/claim-3/claim_contract.json)
- [Source audit](evidence/claim-3/source_audit.md)
- [Raw source facts](evidence/claim-3/raw_source_facts.json)
- [Source verifier](evidence/verify_claim_sources.py)
- [General proof certificate](evidence/claim-3/proof_certificate.md)
- [Raw primary certificate JSON](evidence/claim-3/pure_dp_certificate_run.json)
- [Executable proof and exhaustive checker](evidence/claim-3/verify_claim3_pure_dp.py)
- [Independent Decimal and functional checker](evidence/claim-3/verify_claim3_pure_dp_independent.py)
- [Method](evidence/claim-3/method.md)
- [Limitations](evidence/claim-3/limitations.md)

## Proof reconstruction

The checker reconstructs the complete argument rather than comparing observed
errors to an arbitrary hidden Big-O constant:

1. `Proj` maps every occurrence exactly once to its public-rank span. For tied
   public attributes, the deterministic completion selects the minimum rank
   among lower-bound ties and maximum rank among upper-bound ties.
2. Edge addition is coordinatewise monotone, so projection L1 sensitivity is
   exactly the scalar subgraph-count sensitivity and is bounded by
   `f_H(K_n)-f_H(K_n-e)`.
3. A projected coordinate contributes to at most
   `(ceil(log2(n))+1)^(2d)` released tree nodes. Adding independent Laplace
   noise at that total sensitivity divided by epsilon is one vector Laplace
   mechanism; all answers are post-processing.
4. A separately derived Laplace moment-generating-function bound, the direct
   distinct-query bound `|Q| <= (n+1)^(2d)`, and a union bound yield the claimed
   maximum-error probability `1-1/n`. Simplification gives exactly the paper's
   `log^(3d)(n) * sqrt(log(n|Q|))` order with `c^O(d)` constants.

## Raw checker results

- Primary functional exhaust: 64 four-vertex graphs × 16 public-attribute
  assignments (including ties) × edge/2-star/triangle; 9,216 projection-query
  identities and 9,216 neighboring sensitivity checks passed.
- Independent checker: 1,296 tied-attribute edge checks and 3,393
  high-precision concentration-precondition checks passed.
- Negative controls: average-for-maximum source substitution, naive tied
  boundary, and under-noised range tree all exit nonzero.

The finite exhaust is corroboration, not the universal proof. The analytic
certificate is what discharges the quantified theorem. Formal cumulative run
output will add the experiment Git SHA, CPU allocation, runtime, and exact
control exit records.
