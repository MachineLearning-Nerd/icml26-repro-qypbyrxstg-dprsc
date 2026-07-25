# Claim 2 method

The source verifier checks every domain and regime marker. The negative control replaces \(\widetilde{\mathrm{HS}}\) with GS and drops the success, query-size, and infinitely-many quantifiers; it must exit nonzero.

The dependency audit uses four materially different routes:

1. Pin all cited primary sources and reconstruct the DP Hamming-error
   inequality independently with Z3.
2. Audit the Appendix D partial-coloring recursion with exact rational power
   sums; this finds a missing \(\Theta(\log n)\) accumulation.
3. Test whether the earlier private orthogonal-range theorem closes the gap.
   It controls average squared error and only implies a square-root exponent
   for maximum absolute error.
4. Seek an exact assumption-satisfying falsification. The recursion
   countermodel is only a countermodel to the proof inference, the finite
   graph is not asymptotic, and the zero-edge pattern makes Algorithm 4
   undefined rather than numerically contradicting the theorem.

The existing six-obligation universal SMT check and 16-database exhaustive
certificate remain useful conditional evidence for the paper-specific graph
lift. They do not discharge the missing partial-discrepancy result.
