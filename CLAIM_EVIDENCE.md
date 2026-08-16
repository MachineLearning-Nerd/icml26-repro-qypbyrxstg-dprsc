# Claim-to-evidence map

This document records what each paper claim says, how the repository produces
evidence for it, and where the inference stops. The status labels are
conservative:

- VERIFIED_SCOPED means the declared finite or formal audit passed.
- FALSIFIED means the written proposition or released construction has a valid
  counterexample in the declared scope.
- BLOCKED means the available evidence does not discharge the claim and did
  not produce an assumption-satisfying counterexample.

## C1 — Theorem 1.3: efficient approximate-DP existence

### Contract

For every epsilon greater than zero, delta in (0, 1), fixed pattern H, and
arbitrary query set Q, the paper states existence of an (epsilon, delta)-DP
algorithm with a high-probability maximum absolute error bound involving the
estimated hereditary sensitivity, the dimension, and the query set. It also
states polynomial efficiency in the low-dimensional regime.

### Production path

run_claim1_theorem_audit.py produces the four-route audit and
verify_claim1_theorem_audit.py checks the contract and controls. The relevant
evidence is:

- space_candidate/evidence/claim-1/theorem_audit_run.json
- space_candidate/evidence/claim-1/claim_contract.json
- space_candidate/evidence/claim-1/method.md
- space_candidate/evidence/claim-1/limitations.md
- space_candidate/evidence/claim-1/source_audit.md

### Result

BLOCKED / LOW.

The symbolic route checks 192 proof-chain obligations conditional on a finite
positive EstimateHS. The finite route covers three datasets, three patterns,
eight epsilon values, and 20 repetitions, but it is finite calibration only.
The repair and primary-literature route does not establish the missing
same-scope theorem. The falsification route finds no counterexample satisfying
the existential theorem's quantifiers.

The important failure mode is narrower: Lemma E.4 can leave EstimateHS
negative on a positive-probability event, while the subsequent construction
uses it as a Laplace scale. That makes the named witness undefined there. It
does not logically falsify a separate existential statement.

## C2 — Theorem 1.4: dimension-dependent lower bound

### Contract

For every pattern H and every (epsilon, delta)-DP mechanism, with constant
epsilon greater than zero, delta in [0, 1/2), sufficiently large constant
success probability, and query sets of size at least n^c for sufficiently
small constant c, the theorem claims a maximum-absolute-error lower bound for
infinitely many n. Its regimes are:

- d = O(1): Omega(log^(d-1)(n) * HStilde_fH(G))
- d = O(log n): 2^Omega(d) * HStilde_fH(G)
- d = Omega(log n): n^Omega(1) * HStilde_fH(G)

The theorem is written in terms of HStilde, not GS. GS is only a
constructed-instance comparison and must not be substituted into the claim.

### Production path

The primary and independent routes are:

- repro/src/verify_claim2_dependency_audit.py
- repro/src/verify_claim2_dependency_independent.py
- repro/src/verify_lower_bound.py
- repro/src/verify_universal_lower_bound.py
- docs/claim2_lower_bound_proof_audit.md

Durable outputs include
space_candidate/evidence/claim-2/dependency_audit_run.json,
outputs/c2_proof_certificate.json, and
outputs/c2_universal_smt_certificate.json.

### Result

BLOCKED / LOW.

The DP reconstruction lemma is independently discharged. The finite
four-point certificate also passes 4,608 count identities, 528 reconstruction
checks, and 64 neighbor checks. The blocking gap is Appendix D: its
partial-coloring recursion has Theta(log n) scales, but the written inference
treats the per-scale little-o term as though summing it preserved the same
exponent. The pinned primary sources establish standard or hereditary
discrepancy, not the exact partial-discrepancy statement required by the
paper's Lemma 4.3. No valid assumption-satisfying counterexample was found.

## C3 — Theorem 3.3 and Algorithms 1–3: pure DP

### Contract

The paper's projection, range-tree construction, and pure-DP release
(Proj -> TreeConst -> PDP_RSC) should satisfy pure epsilon-DP and the stated
high-probability maximum-error utility order.

### Production path

- repro/src/verify_claim3_pure_dp.py
- repro/src/verify_claim3_pure_dp_independent.py
- space_candidate/evidence/claim-3/formal_run.json
- space_candidate/evidence/claim-3/pure_dp_certificate_run.json
- space_candidate/evidence/claim-3/proof_certificate.md

### Result

VERIFIED_SCOPED / HIGH.

The analytic certificate and independent checker pass. The run records 9,216
projection identities, 9,216 neighboring sensitivity checks, 1,296
tied-attribute checks, and 3,393 high-precision inequalities. The
average-for-maximum, naive-tie, and under-noised controls all exit with code
2, as required. This is a formal and finite audit of the stated proof path,
not a claim that every possible implementation is correct.

## C4 — Algorithms 4–5: approximate DP

### Contract

The higher-order sensitivity estimator EstimateHS, approximate-DP release
ADP_RSC, and its range-tree queries should define the claimed
(epsilon, delta)-DP mechanism and utility guarantee.

### Production path

- repro/src/verify_claim4_counterexample.py
- repro/src/verify_claim4_counterexample_independent.py
- space_candidate/evidence/claim-4/counterexample.json
- space_candidate/evidence/claim-4/counterexample_run.json

### Result

FALSIFIED / HIGH.

On an empty three-vertex graph with a 2-star pattern, one-dimensional
full-range query, and released Algorithm 4/5 code, EstimateHS is negative with
positive probability. The released NumPy path then raises ValueError when
asked to use that value as a Laplace scale. The formal run records
negative-event probability 4.005510341651234e-7, independent and primary
passes, and the exception. A separate calibration at epsilon 2, delta 0.9,
and n 100 records probability 0.0360495930748611, greater than the stated
failure budget 0.01.

This verdict is about the released construction as written. It is not used to
turn C1's existential theorem into a falsification.

## C5 — Section 5 evidence, split by meaning

The original evaluator sentence combines source attribution, accuracy, and
runtime. This repository keeps them separate.

### C5a — anchored source attribution

The exact proposition says the paper reports 3–4 orders of magnitude in
accuracy at query-set size Theta(n^2). The pinned HTML source instead gives
ceil(n^1.5) as the default accuracy budget and places the 3–4-order and
Theta(n^2) statements in the Runtime scope.

Production:

- repro/src/verify_claim5_source.py
- repro/src/verify_claim5_source_independent.py
- space_candidate/evidence/claim-5/source_verifier_run.json
- space_candidate/evidence/claim-5/source_independent_run.json
- space_candidate/evidence/claim-5/source_control_accept-misattribution.json
- space_candidate/evidence/claim-5/source_control_conflate-query-budgets.json

Result: FALSIFIED / HIGH. Both negative controls fail as expected when the
misattribution is accepted.

### C5b — actual runtime observation

The empirical runtime protocol samples distinct uniform intervals until
relative standard error is below 5%, then extrapolates total time to the full
distinct-query domain. All streams meet the RSE target. Mean speedups range
from 2.18x to 10,640x, with conservative lower values from 1.80x to 8,785x.
The paper reports an Intel Xeon Platinum 8562Y at 2.80 GHz with 768 GB RAM;
the reproduction environment does not match that machine or a complete
software environment.

Result: BLOCKED / MEDIUM. The run is useful scoped evidence, not a valid
hardware-independent historical falsification or exact replication.

### C5 accuracy subclaim

The full paper-default accuracy protocol uses all three released datasets,
three patterns, eight epsilon values, and 20 repetitions. Proposed methods
beat their corresponding composition baselines in 144/144 comparisons. This
supports the empirical ordering only; it does not prove C1 or C3.

## Evidence discipline

The root claims.json records the normalized status. The raw JSON files, source
hashes, reports, and branch-specific history remain the authoritative audit
trail. verify_final.py checks that the root summary and those artifacts cannot
silently drift apart.
