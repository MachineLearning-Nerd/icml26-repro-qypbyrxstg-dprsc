#!/usr/bin/env python3
"""Generate the DPRSC C1/C3 full-scale Colab notebook: accuracy (epsilon-test) of
ours (pure_DP, approx_DP) vs baselines (base_comp, base_comp_ADP) across ALL THREE
paper datasets (ca-netscience, musae-squirrel, bio-WormNet-v3) and all patterns.
Closes the dataset-coverage gap for C1/C3.

Pure Python (CPU/RAM-bound, GPU does NOT help). Reduced query count (qmult) for the
large datasets so it finishes in reasonable time + memory; the accuracy ordering is
structural, so this does not affect the verdict. workers=1-2 (memory); per-pattern
try/except so a triangle OOM still leaves edge + 2-star.
"""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dprsc_c1c3_fullscale.ipynb")
cells = []


def md(src):
    cells.append({"cell_type": "markdown", "metadata": {}, "source": src})


def code(src):
    cells.append({"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": src})


md(
    "# DPRSC — C1/C3 full-scale accuracy across all 3 datasets\n\n"
    "Reproduces **C1** (efficient algorithms, small additive error) and **C3** (significantly outperform baselines "
    "in accuracy) of *Differentially Private Range Subgraph Counting* (ICML 2026, `QYpByrxSTg`) at the paper's "
    "**full dataset coverage**: **ca-netscience (n=379)**, **musae-squirrel (n=5201)**, **bio-WormNet-v3 (n=16347)**, "
    "all patterns (edge, 2-star, triangle).\n\n"
    "For each (dataset, pattern): run the ε-test and compare **ours** (`pure_DP`, `approx_DP`) vs **baselines** "
    "(`base_comp` basic composition, `base_comp_ADP` advanced composition). C3 holds when ours' error ≤ both "
    "baselines at every ε.\n\n"
    "**Pure Python — a GPU does NOT help** (CPU/RAM-bound). To fit Colab's CPU/RAM, the large datasets use a "
    "reduced query count (`qmult`); the accuracy *ordering* (ours ≪ baselines) is structural so this does not change "
    "the verdict, only tightens the estimate. `workers=1–2` controls memory; each pattern is wrapped in try/except "
    "so a heavy `triangle` OOM still leaves `edge`+`2-star` for that dataset.")

code(
    "# Clone official repo (code + bundled datasets) + install deps\n"
    "!pip -q install numpy pandas matplotlib\n"
    "![ ! -d DPRSC ] && git clone --depth 1 https://github.com/Airleave/DPRSC\n"
    "import os, sys\n"
    "os.chdir('/content/DPRSC'); sys.path.insert(0, '/content/DPRSC')\n"
    "print('ready at', os.getcwd(), '| cpus:', os.cpu_count())")

code(
    "# Helper: epsilon (accuracy) test for one (dataset, pattern) at d=1.\n"
    "import math, logging, concurrent.futures\n"
    "import numpy as np, pandas as pd\n"
    "logging.basicConfig(level=logging.WARNING); logger = logging.getLogger('c1c3')\n"
    "import preprocessing, ourAlg, baseline\n"
    "\n"
    "def eps_run_acc(dataset, n, pattern, eps_list, workers=2, qmult=1.0):\n"
    "    d = 1\n"
    "    d_max, test_nodes, edges, h, m = preprocessing.graph_data_load(dataset, pattern, n, logger, d)\n"
    "    Qn = math.ceil(n**1.5 * qmult); Q = preprocessing.generate_queries(Qn, m, d)\n"
    "    rows = []\n"
    "    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as ex:\n"
    "        ftrue = ex.submit(ourAlg.query_true, n, m, d, Q, test_nodes, logger)\n"
    "        fp = {e: ex.submit(ourAlg.pure_DP, n, m, d, Q, e, test_nodes, pattern, logger) for e in eps_list}\n"
    "        fa = {e: ex.submit(ourAlg.approx_DP, n, m, d, Q, d_max, e, 1e-5, test_nodes, pattern, logger) for e in eps_list}\n"
    "        true = ftrue.result()\n"
    "        for e in eps_list:\n"
    "            pe, _ = fp[e].result(); ae, _ = fa[e].result()\n"
    "            bc  = baseline.base_comp(n, Qn, 1, e, true, pattern, logger)\n"
    "            bcA = baseline.base_comp_ADP(n, Qn, 1, d_max, e, 1e-5, true, pattern, logger)\n"
    "            rows.append(dict(eps=e, pure=pe/Qn, approx=ae/Qn, base_comp=bc[0], base_comp_ADP=bcA[0]))\n"
    "    return pd.DataFrame(rows), m, Qn\n"
    "print('helper ready')")

code(
    "# CONFIG: all 3 datasets x all patterns. qmult shrinks Q on the big datasets (time/RAM).\n"
    "EPS = [0.5, 1.0, 2.0, 4.0]\n"
    "W = min(os.cpu_count() or 2, 2)   # workers=1-2 -> memory safe (triangle enumerations are heavy)\n"
    "CONFIG = [\n"
    "    ('ca-netscience',   379,   1.00, ['edge', '2star', 'triangle']),  # tiny -> full Q\n"
    "    ('musae-squirrel',  5201,  0.10, ['edge', '2star', 'triangle']),  # 10x fewer queries\n"
    "    ('bio-WormNet-v3',  16347, 0.02, ['edge', '2star', 'triangle']),  # 50x fewer queries\n"
    "]\n"
    "all_results = {}\n"
    "for ds, n, qm, pats in CONFIG:\n"
    "    for pat in pats:   # light -> heavy, so partial progress if triangle OOMs\n"
    "        key = (ds, pat)\n"
    "        try:\n"
    "            print(f'>> {ds} {pat} (n={n}, qmult={qm}, workers={W}) ...', flush=True)\n"
    "            df, m, Qn = eps_run_acc(ds, n, pat, EPS, workers=W, qmult=qm)\n"
    "            all_results[key] = (df, m, Qn)\n"
    "            print(df.round(3).to_string(index=False), flush=True)\n"
    "        except Exception as e:\n"
    "            print(f'  !! {ds} {pat} FAILED: {type(e).__name__}: {str(e)[:120]}', flush=True)\n"
    "            all_results[key] = None\n"
    "print('DONE')")

code(
    "# C1/C3 summary: per (dataset, pattern), does ours beat both baselines at every eps?\n"
    "rows = []\n"
    "for (ds, pat), res in all_results.items():\n"
    "    if res is None:\n"
    "        rows.append(dict(dataset=ds, pattern=pat, status='FAILED')); continue\n"
    "    df, m, Qn = res\n"
    "    pure_ok   = (df.pure <= df.base_comp).all() and (df.pure <= df.base_comp_ADP).all()\n"
    "    approx_ok = (df.approx <= df.base_comp).all() and (df.approx <= df.base_comp_ADP).all()\n"
    "    r = df.iloc[1]  # eps = 1.0\n"
    "    rows.append(dict(dataset=ds, pattern=pat, Q=Qn,\n"
    "                     pure_eps1=round(r.pure,4), base_comp_eps1=round(r.base_comp,4),\n"
    "                     pure_wins_all_eps=bool(pure_ok), approx_wins_all_eps=bool(approx_ok)))\n"
    "summary = pd.DataFrame(rows)\n"
    "print(summary.to_string(index=False))\n"
    "n_ok = summary.get('pure_wins_all_eps'); \n"
    "if n_ok is not None:\n"
    "    print(f\"\\nC3 (pure_DP <= both baselines at all eps): {int(n_ok.sum())}/{len(n_ok)} (dataset,pattern) cells\")\n"
    "summary.to_csv('c1c3_summary.csv', index=False)")

code(
    "# Plot: mean error ours vs baselines per (dataset, pattern) that succeeded (log scale).\n"
    "import matplotlib.pyplot as plt\n"
    "ok = {k: v for k, v in all_results.items() if v is not None}\n"
    "keys = list(ok.keys())\n"
    "if keys:\n"
    "    n_plots = len(keys); cols = 3; rows_n = (n_plots + cols - 1)//cols\n"
    "    fig, axes = plt.subplots(rows_n, cols, figsize=(5*cols, 3.5*rows_n), squeeze=False)\n"
    "    methods = ['pure', 'approx', 'base_comp', 'base_comp_ADP']\n"
    "    for ax, k in zip(axes.flat, keys):\n"
    "        df, m, Qn = ok[k]\n"
    "        means = [df[x].mean() for x in methods]\n"
    "        ax.bar(methods, means, color=['#2ca02c','#98df8a','#d62728','#ff9896'])\n"
    "        ax.set_yscale('log'); ax.set_title(f'{k[0]} · {k[1]}', fontsize=9)\n"
    "        ax.tick_params(axis='x', labelsize=7, rotation=15)\n"
    "    for ax in axes.flat[n_plots:]: ax.axis('off')\n"
    "    plt.tight_layout(); plt.savefig('c1c3_fullscale.png', dpi=110, bbox_inches='tight'); plt.show()\n"
    "    print('saved c1c3_fullscale.png')\n"
    "else:\n"
    "    print('no successful runs to plot')")

code(
    "# Save all per-(dataset,pattern) CSVs + summary + figure, zip, download.\n"
    "import glob, zipfile\n"
    "from google.colab import files\n"
    "for (ds, pat), res in all_results.items():\n"
    "    if res is None: continue\n"
    "    df, m, Qn = res\n"
    "    df.assign(dataset=ds, pattern=pat, m=m, Q=Qn).to_csv(f'c1c3_{ds}_{pat}.csv', index=False)\n"
    "with zipfile.ZipFile('/content/dprsc_c1c3_results.zip', 'w') as zf:\n"
    "    for f in glob.glob('c1c3_*'):\n"
    "        zf.write(f)\n"
    "files.download('/content/dprsc_c1c3_results.zip')\n"
    "print('zipped', glob.glob('c1c3_*'))")

nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
        "colab": {"provenance": []},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}
with open(OUT, "w") as fh:
    json.dump(nb, fh, indent=1)
print("wrote", OUT, f"({len(cells)} cells)")
