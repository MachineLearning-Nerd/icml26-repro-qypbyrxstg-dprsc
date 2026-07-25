# Methods & environment


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_1e3dbf9406b2", "created_at": "2026-07-16T12:17:42+00:00", "title": "How to reproduce"}
-->
```bash
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python numpy pandas matplotlib
# ca-netscience (all patterns, ε-test + latency):
MPLBACKEND=Agg .venv/bin/python repro/src/run_dprsc.py --dataset ca-netscience --n 379 --workers 4 --tests epsilon,qtime
# musae-squirrel (paper-scale, per pattern, reduced Q for 15GB box):
MPLBACKEND=Agg .venv/bin/python repro/src/run_epsilon_one.py --dataset musae-squirrel --n 5201 --pattern edge --qmult 0.2 --workers 2
```
Upstream `Airleave/DPRSC` vendored **unmodified**; `repro/src/run_dprsc.py` & `run_epsilon_one.py` call its functions directly (cap workers, collect CSVs). Datasets bundled. Python 3.12, numpy 2.5.1, pandas 3.0.3. CPU-only (4 vCPU, 15 GB).
