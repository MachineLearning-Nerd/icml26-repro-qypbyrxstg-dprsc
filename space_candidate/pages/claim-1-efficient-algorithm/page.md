# Claim 1 — efficient algorithm


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_13c1f6890932", "created_at": "2026-07-16T12:17:40+00:00", "title": "C1: efficient algorithm, small error"}
-->
The pure-DP / approximate-DP range-tree algorithms run end-to-end on real graphs (ca-netscience n=379; musae-squirrel n=5201) with small additive error (e.g. edge ε=1.0: ~0.4–1.1 mean relative error). Per-query time is `O((log m)^d)` (see Latency). **C1 verified.**


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_7fbc0ca78181", "created_at": "2026-07-16T12:17:41+00:00", "title": "Latency (query-time, µs, ca-netscience)"}
-->
| pattern | pure_DP (ours) | approx_DP (ours) | base_comp | base_comp_ADP | speedup |
|---|---|---|---|---|---|
| triangle | ~70 µs | ~68 µs | ~1240 µs | ~1140 µs | **~18×** |
| edge | ~67 µs | ~68 µs | ~1000 µs | ~960 µs | **~15×** |
| 2-star | ~69 µs | ~68 µs | ~1610 µs | ~1540 µs | **~23×** |

Range-tree queries are ~15–23× faster than baselines on this small graph; the gap grows with graph size (baselines scan all edges per query).
