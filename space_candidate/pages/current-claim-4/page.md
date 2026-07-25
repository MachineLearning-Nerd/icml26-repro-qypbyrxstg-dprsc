# Current verification — Claim 4

**Verdict: FALSIFIED.**

The exact chain is Algorithm 4 `EstimateHS` → Algorithm 5 `ADP_RSC` → the range-tree mechanism. It is not a well-defined randomized algorithm on all of its stated domain.

## Positive-probability counterexample

Take the empty simple graph on three vertices, \(H=\) 2-star, \(d=1\), one full-range query, \(\varepsilon=2\), and \(\delta=10^{-5}\). All stated input assumptions hold. Here \(f_H^{(2)}(G)=1\) and \(f_H^{(1)}(G)=0\), so Algorithm 4 returns

\[
\widetilde{\mathrm{HS}}_{f_H}(G)
=\frac{\ln(1/\delta')}{\varepsilon'}
+\operatorname{Lap}(1/\varepsilon').
\]

For a Laplace random variable of scale \(1/\varepsilon'\),

\[
\Pr[\widetilde{\mathrm{HS}}_{f_H}(G)<0]=\delta'/2>0.
\]

Algorithm 5 uses this negative value as a later Laplace scale. Definition 2.5 requires a positive scale (otherwise its displayed density is not a probability density), and the released NumPy implementation raises `ValueError`. There is no clipping or fallback in Algorithm 4, Algorithm 5, or the released code.

This falsifies the named Algorithm 4/5 guarantee. It does **not** claim that no repaired approximate-DP algorithm can exist, and it does not falsify Claim 1's bare existence theorem.

- [Exact contract](evidence/claim-4/claim_contract.json)
- [Source audit](evidence/claim-4/source_audit.md)
- [Raw source facts](evidence/claim-4/raw_source_facts.json)
- [Machine-readable counterexample](evidence/claim-4/counterexample.json)
- [Formal cumulative run record](evidence/claim-4/counterexample_run.json)
- [Source verifier](evidence/verify_claim_sources.py)
- [Analytical and released-code checker](evidence/claim-4/verify_claim4_counterexample.py)
- [Independent 60-digit Decimal checker](evidence/claim-4/verify_claim4_counterexample_independent.py)
- [Method](evidence/claim-4/method.md)
- [Limitations](evidence/claim-4/limitations.md)

The clipped repair `max(0, EstimateHS)` is the control: it removes this
counterexample, and the counterexample verifier exits nonzero. The formal run
used the fixed command at Git SHA
`0f98574ffb380f01e027583eba5fa3b932d2946c`, estimated one workload core,
observed 8 allocated logical CPUs while remaining single-threaded, and
completed in 4.139 seconds. The primary and independent checkers passed, the
released code raised `ValueError`, and the clipped control failed as intended.
