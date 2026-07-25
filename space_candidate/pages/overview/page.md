# Overview


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_3b698133d077", "created_at": "2026-07-16T12:17:37+00:00", "title": "Paper & claims"}
-->
Reproduction of **Differentially Private Range Subgraph Counting** (Xian Chen, Ruobing Bai, Pan Peng), ICML 2026 · [arXiv 2606.08179](https://arxiv.org/abs/2606.08179) · OpenReview `QYpByrxSTg`. Official code: [Airleave/DPRSC](https://github.com/Airleave/DPRSC) @ `aae89538` (vendored unmodified, pure-Python, CPU-only).

DP range subgraph-counting: count pattern (triangle/edge/2-star) occurrences among vertices whose attributes fall in a query range, answered privately via a **range tree** — `O((log m)^d)` per query, `~(log m)^d/ε` Laplace noise — vs baselines (basic / advanced composition) that pay `O(m)` per query and `~Q·(log m)^d/ε` noise.


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_862ce983865e", "created_at": "2026-07-16T12:17:37+00:00", "title": "Verdicts"}
-->
| Claim | Type | Verdict |
|---|---|---|
| C1: first efficient DP range subgraph-counting algos, small additive error | empirical | **verified** |
| C2: any DP algo incurs additive error exponential in dimension | theorem | **mechanism confirmed in code** (noise param = `(⌈log₂m⌉+1)^(2d)`); formal proof in paper |
| C3: significantly outperform baselines in accuracy | empirical | **verified** — pure_DP beats both baselines at every ε for all 3 patterns + paper-scale |
