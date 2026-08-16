# Differentially Private Range Subgraph Counting

Paper-first reproduction and claim audit for the ICML 2026 paper
[*Differentially Private Range Subgraph Counting*](https://arxiv.org/abs/2606.08179).
The challenge record is [QYpByrxSTg](https://openreview.net/forum?id=QYpByrxSTg).

This repository was previously named
icml26-repro-qypbyrxstg-dprsc. The normalized home is
MachineLearning-Nerd/icml26-differentially-private-range-subgraph-counting.

## What the paper does

The paper studies private range-subgraph counting. Each vertex has public
attributes, a query selects vertices inside a multidimensional range, and the
mechanism counts fixed patterns such as edges, 2-stars, and triangles in the
induced subgraph. Its main construction projects each pattern occurrence onto
attribute ranks, releases a noisy range-tree representation once, and answers
many range queries by post-processing canonical tree nodes. The paper also
proposes a higher-order local-sensitivity estimator for approximate
differential privacy and gives a dimension-dependent lower bound.

The released implementation is vendored under upstream/ at
Airleave/DPRSC@aae89538544bddb1bc89961453f3cd6b6091de19. The reproduction entry
point is repro/src/run_campaign.py.

## Current scientific status

The evidence is deliberately mixed. A finite experiment is not presented as
an asymptotic theorem proof, and a defect in a named construction is not
silently promoted to a refutation of a separate existential theorem.

| Claim | Scope | Verdict | Main evidence |
| --- | --- | --- | --- |
| C1 — Theorem 1.3 approximate-DP existence and utility | Exact theorem quantifiers | BLOCKED / LOW | Four audit routes; finite calibration corroborates only a finite scope, while the named Algorithm 5 witness can use a negative scale |
| C2 — Theorem 1.4 dimension-dependent lower bound | Maximum absolute error and all stated regimes | BLOCKED / LOW | DP reconstruction closes, but the Appendix D partial-discrepancy recursion does not establish the written exponent |
| C3 — Theorem 3.3 and Algorithms 1–3 | Pure-DP mechanism and utility bound | VERIFIED_SCOPED / HIGH | Analytic certificate, 9,216 projection checks, 9,216 sensitivity checks, 1,296 tied-attribute checks, 3,393 precision checks, and failing negative controls |
| C4 — Algorithms 4–5 | Approximate-DP construction | FALSIFIED / HIGH | Empty-graph 2-star counterexample produces a negative Laplace scale; released NumPy raises ValueError |
| C5a — evaluator-anchored source attribution | Exact sentence about accuracy, query budget, and 3–4 orders | FALSIFIED / HIGH | The pinned Section 5 source assigns ceil(n^1.5) to default accuracy and assigns the 3–4-order and Theta(n^2) statements to Runtime |
| C5b — actual runtime observation | Historical hardware-dependent runtime result | BLOCKED / MEDIUM | Timing protocol reaches RSE below 5%, but hardware and full environment are not matched |

The complete accuracy protocol preserves the paper's proposed-versus-baseline
ordering in 144/144 privacy-matched comparisons. At epsilon 2, the pure-DP
ratios range from 11.47x to 884.01x and the approximate-DP ratios from 1.47x
to 9.49x. Runtime speedups at the extrapolated full query domain range from
2.18x to 10,640x; that range does not justify a uniform paper-level runtime
claim on unmatched hardware.

The repository records a historical live judge score of 4/10 at Space revision
adf4e474c3afe562e54e0bfd1534e1323f0c5783. No new judge score or author
endorsement is claimed here.

The full reasoning, exact quantifiers, controls, and limitations are in
[CLAIM_EVIDENCE.md](CLAIM_EVIDENCE.md) and the
[illustrated technical report](reports/dprsc-reproduction-2026-07-26/report.md).

## How each claim is produced

The fixed campaign is intentionally small and auditable:

~~~text
find_patterns.py -> ourAlg.py -> range_tree.py::querySplit
                         \-> baseline.py for composition baselines
run_campaign.py -> claim runners -> independent checkers -> JSON evidence
~~~

| Claim | Production path | Durable evidence |
| --- | --- | --- |
| C1 | repro/src/run_claim1_theorem_audit.py and verify_claim1_theorem_audit.py | space_candidate/evidence/claim-1/theorem_audit_run.json, method, limitations, and source audit |
| C2 | repro/src/verify_claim2_dependency_audit.py, verify_claim2_dependency_independent.py, and the two lower-bound verifiers | space_candidate/evidence/claim-2/dependency_audit_run.json, outputs/c2_proof_certificate.json, and outputs/c2_universal_smt_certificate.json |
| C3 | repro/src/verify_claim3_pure_dp.py and verify_claim3_pure_dp_independent.py | space_candidate/evidence/claim-3/formal_run.json and pure_dp_certificate_run.json |
| C4 | repro/src/verify_claim4_counterexample.py and its independent checker | space_candidate/evidence/claim-4/counterexample_run.json and counterexample.json |
| C5a | repro/src/verify_claim5_source.py plus the independent source checker | space_candidate/evidence/claim-5/source_verifier_run.json and source_independent_run.json |
| C5b | repro/src/run_claim5_runtime.py and verify_claim5_runtime.py | space_candidate/evidence/claim-5/cumulative_runtime_run.json, raw timing summaries, and the report |
| C5 accuracy | repro/src/run_claim5_accuracy.py and verify_claim5_accuracy.py | space_candidate/evidence/claim-5/cumulative_accuracy_run.json and accuracy tables |

Every claim has a machine-readable contract in the corresponding
space_candidate/evidence/claim-* directory. claims.json is the concise
repository-level ledger; it does not replace the raw artifacts.

## Reproduce

Requirements are Python 3.12 and uv. The lockfile is authoritative.

~~~bash
uv run --frozen python repro/src/run_campaign.py
~~~

The command regenerates the campaign records and runs the independent
checkers. Short proof and counterexample checks run single-threaded on CPU.
The larger accuracy and runtime protocols used a CPU-only environment; no GPU
result is claimed.

Dataset snapshots bundled by the official code are:

- CA-Netscience: 379 vertices, 914 edges
- Wiki-Squirrel: 5,201 vertices, 198,353 edges
- WormNet-v3: 16,347 vertices, 762,822 edges

Accuracy uses ceil(n^1.5) queries, eight epsilon values, and 20 repetitions.
Runtime samples distinct uniform intervals until relative standard error is
below 5%, then reports the paper-style extrapolation to the full query domain.
See [ENVIRONMENT.md](ENVIRONMENT.md) for the exact boundary and limitations.

## Repository map

- repro/src/ — fixed campaign, claim runners, independent checkers, and controls
- space_candidate/evidence/ — evaluator-visible contracts and run records
- outputs/ — lower-bound certificates and experiment tables
- upstream/ — pinned author code and datasets
- reports/dprsc-reproduction-2026-07-26/ — narrative report and figures
- notebooks/dprsc_reproduction.py — bounded, non-expensive tutorial
- paper_2606.08179v1.pdf and source/arxiv/2606.08179v1.tar — pinned paper artifacts

## Branches

The final public branch vocabulary is descriptive. The old orx/* names are
mapped in [BRANCH_AUDIT.md](BRANCH_AUDIT.md).

| Branch | Purpose |
| --- | --- |
| main | Publication surface and integrated documentation |
| baseline/validated-5-10 | Historical judged baseline |
| audit/claim-1-theorem | Four-route Theorem 1.3 audit |
| audit/claim-2-lower-bound | Theorem 1.4 dependency and exponent audit |
| audit/claim-3-pure-dp | Pure-DP Algorithms 1–3 proof reconstruction |
| audit/claim-4-negative-scale | Algorithm 4/5 negative-scale counterexample |
| audit/claim-5-runtime | Adaptive runtime and cumulative timing protocol |
| audit/claim-5-source-attribution | Exact source-content attribution contract |
| audit/claim-5-accuracy | Full three-dataset accuracy protocol |
| audit/exact-source-contracts | Source and claim contract packaging |
| audit/five-claim-contracts | Integrated five-claim evidence ledger |
| release/evaluator-visible | Evaluator-facing cumulative release |

## Source and version boundary

The audit pins arXiv v1, its source archive, the rendered HTML used for the
Claim 5 source contract, and the released author code. The repository does not
claim that later paper revisions, unpinned author changes, or unavailable
hardware would produce identical numbers. Hashes and retrieval details are in
[SOURCE_AUDIT.md](SOURCE_AUDIT.md).

## Citation

If this repository or its audit artifacts are useful, please cite the paper
and the reproduction record. A ready-to-use CFF file is in
[CITATION.cff](CITATION.cff).

~~~bibtex
@misc{chen2026differentially,
  title         = {Differentially Private Range Subgraph Counting},
  author        = {Chen, Xian and Bai, Ruobing and Peng, Pan},
  year          = {2026},
  eprint        = {2606.08179},
  archivePrefix = {arXiv},
  primaryClass  = {cs.DS},
  note          = {ICML 2026}
}
~~~

## Thank you

Thank you to Xian Chen, Ruobing Bai, and Pan Peng for making the paper,
implementation, and data snapshots available. The audit is intended to make
the evidence easier to inspect and reproduce; it is independent work and
should not be read as an endorsement by the authors.

See [AUTHOR_THANK_YOU.md](AUTHOR_THANK_YOU.md) for the full note.
