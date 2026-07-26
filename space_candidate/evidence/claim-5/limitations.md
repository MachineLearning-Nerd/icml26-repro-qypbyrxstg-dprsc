# Claim 5 limitations and deviations

- Accuracy is direct full-protocol evidence, but the paper publishes figures
  rather than machine-readable numeric targets. The faithful test is the
  stated proposed-versus-baseline ordering, not pixel-level agreement.
- Runtime at Theta(n^2) is extrapolated from query-time samples, as in the
  paper. It does not time hundreds of millions of queries exhaustively.
- The released code and datasets are exact, but our hardware differs from the
  reported Intel Xeon Platinum 8562Y/768 GB machine, and the paper omits raw
  timing samples plus OS/Python/dependency/threading details. This is material:
  the literal 3–4-order runtime statement is not uniform on this hardware.
- CA-Netscience is only 2.18x–6.28x faster at the full distinct-query domain;
  Wiki-Squirrel is 623x–2,430x; WormNet-v3 is 2,742x–10,640x. Therefore the
  paper's actual runtime observation remains BLOCKED, not upgraded on trend
  alone.
- A runtime difference on unmatched hardware is not an assumption-satisfying
  falsification of the paper's reported observations.
- The `FALSIFIED` verdict applies only to the exact evaluator-anchored
  source-attribution sentence. It must not be read as falsifying the paper's
  actual accuracy ordering or runtime observation.
