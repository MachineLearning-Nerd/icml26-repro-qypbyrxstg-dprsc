# Current verification — Claim 1

**Verdict: BLOCKED.**

Theorem 1.3 states: for every \(\varepsilon>0\) and \(\delta\in(0,1)\), there exists an \((\varepsilon,\delta)\)-DP algorithm whose **maximum absolute error over \(Q\)** is

\[
O\!\left(
\frac{\widetilde{\mathrm{HS}}_{f_H}(G)\,
\sqrt{(\varepsilon+\log(1/\delta))\log(n|Q|)}\,
\log^{2d}n}{\varepsilon}
\right),
\]

with probability at least \(1-1/n\); hidden constants are \(c^{O(d)}\). The paper separately calls it the first efficient DPRSC algorithm and gives polynomial time for \(d=O(\log n/\log\log n)\).

Raw facts: theorem `1.3`; metric `max absolute error`; success `1-1/n`; hidden constants `c^O(d)`; current verdict `BLOCKED`.

- [Source audit](evidence/claim-1/source_audit.md)
- [Raw source facts](evidence/claim-1/raw_source_facts.json)
- [Source verifier](evidence/verify_claim_sources.py)
- [Method](evidence/claim-1/method.md)
- [Limitations](evidence/claim-1/limitations.md)

The negative control drops the probability and dimension-dependent constants and exits nonzero. A proof-level privacy/utility/complexity certificate and priority audit remain missing.
