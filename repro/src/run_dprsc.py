#!/usr/bin/env python3
"""DPRSC reproduction runner.

Calls the upstream functions directly (so upstream/ stays unmodified) on a
bundled dataset, with a worker count tuned to this 4-vCPU box (the repo default
assumes ~120 cores). Runs:
  - implement_epsilon_test  -> {ds}_{pattern}_epsilon_result.csv
      columns: epsilon, pure_DP_error, approx_DP_error, base_comp_error,
               base_comp_ADP_error (+ _std).  Verifies C3 (accuracy): ours << baselines.
  - query_time_test         -> {ds}_{pattern}_qtime_result.csv  (microseconds).
  - implement_Q_test        -> error vs query count (optional).

Faithful to the authors' protocol; DP noise is the code's own Laplace mechanism,
averaged over Q_num x repeat_times queries. CSVs land in upstream/{ds}/ then are
copied to outputs/.
"""
import argparse
import glob
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.abspath(os.path.join(HERE, "..", "..", "upstream"))
OUT = os.path.abspath(os.path.join(HERE, "..", "..", "outputs"))
sys.path.insert(0, UP)
os.chdir(UP)  # modules import each other by name; CSVs write to {ds}/


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--m", type=int, default=None)
    ap.add_argument("--d", type=int, default=1)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--tests", default="epsilon,qtime")
    args = ap.parse_args()
    m = args.m or args.n
    mw = [args.workers] * 3
    import test as T  # noqa: E402  (import after sys.path/cwd set)

    tests = args.tests.split(",")
    if "epsilon" in tests:
        print(f"== epsilon test {args.dataset} n={args.n} d={args.d} workers={args.workers} ==", flush=True)
        T.implement_epsilon_test(args.dataset, args.n, args.d, mw)
    if "qtime" in tests:
        print(f"== query-time test {args.dataset} n={args.n} m={m} ==", flush=True)
        T.query_time_test(args.dataset, args.n, m, args.d)
    if "q" in tests:
        print(f"== Q-scaling test {args.dataset} ==", flush=True)
        T.implement_Q_test(args.dataset, args.n, m, args.d, mw, 5)

    os.makedirs(OUT, exist_ok=True)
    for csv in glob.glob(os.path.join(args.dataset, "*.csv")):
        dst = os.path.join(OUT, args.dataset + "_" + os.path.basename(csv))
        shutil.copy(csv, dst)
        print("collected", dst, flush=True)
    print("RUN_DONE", flush=True)


if __name__ == "__main__":
    main()
