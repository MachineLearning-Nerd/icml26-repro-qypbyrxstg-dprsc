# Claim 4 source audit

Algorithm 5 is not a standalone range-tree experiment. Its defining difference from Algorithm 3 is private calibration using Algorithm 4's higher-order local-sensitivity estimate. Its analysis is the proof of Theorem 1.3.

Algorithm 4 line 4 adds unbounded two-sided Laplace noise and contains no clipping. Algorithm 5 line 3 accepts the returned value and uses it to calibrate later Laplace noise. Definition 2.5 defines `Lap(b)` with density \(e^{-|x|/b}/(2b)\), which is a probability density only for positive \(b\).

For an empty three-vertex graph and 2-star pattern, \(f_H^{(2)}(G)=1\) and \(f_H^{(1)}(G)=0\). Thus Algorithm 4 returns
\[
\ln(1/\delta')/\varepsilon' + \operatorname{Lap}(1/\varepsilon').
\]
It is negative with exact probability \(\delta'/2>0\). This input satisfies the graph, pattern, privacy-parameter, dimension, and query assumptions.
