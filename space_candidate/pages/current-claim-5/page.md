# Current verification — Claim 5

**Anchored claim verdict: FALSIFIED. Confidence: HIGH.** The exact evaluator
claim is a source attribution: it says Section 5 reports 3–4 orders of
magnitude in *accuracy* at \(\Theta(n^2)\). The complete pinned section instead
assigns the default accuracy protocol \(\lceil n^{1.5}\rceil\), while both the
magnitude and \(\Theta(n^2)\) occur under Runtime. This page supersedes the
historical Claim 3 accuracy page.

**Actual paper runtime claim: BLOCKED. Confidence: MEDIUM.** The separate,
paper-faithful timing reproduction is hardware-dependent and is not treated as
an assumption-matched falsification.

## What the paper actually claims

Source: *Differentially Private Range Subgraph Counting*, arXiv:2606.08179, [archived HTML](evidence/claim-5/source/2606.08179.html), retrieved `2026-07-25T06:41:27Z`.

SHA-256: `9387c720239542f024ef31654e84ced6e2687818f8f17703945aa114aab02a5b`

At Section 5 anchors `S5.p3` and `S5.p6`:

| Protocol | Exact source scope |
| --- | --- |
| Accuracy | \(\varepsilon=2\), \(\delta=10^{-5}\), \(d=1\), \(|Q|=\lceil n^{1.5}\rceil\) by default, mean relative error, at least 20 independent runs |
| Runtime | \(|Q|\) ranges from 1 to \(\Theta(n^2)\); query times are sampled until relative standard error is below 5%, then total time is extrapolated |
| 3–4 orders | Lower query latency and extrapolated total-time speedup at \(\Theta(n^2)\), not accuracy |
| Reported hardware | Intel Xeon Platinum 8562Y at 2.80 GHz with 768 GB RAM; raw timings and complete software environment are not published |
| Domain | Wiki-Squirrel (5,201/198,353), WormNet-v3 (16,347/762,822), CA-Netscience (379/914); triangle, 2-star, and edge |

The exact anchored claim says “are reported,” so its domain is the complete
finite content of the hash-pinned Section 5. The primary verifier checks raw
anchors and ordering; an **independent source checker** uses Python's
`HTMLParser` to reconstruct semantic text. Both conclude that the attribution
is false. Two controls—accepting the misattribution and conflating the two
query budgets—exit nonzero.

## Full accuracy result

The exact released graphs, attributes, algorithms, privacy matching, at least
20 repetitions, and paper-default query counts were used. All **144/144**
pairwise orderings hold across 3 datasets × 3 patterns × 8 epsilon values ×
2 privacy regimes.

At the paper default \(\varepsilon=2\):

| Dataset / pattern | PDP_RSC | PDP_Comp | ADP_RSC | ADP_Comp |
| --- | ---: | ---: | ---: | ---: |
| CA / edge | 0.580027 | 6.654207 | 0.503825 | 0.741597 |
| CA / 2-star | 40.235248 | 467.965440 | 25.250186 | 37.706829 |
| CA / triangle | 290.829430 | 3386.851416 | 2408.085135 | 3928.810545 |
| Wiki / edge | 0.005220 | 1.206435 | 0.003855 | 0.018917 |
| Wiki / 2-star | 0.074014 | 17.130047 | 0.131410 | 0.646151 |
| Wiki / triangle | 0.617721 | 142.936833 | 0.817817 | 4.110057 |
| Worm / edge | 0.001890 | 1.668784 | 0.001169 | 0.011080 |
| Worm / 2-star | 0.115651 | 102.236264 | 0.033497 | 0.318046 |
| Worm / triangle | 1.722583 | 1522.760634 | 0.512518 | 4.720184 |

Query counts are exactly `7,379`, `375,086`, and `2,090,053`; every cell is a
20-repeat mean relative error. The epsilon-2 baseline/proposed ratios span
`11.47x`–`884.01x` for pure DP and `1.47x`–`9.49x` for approximate DP.

## Runtime result

Every adaptive timing stream reached RSE below 5%. Exact i.i.d. uniform
distinct intervals, released `range_tree.querySplit`, and exact
filtering/counting baselines were used.

| Dataset / pattern | Query-latency speedup | Total speedup at full distinct Theta(n²) | Conservative 95% lower |
| --- | ---: | ---: | ---: |
| CA / edge | 2.20x | 2.18x | 1.80x |
| CA / 2-star | 4.35x | 4.31x | 3.57x |
| CA / triangle | 6.34x | 6.28x | 5.19x |
| Wiki / edge | 631x | 623x | 515x |
| Wiki / 2-star | 640x | 632x | 523x |
| Wiki / triangle | 2,462x | 2,430x | 2,003x |
| Worm / edge | 2,748x | 2,742x | 2,275x |
| Worm / 2-star | 3,063x | 3,056x | 2,533x |
| Worm / triangle | 10,665x | 10,640x | 8,785x |

The trend and large-graph crossover align with the paper. The exact 3–4-order
runtime wording does not hold uniformly. Different, insufficiently specified
hardware and absent raw timing samples prevent treating this as a valid
falsification of the paper's observed timing, so that separate actual paper
claim remains BLOCKED.

## Reproduce and inspect

- [Exact claim contract](evidence/claim-5/claim_contract.json)
- [Source audit](evidence/claim-5/source_audit.md)
- [Primary verifier](evidence/claim-5/verify_claim5_source.py)
- [Independent source checker](evidence/claim-5/verify_claim5_source_independent.py)
- [Primary verifier output](evidence/claim-5/source_verifier_run.json)
- [Independent checker output](evidence/claim-5/source_independent_run.json)
- [Misattribution control output](evidence/claim-5/source_control_accept-misattribution.json)
- [Budget-conflation control output](evidence/claim-5/source_control_conflate-query-budgets.json)
- [Raw source facts](evidence/claim-5/raw_source_facts.json)
- [Raw cumulative accuracy JSON](evidence/claim-5/cumulative_accuracy_run.json)
- [Raw cumulative runtime JSON](evidence/claim-5/cumulative_runtime_run.json)
- [Accuracy runner](evidence/reproduction/repro/src/run_claim5_accuracy.py)
- [Accuracy checker](evidence/reproduction/repro/src/verify_claim5_accuracy.py)
- [Runtime runner](evidence/reproduction/repro/src/run_claim5_runtime.py)
- [Runtime checker](evidence/reproduction/repro/src/verify_claim5_runtime.py)
- [Released range-tree implementation](evidence/reproduction/upstream/range_tree.py)
- [Released algorithms](evidence/reproduction/upstream/ourAlg.py)
- [Released baselines](evidence/reproduction/upstream/baseline.py)
- [Locked environment](evidence/reproduction/uv.lock)
- [Fixed command entrypoint](evidence/reproduction/repro/src/run_campaign.py)
- [Method](evidence/claim-5/method.md)
- [Limitations](evidence/claim-5/limitations.md)

Fixed command:

```bash
uv run --frozen python repro/src/run_campaign.py
```

Successful cumulative run `a222c714-1f0c-4d05-881e-a7d1b85dac74` at source
Git SHA `c4cb4544392008732b669b626de6b2c4c8867342`; HF `cpu-upgrade`; estimated
4 cores and 15–30 minutes; 64 logical CPUs exposed; scientific suite
`635.455 s`; orchestrator `10m53s`. The source test is deterministic; seeds
are embedded in both empirical raw records.
The two source-attribution controls, query-budget control, and biased-sampler
control exit nonzero.
