# Current verification — Claim 4

**Verdict: BLOCKED.**

The exact chain is Algorithm 4 `EstimateHS` → Algorithm 5 `ADP_RSC` → the range-tree mechanism. The defining calibration uses a private higher-order local-sensitivity estimate rather than global sensitivity, and the claimed utility is exactly Theorem 1.3.

Raw facts inline:

```json
{"algorithms":["EstimateHS","ADP_RSC"],"privacy":"(epsilon,delta)-DP","utility":"Theorem 1.3","current_verdict":"BLOCKED"}
```

- [Exact contract](evidence/claim-4/claim_contract.json)
- [Source audit](evidence/claim-4/source_audit.md)
- [Raw source facts](evidence/claim-4/raw_source_facts.json)
- [Source verifier](evidence/verify_claim_sources.py)
- [Method](evidence/claim-4/method.md)
- [Limitations](evidence/claim-4/limitations.md)

The bypass-EstimateHS negative control exits nonzero. Independent EstimateHS tests and a combined privacy/utility certificate remain pending.
