# Claim 2 source audit

Theorem 1.4 concerns an arbitrary private mechanism, sufficiently large constant success probability, sufficiently many queries, and infinitely many graph sizes. Its scale is \(\widetilde{\mathrm{HS}}_{f_H}(G)\), not GS. The judge paraphrase's GS substitution drops a material qualifier.

The proof imports discrepancy results from Chazelle–Lvov, Muthukrishnan–Nikolov, and Matoušek–Nikolov, and a reconstruction lower bound traced through De and Eden et al. These dependencies must be independently discharged for full verification.

## Primary-source result

Five exact PDFs were retrieved with an explicit browser User-Agent on
2026-07-25 and pinned in `primary_source_manifest.json`. The independent
audit confirms:

- Eden et al. Lemma 3.9 is sufficient for the reconstruction step, and its
  one-coordinate inequality has been independently proved with an SMT
  refutation.
- Matoušek–Nikolov establish standard/hereditary box discrepancy
  \(\Omega(\log^{d-1} n)\) for fixed \(d\).
- Chazelle–Lvov establish standard high-dimensional box discrepancy
  \(2^{\Omega(d)}\) and \(n^{\Omega(1)}\) in the corresponding regimes.
- Muthukrishnan–Nikolov Lemma 5 explicitly sums partial discrepancies over
  geometric residual sizes.

## Unclosed dependency

Appendix D applies that last recursion as though it had a constant number of
terms. For \(\alpha=1/2\) and \(n=2^k\), it has \(k+1=\Theta(\log n)\)
terms. The exact countermodel sequence \(f_j=1\) for \(d=2\) has each
single scale \(f_j=o(\log n)\), while the recursion sum is
\(\Theta(\log n)\). For dimensions 3 and 4, \(f_j=j^{d-2}\) gives the same
one-logarithm loss. Therefore the cited results and the written Appendix D
argument do not establish the same-exponent partial discrepancy needed by
Lemma 4.3.

This is a proof gap, not an assumption-satisfying counterexample to the
theorem. Claim 2 remains **BLOCKED**, not FALSIFIED.
