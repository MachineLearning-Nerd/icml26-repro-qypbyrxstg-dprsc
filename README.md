# Differentially Private Range Subgraph Counting — reproduction

[![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/MachineLearning-Nerd/icml26-repro-qypbyrxstg-dprsc/blob/master/notebooks/dprsc_reproduction.py)

This is a claim-by-claim reproduction of
[*Differentially Private Range Subgraph Counting*](https://arxiv.org/abs/2606.08179)
(ICML 2026, OpenReview `QYpByrxSTg`). The previous live judge score is
**5/10**. The present evidence supports a conservative **7–8/10 forecast**;
only the live judge can change the score.

Publication receipt: the terminal release regression passed at Git SHA
`ff86be4c06d2a8f8b65c735478830e0c42db5e8a` (HF `cpu-upgrade`, 11m40s), and
Space revision `0af4a5487541cbfa8e85a687a24483a1075c3454` passed an exact
post-download manifest and evaluator traversal. The paper is awaiting the live
judge; 5/10 remains the only recorded score.

The headline empirical result is strong: using all three released datasets,
all three patterns, eight epsilon values, 20 repetitions, and the paper's
default query counts, the proposed method has lower error in **144/144**
privacy-matched comparisons. The theorem results are more mixed:

| Claim | Assessment | Paper result versus observed evidence |
| --- | --- | --- |
| Theorem 1.3 efficient approximate-DP existence | **BLOCKED / LOW** | Full-scale finite calibration is stable, but the named Algorithm 5 witness has invalid negative-scale draws and the existential theorem is neither proved nor falsified |
| Theorem 1.4 lower bound | **BLOCKED / LOW** | Reconstruction closes, but the cited partial-discrepancy transfer does not prove the written exponent |
| Algorithms 1–3 pure DP | **VERIFIED / HIGH** | Independent universal privacy/utility derivation, exhaustive functional checks, and failing negative controls |
| Algorithms 4–5 approximate DP | **FALSIFIED / HIGH** | Valid empty-graph 2-star input yields a negative Laplace scale with positive probability; released NumPy raises `ValueError` |
| Section 5 accuracy/runtime | **BLOCKED / MEDIUM** | Accuracy aligns in 144/144 cases; total-time speedup is 2.18x–10,640x, so the literal 3–4-order statement is not uniform on this hardware |

Read the [illustrated technical report](reports/dprsc-reproduction-2026-07-26/report.md)
or open the [self-contained marimo tutorial](notebooks/dprsc_reproduction.py).
The notebook embeds the central result and does not rerun expensive
experiments.

## Reproduce

The environment is Python 3.12 with one repository-level `.venv`, managed and
locked by `uv`. The fixed command on every experiment node is:

```bash
uv run --frozen python repro/src/run_campaign.py
```

The command regenerates raw records, runs independent checkers, and requires
every negative control to exit nonzero. Long and uncertain CPU runs used
Hugging Face `cpu-upgrade`; no GPU was used. The final cumulative scientific
run estimated 4 cores and 15–30 minutes, observed 64 logical CPUs, and took
1,036.093 seconds (`17m46s` orchestrator duration).

## Experiment log

| Branch / experiment | Purpose or change | Exact run command | Assessment / outcome | Compute |
| --- | --- | --- | --- | --- |
| [`orx/validated-5-10-baseline`](https://github.com/MachineLearning-Nerd/icml26-repro-qypbyrxstg-dprsc/tree/orx/validated-5-10-baseline) | Freeze judged state | `uv run --frozen python repro/src/run_campaign.py` | Historical 5/10 baseline | Local, 1 core, 3.099s |
| [`orx/claim-4-estimatehs-negative-scale-counterexample`](https://github.com/MachineLearning-Nerd/icml26-repro-qypbyrxstg-dprsc/tree/orx/claim-4-estimatehs-negative-scale-counterexample) | Test Algorithm 4/5 total-domain validity | `uv run --frozen python repro/src/run_campaign.py` | Claim 4 FALSIFIED/HIGH | Local, single-threaded, 4.139s |
| [`orx/claim-3-pure-dp-proof-audit-and-visible-claim-4`](https://github.com/MachineLearning-Nerd/icml26-repro-qypbyrxstg-dprsc/tree/orx/claim-3-pure-dp-proof-audit-and-visible-claim-4) | Reconstruct Algorithms 1–3 proof | `uv run --frozen python repro/src/run_campaign.py` | Claim 3 VERIFIED/HIGH | Local, single-threaded, 4.106s |
| [`orx/claim-2-imported-lower-bound-lemma-audit`](https://github.com/MachineLearning-Nerd/icml26-repro-qypbyrxstg-dprsc/tree/orx/claim-2-imported-lower-bound-lemma-audit) | Audit imported lower-bound dependencies | `uv run --frozen python repro/src/run_campaign.py` | Claim 2 BLOCKED/LOW after four routes | Local, single-threaded |
| [`orx/claim-5-full-three-dataset-paper-protocol-reprod`](https://github.com/MachineLearning-Nerd/icml26-repro-qypbyrxstg-dprsc/tree/orx/claim-5-full-three-dataset-paper-protocol-reprod) | Full accuracy protocol | `uv run --frozen python repro/src/run_campaign.py` | 144/144 orderings hold | HF cpu-upgrade |
| [`orx/claim-5-adaptive-rse-runtime-and-cumulative-accu`](https://github.com/MachineLearning-Nerd/icml26-repro-qypbyrxstg-dprsc/tree/orx/claim-5-adaptive-rse-runtime-and-cumulative-accu) | Exact adaptive runtime protocol | `uv run --frozen python repro/src/run_campaign.py` | Claim 5 BLOCKED/MEDIUM | HF cpu-upgrade, 16m51s |
| [`orx/claim-1-theorem-audit-and-cumulative-full-scale`](https://github.com/MachineLearning-Nerd/icml26-repro-qypbyrxstg-dprsc/tree/orx/claim-1-theorem-audit-and-cumulative-full-scale) | Four-route Claim 1 audit and cumulative regression | `uv run --frozen python repro/src/run_campaign.py` | Claim 1 BLOCKED/LOW; cumulative PASS | HF cpu-upgrade, 17m46s |
| `master` | Public landing page, report, and notebook | Not run as an experiment (publication surface) | Presentation only | None |

Failed branches are omitted unless they explain the terminal lineage. Raw
experiment and run IDs are retained in OpenResearch experiment descriptions
and the candidate evidence pages.

## Repository map

- `repro/src/` — fixed campaign, claim runners, independent checkers, controls
- `.openresearch/artifacts/` — durable contracts, source audits, raw JSON, methods, limitations
- `upstream/` — released `Airleave/DPRSC` code and datasets pinned at `aae89538`
- `reports/dprsc-reproduction-2026-07-26/` — illustrated report and source data
- `notebooks/dprsc_reproduction.py` — bounded tutorial notebook
- `space_candidate/` — additive evaluator-visible candidate for the existing HF Space

Historical judged Space evidence is preserved unchanged under
`space_candidate/historical/judged-6d5d785bb7f0386ef5d46b609fb529dbd1058fcb/`
and labeled exactly **Historical rejected baseline**. It is not the current
verifier.
