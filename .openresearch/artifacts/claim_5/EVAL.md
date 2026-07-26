# Claim 5 evaluator checklist

Current verdict: **BLOCKED**. Confidence: **MEDIUM**.

The paper-faithful accuracy reproduction now covers Wiki-Squirrel,
WormNet-v3, and CA-Netscience; edge, 2-star, and triangle; eight epsilon
values; 20 deterministic repetitions; and the paper-default
`ceil(n^1.5)` query budget. All 144 privacy-matched
proposed-versus-baseline orderings hold.

The runtime reproduction samples exact i.i.d. uniform distinct intervals,
uses the released `range_tree.querySplit`, samples the exact filtering/counting
baselines until RSE is below 5%, and extrapolates to the full distinct-query
Theta(n^2) domain. All nine sampling comparisons reach the stop rule.

The exact 3–4-order wording is not uniformly reproduced: mean total-time
speedups range from 2.18x to 10,640x, with conservative 95% lower values from
1.80x to 8,785x. Because runtime is hardware-dependent and the paper does not
publish a sufficient environment specification for an assumption-matched
counterexample, the result is BLOCKED rather than FALSIFIED.

Canonical page: `space_candidate/pages/current-claim-5/page.md`. Raw cumulative
records, executable primary and independent checkers, source snapshot, locked
environment, negative-control output, exact command, seeds, and compute/runtime
metadata are linked there. Historical judged pages remain reachable and are
explicitly labeled “Historical rejected baseline.”
