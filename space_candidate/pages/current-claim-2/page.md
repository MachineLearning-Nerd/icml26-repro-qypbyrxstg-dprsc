# Current verification — Claim 2

**Verdict: BLOCKED.**

Theorem 1.4 quantifies over every pattern \(H\), every \((\varepsilon,\delta)\)-DP algorithm with constant \(\varepsilon>0\) and \(\delta\in[0,1/2)\), sufficiently large constant success probability, \(|Q|\ge n^c\) for sufficiently small constant \(c>0\), and infinitely many \(n\). Its three regimes scale against \(\widetilde{\mathrm{HS}}_{f_H}(G)\), not GS.

Raw facts inline:

```json
{"constant_d":"Omega(log^(d-1)(n) * HS_tilde)","d_O_log_n":"2^Omega(d) * HS_tilde","d_Omega_log_n":"n^Omega(1) * HS_tilde"}
```

- [Exact contract](evidence/claim-2/claim_contract.json)
- [Source audit](evidence/claim-2/source_audit.md)
- [Primary-source manifest with URLs and SHA-256](evidence/claim-2/primary_source_manifest.json)
- [Raw source facts](evidence/claim-2/raw_source_facts.json)
- [Source verifier](evidence/verify_claim_sources.py)
- [Dependency-audit verifier](evidence/claim-2/verify_claim2_dependency_audit.py)
- [Independent checker](evidence/claim-2/verify_claim2_dependency_independent.py)
- [Raw dependency-audit record](evidence/claim-2/dependency_audit_run.json)
- [Method](evidence/claim-2/method.md)
- [Limitations](evidence/claim-2/limitations.md)

## What the primary sources establish

| Dependency | Exact role | Audit result |
| --- | --- | --- |
| Matoušek–Nikolov 2015, Theorem 1 | Fixed-\(d\) standard/hereditary box discrepancy \(\Omega(\log^{d-1}n)\) | Pinned and matched |
| Chazelle–Lvov 2001, Theorem 2.1/Corollary 2.2 | High-dimensional standard discrepancy \(2^{\Omega(d)}\), then \(n^{\Omega(1)}\) | Pinned and matched |
| Muthukrishnan–Nikolov 2012, Lemma 5 | Sum partial discrepancies over geometric residual sizes | Pinned; exposes the gap below |
| Eden et al. 2023, Lemma 3.9 | Expected Hamming error at least \(e^{-\varepsilon}(1/2-\delta)N\) | Independently re-proved by an UNSAT SMT obligation |

All five source PDFs were retrieved on `2026-07-25` with the recorded explicit
User-Agent. Their exact URLs and hashes are in the manifest.

## Exact blocking gap

Appendix D uses Lemma D.2 to transfer a standard discrepancy lower bound to
the same-exponent partial discrepancy required by the reconstruction attack.
For \(\alpha=1/2\) and \(n=2^k\), however, the recursion has
\(k+1=\Theta(\log n)\) scales.

The independent exact-rational countermodel gives:

| \(d\) | Per-scale sequence | Largest term / target at \(k=128\) | Sum / target at \(k=128\) |
| --- | --- | --- | --- |
| 2 | \(f_j=1\) | `1/128` | `1` |
| 3 | \(f_j=j\) | `1/128` | `129/256` |
| 4 | \(f_j=j^2\) | `1/128` | `11051/32768` |

Thus every individual scale is little-\(o\) of the asserted target while
their recursion sum remains \(\Theta\) of it. The cited primary results do
not supply the missing same-exponent partial-discrepancy theorem.

## Four verification routes

1. **Primary-source closure:** the DP reconstruction dependency is discharged,
   but the geometric partial-discrepancy dependency is not.
2. **Conditional proof and finite exhaust:** six universal SMT obligations
   and all 16 databases on a 4-point/6-box instance validate the paper-specific
   graph lift only after assuming the missing discrepancy premise.
3. **Alternative published theorem:** the 2012 orthogonal-range result
   lower-bounds average squared error; converting it to maximum absolute error
   takes a square root and does not yield Claim 2's exponent.
4. **Dedicated falsification attempt:** the recursion sequence is a
   countermodel to a proof inference, not a box-incidence/DP counterexample;
   the finite instance is not asymptotic; and the zero-edge pattern makes
   Algorithm 4 undefined rather than contradicting a numerical bound. No valid
   assumption-satisfying counterexample was found.

Two controls—omitting the recursion rounds and promoting squared error without
a square root—exit nonzero. The GS-substitution source control also exits
nonzero. The honest scientific verdict is therefore **BLOCKED**, not
FALSIFIED.
