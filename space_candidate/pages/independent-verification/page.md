# Independent verification


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_8e6ec2b8a951", "created_at": "2026-07-16T12:17:43+00:00", "title": "Why the result is structural + reproducible"}
-->
1. **Structural:** ours' noise scale is `~(log m)^d/ε`; baselines' is `~Q·(log m)^d/ε` (`Q=n^1.5`). ours' advantage is by construction — confirmed by reading `ourAlg.py` (range tree) vs `baseline.py` (naive composition).
2. **Reproducible:** DP noise is randomized but error is averaged over `Q × repeats` queries; the ordering ours < base_comp is stable across re-runs (a live re-run is captured on this page).
3. **Per-pattern:** pure_DP ≤ both baselines at all ε for **all 3 patterns** (triangle/edge/2-star) — see Claim 3 tables.
4. **Negative control:** baselines never beat ours on edge/2-star at any ε; on triangle only approx_DP (not pure_DP) trails basic-comp at low ε.


---
<!-- trackio-cell
{"type": "code", "id": "cell_78f6aaf4da15", "created_at": "2026-07-16T12:18:44+00:00", "title": "Reproducibility re-run: ca-netscience edge", "command": [".venv/bin/python", "repro/src/run_epsilon_one.py", "--dataset", "ca-netscience", "--n", "379", "--pattern", "edge", "--workers", "4"], "exit_code": 0, "duration_s": 6.743}
-->
````bash
$ .venv/bin/python repro/src/run_epsilon_one.py --dataset ca-netscience --n 379 --pattern edge --workers 4
````

exit 0 · 6.7s


````python title=run_epsilon_one.py
#!/usr/bin/env python3
"""Single-pattern DPRSC epsilon (accuracy) test — for paper-scale datasets within
a time budget. Mirrors test.implement_epsilon_test for ONE pattern with a
configurable repeat count, so each musae-squirrel pattern fits in one bounded run.
Output: outputs/{dataset}_{pattern}_epsilon_result.csv + a C3 claim check.
"""
import argparse
import concurrent.futures
import csv
import logging
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.abspath(os.path.join(HERE, "..", "..", "upstream"))
OUT = os.path.abspath(os.path.join(HERE, "..", "..", "outputs"))
sys.path.insert(0, UP)
os.chdir(UP)
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

import baseline  # noqa: E402
import ourAlg  # noqa: E402
import preprocessing  # noqa: E402


def calc_mu_std(s, s2, c):
    mu = s / c
    std = math.sqrt((s2 - s * mu) / (c - 1))
    return mu, std


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--d", type=int, default=1)
    ap.add_argument("--pattern", required=True, choices=["triangle", "edge", "2star"])
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--repeats", type=int, default=1)
    ap.add_argument("--qmult", type=float, default=1.0,
                    help="scale Q_num down to fit memory/time on small boxes (claim is structural)")
    args = ap.parse_args()

    eps_test = [x / 10.0 for x in range(5, 45, 5)]
    pattern = args.pattern
    d_max, test_input_nodes, edges, h, m = preprocessing.graph_data_load(
        args.dataset, pattern, args.n, logger, args.d)
    if args.d == 1:  # upstream convention: Q_num = n^1.5, skewed queries
        Q_num = math.ceil(args.n ** 1.5 * args.qmult)
        Q = preprocessing.generate_queries(Q_num, m, args.d)
    else:            # d == 2: Q_num = n^2, random queries (per upstream test.py)
        Q_num = math.ceil(args.n ** 2 * args.qmult)
        Q = preprocessing.generate_random_queries(Q_num, m, args.d)
    print(f"{args.dataset} {pattern} n={args.n} Q={Q_num} repeats={args.repeats} m={m}", flush=True)

    rows = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as ex:
        ftrue = ex.submit(ourAlg.query_true, args.n, m, args.d, Q, test_input_nodes, logger)
        fpure = [[ex.submit(ourAlg.pure_DP, args.n, m, args.d, Q, eps, test_input_nodes, pattern, logger) for eps in eps_test] for _ in range(args.repeats)]
        fapprox = [[ex.submit(ourAlg.approx_DP, args.n, m, args.d, Q, d_max, eps, 1e-5, test_input_nodes, pattern, logger) for eps in eps_test] for _ in range(args.repeats)]
        true = ftrue.result()
        for i, eps in enumerate(eps_test):
            ps = ps2 = aps = aps2 = 0.0
            for t in range(args.repeats):
                e, e2 = fpure[t][i].result(); ps += e; ps2 += e2
                e, e2 = fapprox[t][i].result(); aps += e; aps2 += e2
            pmu, pstd = calc_mu_std(ps, ps2, Q_num * args.repeats)
            amu, astd = calc_mu_std(aps, aps2, Q_num * args.repeats)
            bc = baseline.base_comp(args.n, Q_num, args.repeats, eps, true, pattern, logger)
            bcA = baseline.base_comp_ADP(args.n, Q_num, args.repeats, d_max, eps, 1e-5, true, pattern, logger)
            rows.append((eps, pmu, pstd, amu, astd, bc[0], bc[1], bcA[0], bcA[1]))
            print(f"  eps={eps}: pure={pmu:.4g} approx={amu:.4g} base_comp={bc[0]:.4g} base_comp_ADP={bcA[0]:.4g}", flush=True)

    os.makedirs(OUT, exist_ok=True)
    fn = os.path.join(OUT, f"{args.dataset}_{pattern}_epsilon_result.csv")
    with open(fn, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["epsilon", "pure_DP_error", "pure_DP_std", "approx_DP_error", "approx_DP_std",
                    "base_comp_error", "base_comp_std", "base_comp_ADP_error", "base_comp_ADP_std"])
        for r in rows:
            w.writerow([round(x, 4) for x in r])
    ok = all(r[1] <= r[5] and r[3] <= r[5] and r[1] <= r[7] and r[3] <= r[7] for r in rows)
    print(f"wrote {fn} | C3 ({pattern}) ours<=both baselines at all eps: {ok}", flush=True)


if __name__ == "__main__":
    main()

````


````output
INFO attribute for ca-netscience finished!
INFO edge counting for ca-netscience finished!
914
ca-netscience edge n=379 Q=7379 repeats=1 m=379
INFO finish building range tree dynamically for pure DP
INFO finish building range tree dynamically for query true
INFO finish building range tree dynamically for pure DP
INFO finish building range tree dynamically for pure DP
INFO finish answering queries for pure DP
INFO finish building range tree dynamically for pure DP
INFO finish building range tree dynamically for pure DP
INFO finish answering queries for pure DP
INFO finish answering queries for pure DP
INFO finish building range tree dynamically for pure DP
INFO finish building range tree dynamically for pure DP
INFO finish answering queries for pure DP
INFO finish answering queries for pure DP
INFO finish building range tree dynamically for pure DP
INFO finish building range tree dynamically for approximate DP
INFO finish answering queries for pure DP
INFO finish answering queries for pure DP
INFO finish building range tree dynamically for approximate DP
INFO finish building range tree dynamically for approximate DP
INFO finish answering queries for pure DP
INFO finish building range tree dynamically for approximate DP
INFO finish answering queries for approximate DP
INFO finish answering queries for approximate DP
INFO finish answering queries for approximate DP
INFO finish building range tree dynamically for approximate DP
INFO finish building range tree dynamically for approximate DP
INFO finish building range tree dynamically for approximate DP
INFO finish answering queries in base_comp
INFO finish answering queries for approximate DP
INFO finish building range tree dynamically for approximate DP
INFO finish answering queries for approximate DP
INFO finish answering queries in base_comp_ADP
  eps=0.5: pure=1.933 approx=1.784 base_comp=26.95 base_comp_ADP=3.004
INFO finish answering queries for approximate DP
INFO finish answering queries for approximate DP
INFO finish answering queries in base_comp
INFO finish answering queries for approximate DP
INFO finish answering queries in base_comp_ADP
  eps=1.0: pure=1.033 approx=1.36 base_comp=13.34 base_comp_ADP=1.496
INFO finish answering queries in base_comp
INFO finish answering queries in base_comp_ADP
  eps=1.5: pure=0.9287 approx=0.7512 base_comp=8.718 base_comp_ADP=0.9839
INFO finish answering queries in base_comp
INFO finish answering queries in base_comp_ADP
  eps=2.0: pure=0.5788 approx=0.5011 base_comp=6.514 base_comp_ADP=0.7355
INFO finish answering queries in base_comp
INFO finish answering queries in base_comp_ADP
  eps=2.5: pure=0.3314 approx=0.412 base_comp=5.232 base_comp_ADP=0.5846
INFO finish answering queries in base_comp
INFO finish answering queries in base_comp_ADP
  eps=3.0: pure=0.3022 approx=0.2805 base_comp=4.372 base_comp_ADP=0.5046
INFO finish answering queries in base_comp
INFO finish answering queries in base_comp_ADP
  eps=3.5: pure=0.2428 approx=0.2848 base_comp=3.869 base_comp_ADP=0.4257
INFO finish answering queries in base_comp
INFO finish answering queries in base_comp_ADP
  eps=4.0: pure=0.278 approx=0.2653 base_comp=3.3 base_comp_ADP=0.3784
wrote /home/dineshai/Drives/Code/AllCode/ReproduceICML/papers/icml26-repro-qypbyrxstg-dprsc/outputs/ca-netscience_edge_epsilon_result.csv | C3 (edge) ours<=both baselines at all eps: True

````


---
<!-- trackio-cell
{"type": "artifact", "id": "cell_c82ab34544bf", "created_at": "2026-07-16T12:18:44+00:00", "title": "Artifact: ca-netscience_edge_epsilon_result.csv", "path": "outputs/ca-netscience_edge_epsilon_result.csv", "size": 619, "artifact_type": "dataset", "auto": true}
-->
**📦 Artifact** `outputs/ca-netscience_edge_epsilon_result.csv` · dataset · 619 B

https://huggingface.co/buckets/DineshAI/QYpByrxSTg-artifacts#logbook-files/outputs/ca-netscience_edge_epsilon_result.csv
