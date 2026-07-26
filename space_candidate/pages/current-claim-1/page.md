# Current verification — Claim 1

**Verdict: BLOCKED. Confidence: LOW.**

Theorem 1.3 states: for every \(\varepsilon>0\) and \(\delta\in(0,1)\), there exists an \((\varepsilon,\delta)\)-DP algorithm whose **maximum absolute error over \(Q\)** is

\[
O\!\left(
\frac{\widetilde{\mathrm{HS}}_{f_H}(G)\,
\sqrt{(\varepsilon+\log(1/\delta))\log(n|Q|)}\,
\log^{2d}n}{\varepsilon}
\right),
\]

with probability at least \(1-1/n\); hidden constants are \(c^{O(d)}\). The paper separately calls it the first efficient DPRSC algorithm and gives polynomial time for \(d=O(\log n/\log\log n)\).

Raw facts: theorem `1.3`; metric `max absolute error`; success `1-1/n`;
hidden constants `c^O(d)`; current verdict `BLOCKED`.

- [Exact contract](evidence/claim-1/claim_contract.json)
- [Source audit](evidence/claim-1/source_audit.md)
- [Raw source facts](evidence/claim-1/raw_source_facts.json)
- [Source verifier](evidence/verify_claim_sources.py)
- [Primary-source manifest](evidence/claim-1/primary_source_manifest.json)
- [Raw four-route cumulative record](evidence/claim-1/theorem_audit_run.json)
- [Primary executable](evidence/reproduction/repro/src/run_claim1_theorem_audit.py)
- [Independent checker](evidence/reproduction/repro/src/verify_claim1_theorem_audit.py)
- [Method](evidence/claim-1/method.md)
- [Limitations](evidence/claim-1/limitations.md)

## Four verification routes

| Route | Direct result | Why it does or does not close the claim |
| --- | --- | --- |
| Symbolic proof reconstruction | 192 obligations checked | Printed algebra is consistent only conditional on a positive finite EstimateHS; the named witness is undefined on negative draws |
| Full-scale calibration | 72 summaries: 3 datasets × 3 patterns × 8 epsilons, 20 repetitions, paper query budgets | p95 max-error/explicit-normalizer ranges `6.0806`–`32.1799`; finite ratios cannot identify hidden `c^O(d)` constants |
| Repair and primary literature | Nissim 2007, Karwa 2011, Nguyen 2023 pinned and audited | No cited repair proves the exact stated bound; priority remains open-world |
| Mandatory falsification | Empty graphs, 2-star, d=1, predeclared epsilon/delta/n grid | Named Algorithm 5 witness is invalid, but Theorem 1.3 existential quantifier is not contradicted |

At `epsilon=2`, `delta=0.9`, `n=100`, the independently recomputed
negative-scale probability is `0.0360495930748611`, exceeding the theorem's
failure budget `1/n = 0.01`. The exact same issue occurs at multiple allowed
grid points. This is a construction-level falsification only.

Formal cumulative run `8e48d699-77f6-4924-93a8-f1cc62d50777`, source Git SHA
`9cbe9f7d90b6a2ec32d8bf1047450c5c26aa6ec3`, HF `cpu-upgrade`, estimated
4 cores / 15–30 minutes, 64 logical CPUs exposed, scientific runtime
`1036.093 s`, orchestrator duration `17m46s`. The independent checker passed.
The three Claim 1 controls—ignore undefined draws, mean-for-max, and
witness-for-existence—exit nonzero; all 15 cumulative controls failed as
intended.
