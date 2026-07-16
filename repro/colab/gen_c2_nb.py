#!/usr/bin/env python3
"""Generate the Colab notebook for the DPRSC C2 dimension-scaling experiment."""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dprsc_c2_dimension_scaling.ipynb")

cells = []

def md(src):
    cells.append({"cell_type": "markdown", "metadata": {}, "source": src})

def code(src):
    cells.append({"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": src})

md(
    "# DPRSC — C2 dimension-scaling (error vs dimension)\n\n"
    "Empirically illustrates **Claim 2** of *Differentially Private Range Subgraph Counting* "
    "(ICML 2026, `QYpByrxSTg`): **any DP algorithm must incur additive error exponential in the dimension.**\n\n"
    "We run the released DPRSC algorithms **and** the baselines at **d=1** and **d=2** on a bundled dataset "
    "and show the error grows ~exponentially with dimension. The theory is direct from the code: the Laplace "
    "noise magnitude is parameterized as `(ceil(log2(m))+1)^(2*d)`, so going d=1 → d=2 should multiply the "
    "error by ~`(ceil(log2(m))+1)^2` for every method (ours and baselines alike) — exactly the "
    "'exponential in dimension' behaviour C2 claims must hold for *any* DP algorithm.\n\n"
    "**CPU-only** (pure Python: numpy/pandas/matplotlib). Colab gives enough cores/RAM/time for the d=2 "
    "(4-D range-tree) run that times out on a 4-vCPU/15 GB box.")

code(
    "# Clone the official repo (code + bundled datasets) and install deps\n"
    "!pip -q install numpy pandas matplotlib\n"
    "![ ! -d DPRSC ] && git clone --depth 1 https://github.com/Airleave/DPRSC\n"
    "import os, sys\n"
    "os.chdir('/content/DPRSC'); sys.path.insert(0, '/content/DPRSC')\n"
    "print('ready at', os.getcwd())")

code(
    "# Helper: epsilon (accuracy) test for one (pattern, dimension). Returns a DataFrame of\n"
    "# MEAN relative error per epsilon for ours (pure_DP, approx_DP) and baselines (base_comp, base_comp_ADP).\n"
    "import math, logging\n"
    "import concurrent.futures\n"
    "import numpy as np, pandas as pd\n"
    "logging.basicConfig(level=logging.WARNING); logger = logging.getLogger('c2')\n"
    "import preprocessing, ourAlg, baseline\n"
    "\n"
    "def eps_run(dataset, n, pattern, d, eps_list, workers=2, qmult=1.0):\n"
    "    d_max, test_nodes, edges, h, m = preprocessing.graph_data_load(dataset, pattern, n, logger, d)\n"
    "    if d == 1:\n"
    "        Qn = math.ceil(n**1.5 * qmult); Q = preprocessing.generate_queries(Qn, m, d)\n"
    "    else:  # d == 2: upstream convention (Q_num = n^2, random queries)\n"
    "        Qn = math.ceil(n**2 * qmult); Q = preprocessing.generate_random_queries(Qn, m, d)\n"
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
    "    return pd.DataFrame(rows), m\n"
    "print('helper ready')")

code(
    "# Run d=1 and d=2 for edge + triangle on ca-netscience (n=379; one of the paper's datasets).\n"
    "eps_list = [0.5, 1.0, 2.0, 4.0]\n"
    "results = {}\n"
    "for pat in ['edge', 'triangle']:\n"
    "    for d in [1, 2]:\n"
    "        print(f'>> {pat} d={d} ...', flush=True)\n"
    "        df, m = eps_run('ca-netscience', 379, pat, d, eps_list, workers=2, qmult=1.0)\n"
    "        results[(pat, d)] = (df, m)\n"
    "        print(df.round(3).to_string(index=False), flush=True)\n"
    "print('done')")

code(
    "# d=2 / d=1 error ratio vs the theoretical noise factor (ceil(log2 m)+1)^2.\n"
    "print('C2 — exponential-in-dimension check (d=2 error should be ~(log2 m+1)^2 x d=1 error):\\n')\n"
    "for pat in ['edge', 'triangle']:\n"
    "    d1, _ = results[(pat, 1)]; d2, m = results[(pat, 2)]\n"
    "    theo = (math.ceil(math.log2(m)) + 1) ** 2\n"
    "    print(f'[{pat}] m={m}  ->  theoretical d2/d1 noise ratio = (log2(m)+1)^2 = {theo}')\n"
    "    print(f\"{'eps':>4} {'pure_d1':>9} {'pure_d2':>9} {'pure_ratio':>10} {'bc_d1':>8} {'bc_d2':>8} {'bc_ratio':>9}\")\n"
    "    for i in range(len(d1)):\n"
    "        rp = d2.pure[i] / max(d1.pure[i], 1e-12)\n"
    "        rb = d2.base_comp[i] / max(d1.base_comp[i], 1e-12)\n"
    "        print(f'{d1.eps[i]:>4} {d1.pure[i]:>9.3g} {d2.pure[i]:>9.3g} {rp:>10.1f} {d1.base_comp[i]:>8.3g} {d2.base_comp[i]:>8.3g} {rb:>9.1f}')\n"
    "    print()")

code(
    "# Plot: mean error at d=1 vs d=2 for every method (log scale). Bars should jump ~exponentially with d.\n"
    "import matplotlib.pyplot as plt\n"
    "fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))\n"
    "methods = ['pure', 'approx', 'base_comp', 'base_comp_ADP']\n"
    "for ax, pat in zip(axes, ['edge', 'triangle']):\n"
    "    d1, _ = results[(pat, 1)]; d2, m = results[(pat, 2)]\n"
    "    m1 = [d1[k].mean() for k in methods]; m2 = [d2[k].mean() for k in methods]\n"
    "    x = np.arange(len(methods)); w = 0.38\n"
    "    ax.bar(x - w/2, m1, w, label='d=1'); ax.bar(x + w/2, m2, w, label='d=2')\n"
    "    ax.set_yscale('log'); ax.set_xticks(x); ax.set_xticklabels(methods, rotation=15)\n"
    "    ax.set_title(f'{pat} (m={m}): mean error d=1 vs d=2'); ax.set_ylabel('mean relative error (log)'); ax.legend()\n"
    "plt.tight_layout(); plt.savefig('c2_dimension_scaling.png', dpi=110, bbox_inches='tight'); plt.show()\n"
    "print('saved c2_dimension_scaling.png')")

code(
    "# Save CSVs + zip everything for download (so the logbook can embed the numbers/figure).\n"
    "import shutil\n"
    "from google.colab import files\n"
    "for (pat, d), (df, m) in results.items():\n"
    "    df.assign(m=m).to_csv(f'c2_{pat}_d{d}.csv', index=False)\n"
    "shutil.make_archive('/content/dprsc_c2_results', 'zip', '.', 'c2_')\n"
    "files.download('/content/dprsc_c2_results.zip')\n"
    "print('zipped c2_*.{csv,png} -> /content/dprsc_c2_results.zip')")

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
