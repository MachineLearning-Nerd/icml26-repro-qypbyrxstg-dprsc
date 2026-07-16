# STATUS — DPRSC (QYpByrxSTg) reproduction

**Paper:** *Differentially Private Range Subgraph Counting* — Xian Chen, Ruobing Bai, Pan Peng.
OpenReview `QYpByrxSTg` · arXiv 2606.08179 · official code `Airleave/DPRSC` (cloned @ `aae89538`, unmodified; pure-Python, numpy/pandas/matplotlib, no GPU).
Session: autoloop. Last updated 2026-07-16.

## Official claims (judge scores these)
1. First efficient algorithms for DP range subgraph counting with small additive error. **(empirical ✓)**
2. Proves any DP algorithm incurs additive error exponential in the dimension. **(theorem — not empirically reproducible; document, skip)**
3. Algorithms significantly outperform baselines in accuracy while maintaining strong privacy guarantees. **(empirical ✓)**

## Method
Run the authors' `implement_epsilon_test` (DP additive error vs ε ∈ {0.5…4.0} for patterns triangle/edge/2star; ours = `pure_DP`, `approx_DP` vs baselines `base_comp`, `base_comp_ADP`) and `query_time_test` (per-query latency) on the bundled datasets. Compare ours vs baselines — C3 is the error ordering, C1 the small absolute error + the algorithms running at scale. DP noise is the code's own Laplace mechanism, averaged over `Q_num × repeat_times` queries.

Runner: `repro/src/run_dprsc.py` (calls upstream fns directly, caps workers to 4, copies CSVs to `outputs/`). Smoke = ca-netscience (n=379); paper-scale = musae-squirrel (n=5201), bio-WormNet-v3 (n=16347, heaviest).

## Results so far — ca-netscience (n=379) SMOKE ✓
- **Accuracy (C3):** `triangle` and `edge` — `pure_DP` & `approx_DP` error ≪ `base_comp` at **all ε** (e.g. triangle ε=2.0: ours 22–32 vs base_comp 464; edge ε=2.0: ours 0.4–0.6 vs 6.6). **C3 verified for 2/3 patterns cleanly.** `2star`: `pure_DP` ≪ base_comp ✓, but `approx_DP` has high error on this tiny graph (likely small-n artifact — musae-squirrel will confirm; the paper's real graphs are 14–43× larger).
- **Latency:** ours ~67–70 µs/query vs baselines ~1.0–1.6 ms → **~15–23× faster** (paper claims 3–4 orders of magnitude on the larger graphs).

## CURRENT STEP
musae-squirrel (n=5201, paper-scale) epsilon+qtime running in the background. ca-netscience CSVs + figures in `outputs/`.

## NEXT (resume here)
1. When musae-squirrel finishes: verify C3 (ours < baselines) across all 3 patterns; expect the 2star approx_DP anomaly to shrink/disappear at scale; record latency gap (expect larger, toward 3–4 orders).
2. Independent verification: re-run (DP noise is randomized → check the ordering is stable across re-runs); negative-control sanity (baselines must NOT beat ours on triangle/edge).
3. Logbook: Trackio pages per claim (C1, C3; C2 = theorem note), embed accuracy + latency CSVs/figures.
4. **Publish gate** (re-run clean + secret-scan) → `trackio logbook publish DineshAI/QYpByrxSTg`; create GitHub `MachineLearning-Nerd/icml26-repro-qypbyrxstg-dprsc`.

## venv
`papers/icml26-repro-qypbyrxstg-dprsc/.venv` (py3.12; numpy 2.5.1, pandas 3.0.3, matplotlib). Run via `MPLBACKEND=Agg .venv/bin/python repro/src/run_dprsc.py --dataset <ds> --n <n> --workers 4 --tests epsilon,qtime`.
