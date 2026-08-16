# Status — Differentially Private Range Subgraph Counting

Last updated: 2026-08-16

## Collection state

MIXED_SCOPED: the paper's released empirical ordering is reproduced in a
declared finite protocol, one pure-DP theorem is verified within that audit
scope, one approximate-DP construction is falsified as written, and two
asymptotic/theorem-level claims remain blocked.

The evidence bundle records a historical live evaluator score of 4/10 at Space
revision adf4e474c3afe562e54e0bfd1534e1323f0c5783. This repository makes no
new score claim.

## Claim ledger

| ID | Verdict | Why |
| --- | --- | --- |
| C1 | BLOCKED / LOW | Finite calibration cannot discharge the asymptotic existence theorem; the named Algorithm 5 witness is not total on a positive-probability event |
| C2 | BLOCKED / LOW | Reconstruction and finite certificates pass, but the partial-discrepancy recursion does not preserve the written exponent |
| C3 | VERIFIED_SCOPED / HIGH | Pure-DP proof chain and independent finite checks pass; three negative controls fail as intended |
| C4 | FALSIFIED / HIGH | A valid empty-graph 2-star input gives a negative Laplace scale and a released-code ValueError |
| C5a | FALSIFIED / HIGH | The pinned source does not make the evaluator-anchored accuracy attribution |
| C5b | BLOCKED / MEDIUM | Runtime evidence is hardware-mismatched, although all adaptive streams meet the RSE target |
| C5 accuracy | VERIFIED_SCOPED | Proposed methods beat their corresponding composition baselines in 144/144 comparisons |

## Reproduction gate

The exact entry point is:

~~~bash
uv run --frozen python repro/src/run_campaign.py
~~~

verify_final.py is a fail-closed publication check. It validates the repository
documents, evidence contracts, pinned artifacts, final branch vocabulary,
canonical commit attribution, and absence of legacy orx/* and master refs.

## Scope limits

- The theorem audits are not substitutes for a peer-reviewed proof.
- The finite accuracy result does not prove an asymptotic utility theorem.
- The C4 counterexample targets the released approximate-DP construction; it
  does not by itself falsify the existential C1 statement.
- Runtime is reported as scoped evidence, not as a hardware-independent
  historical replication.
- No author endorsement, competition-score increase, or later-version
  equivalence is claimed.
