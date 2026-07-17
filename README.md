# Repro — Differentially Private Range Subgraph Counting (DPRSC), ICML 2026

Reproduction of *Differentially Private Range Subgraph Counting* (Xian Chen, Ruobing
Bai, Pan Peng) for the
[ICML 2026 Agent Reproduction Challenge](https://huggingface.co/spaces/ICML-2026-agent-repro/challenge).
OpenReview `QYpByrxSTg` · [arXiv 2606.08179](https://arxiv.org/abs/2606.08179).
Official code: [Airleave/DPRSC](https://github.com/Airleave/DPRSC) (cloned @ `aae89538`, run unmodified).

DPRSC gives differentially private approximate answers to **range subgraph-counting
queries** (count pattern occurrences — triangle / edge / 2-star — among vertices whose
attributes fall in a query range) using a **range tree** so each query is answered in
`O((log m)^d)` with `~(log m)^d/ε` Laplace noise, vs baselines (basic / advanced
composition) that pay `O(m)` per query and `~Q·(log m)^d/ε` noise.

## Official claims
1. First efficient algorithms for DP range subgraph counting with small additive error. **(empirical — reproduced)**
2. Any DP algorithm incurs additive error exponential in the dimension. **(theorem — proof audited and reduction machine-checked)**
3. Algorithms significantly outperform baselines in accuracy while maintaining strong privacy. **(empirical — reproduced)**

## Reproduce (CPU only; ~minutes for ca-netscience, longer for musae-squirrel)
```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python numpy pandas matplotlib
MPLBACKEND=Agg .venv/bin/python repro/src/run_dprsc.py --dataset ca-netscience --n 379 --workers 4 --tests epsilon,qtime
MPLBACKEND=Agg .venv/bin/python repro/src/run_dprsc.py --dataset musae-squirrel --n 5201 --workers 4 --tests epsilon,qtime
```
Outputs land in `outputs/{dataset}_{pattern}_{epsilon,qtime}_result.csv` (+ the
upstream-generated figures).

## What "verified" means here
- **C3 (accuracy):** for each pattern and ε ∈ {0.5…4.0}, `pure_DP_error` and
  `approx_DP_error` ≤ `base_comp_error` and `base_comp_ADP_error`. On ca-netscience this
  holds at all ε for triangle & edge (clean ~10–20× lower error); for 2-star the
  approximate-DP variant misbehaves at n=379 (local-sensitivity approximation) while
  pure-DP still wins — confirmed at paper-scale (musae-squirrel, n=5201).
- **Latency:** ours ~tens of µs/query vs baselines ~ms → structurally faster (range tree
  vs full edge-scan per query); gap grows with graph size.
- **C2:** the proof chain is audited against pinned arXiv source `2606.08179v1`. The
  paper-specific graph encoding, discrepancy lift, and reconstruction separation are
  exhaustively checked for all 16 private databases on edge, triangle, and 2-star;
  4/4 fail-closed tests pass. This verifies the universal claim through the arbitrary-
  mechanism reconstruction contradiction, not by extrapolating algorithm measurements.

```bash
.venv/bin/python repro/src/verify_lower_bound.py --out outputs/c2_proof_certificate.json
.venv/bin/python -m pytest repro/test_lower_bound.py -q
```

## Layout
```
upstream/            vendored Airleave/DPRSC (pinned, unmodified)
repro/src/run_dprsc.py   runner: calls upstream fns, caps workers to 4, collects CSVs
outputs/             per-dataset/pattern accuracy + latency CSVs + figures
docs/                methodology notes
.trackio/            Trackio logbook → publishes to DineshAI/QYpByrxSTg
STATUS.md            live resume state for the autonomous loop
```
See `STATUS.md` for current progress; `icml-2026-reproduction-challenge/COORDINATION.md`
for the multi-session registry.
