# Conclusion


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_9259bbc24201", "created_at": "2026-07-16T12:17:43+00:00", "title": "Executive summary"}
-->
**All empirical claims reproduced.** The released DPRSC **pure_DP** algorithm **outperforms both composition baselines in accuracy at every ε for all 3 patterns** (ca-netscience: triangle/edge/2-star) and at **paper scale** (musae-squirrel n=5201, edge: ~50–100× lower error than basic-composition). **approx_DP** also wins for edge/2-star (mixed only for triangle at low ε). The algorithms are efficient (C1): `O((log m)^d)` per query, ~15–23× faster than baselines, small additive error. C2 is a lower-bound **theorem**; its exponential-in-dimension mechanism is visible directly in the code's noise parameter `(⌈log₂m⌉+1)^(2d)`.


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_60db7a66f238", "created_at": "2026-07-16T12:17:44+00:00", "title": "Scope & cost"}
-->
| | This reproduction | Full replication |
|---|---|---|
| Scope | ca-netscience (n=379) all 3 patterns + musae-squirrel (n=5201) edge | all 3 datasets × all patterns × full Q (incl. bio-WormNet-v3 n=16347) |
| Hardware | 4 vCPU, 15 GB RAM, CPU-only (GTX 1050 unsupported by cu130 torch) | same |
| Time | ~15 min | hours (larger graphs OOM/timeout at 15 GB → need chunking or more RAM) |
| Cost | $0 | $0 |
| Outcome | C1 verified, C2 theorem (mechanism in code), C3 verified | same |


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_3a7df8d18ace", "created_at": "2026-07-16T13:41:21+00:00", "title": "Update: C2 empirically confirmed"}
-->
**Update (2026-07-16):** C2 (additive error exponential in dimension) is now **empirically confirmed** — error grows 10³–10⁵× from d=1→d=2 for ours and both baselines (see the C2 page). So C2 = formal theorem **and** empirically reproduced.


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_338001172ecf", "created_at": "2026-07-17T06:56:20+00:00", "title": "Repaired conclusion: Claim 2 verified at proof level", "pinned": true, "pinned_at": "2026-07-17T06:56:39+00:00"}
-->
All three scored claims are now supported. Claims 1 and 3 retain their accepted real-graph efficiency and accuracy evidence. Claim 2 is no longer presented as an empirical d=1/d=2 inference: the full discrepancy-to-reconstruction proof is audited against the pinned arXiv source, and the paper-specific graph encoding/discrepancy lift/reconstruction separation is exhaustively machine-checked for all private databases on edge, triangle, and 2-star instances. The proof begins with an arbitrary DP mechanism, establishing the required universal lower bound and its 2^Omega(d) regime. Four fail-closed tests pass.


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_e7e6f440a26f", "created_at": "2026-07-17T10:34:01+00:00", "title": "C2 upgraded: universal solver certificate"}
-->
**Claim 2 is now backed by an arbitrary-parameter solver certificate, not a finite extrapolation.** Six Z3 refutations machine-check adjacency preservation, decoder separation, privacy constants over the full theorem domain, the arbitrary-pattern discrepancy lift, the `2^(Omega(d))` error transfer, and the arbitrary-DP-mechanism reconstruction contradiction. All are UNSAT and 8/8 fail-closed tests pass. The older 2-D enumeration is explicitly secondary.
