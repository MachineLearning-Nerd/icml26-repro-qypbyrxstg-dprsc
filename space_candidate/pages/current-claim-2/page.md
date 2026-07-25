# Current verification — Claim 2

**Verdict: BLOCKED.**

Theorem 1.4 quantifies over every pattern \(H\), every \((\varepsilon,\delta)\)-DP algorithm with constant \(\varepsilon>0\) and \(\delta\in[0,1/2)\), sufficiently large constant success probability, \(|Q|\ge n^c\) for sufficiently small constant \(c>0\), and infinitely many \(n\). Its three regimes scale against \(\widetilde{\mathrm{HS}}_{f_H}(G)\), not GS.

Raw facts inline:

```json
{"constant_d":"Omega(log^(d-1)(n) * HS_tilde)","d_O_log_n":"2^Omega(d) * HS_tilde","d_Omega_log_n":"n^Omega(1) * HS_tilde"}
```

- [Exact contract](evidence/claim-2/claim_contract.json)
- [Source audit and primary dependency list](evidence/claim-2/source_audit.md)
- [Raw source facts](evidence/claim-2/raw_source_facts.json)
- [Source verifier](evidence/verify_claim_sources.py)
- [Method](evidence/claim-2/method.md)
- [Limitations](evidence/claim-2/limitations.md)

The GS-substitution negative control exits nonzero. The historical SMT and finite checks do not discharge the imported discrepancy and DP-reconstruction lemmas, so they cannot verify this universal theorem.
