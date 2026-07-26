# Release report and score forecast

- Previous live judged score: `5/10`
- Conservative projected score range after the proposed change: `7–8/10`
- Best-supported possible new score: **`8/10` forecast**, not a judge result

Only the live evaluator can change the score. The forecast assumes full credit
for the proof-level Claim 3 verification and the assumption-satisfying Claim 4
falsification; it does not award full credit to any BLOCKED claim.

| Claim | Current points | Possible points | Confidence | Evidence status | Basis and remaining risk |
| --- | ---: | ---: | --- | --- | --- |
| 1 | 1 | 1 | LOW | BLOCKED | Four routes expose a positive-probability invalid Algorithm 5 witness and provide full-scale finite calibration, but do not prove or falsify the existential theorem or exhaustively establish “first.” |
| 2 | 1 | 1 | LOW | BLOCKED | Reconstruction and graph-lift algebra pass, but the cited partial-discrepancy transfer does not prove the written exponent; the fourth route finds no theorem-level counterexample. |
| 3 | 1 | 2 | HIGH | VERIFIED | Independent universal privacy/utility derivation, exact projection identity, exhaustive functional checks, and failing under-noise/tie/average controls directly establish Algorithm 1–3 and Theorem 3.3. |
| 4 | 1 | 2 | HIGH | FALSIFIED | A valid empty-graph 2-star input gives Algorithm 4 a negative output with positive probability; Algorithm 5 uses it as a Laplace scale and released NumPy raises `ValueError`. |
| 5 | 1 | 1–2 | MEDIUM | BLOCKED | All 144 full accuracy comparisons hold and all runtime RSE gates pass. Runtime reaches 3–4 orders only on larger cases, not uniformly; cross-hardware interpretation remains material. |

## What changed since the previous judge

- Claim 1: exact max-absolute, probability, hidden-constant, and efficiency
  quantifiers are now visible; all three datasets/patterns and paper query
  budgets are calibrated; exactly four low-confidence routes are recorded.
- Claim 2: the imported GS substitution is corrected to HS-tilde; five primary
  sources are pinned; the reconstruction lemma is independently discharged;
  the exact partial-discrepancy proof gap and mandatory falsification route are
  visible.
- Claim 3: the empirical proxy is replaced by a universal analytic
  privacy/utility certificate plus exhaustive and independent checkers.
- Claim 4: Algorithm 4 is independently tested and yields a valid
  assumption-satisfying counterexample to the named Algorithm 4/5 guarantee.
- Claim 5: WormNet-v3, all patterns, all eight epsilon values, 20 repetitions,
  exact paper query budgets, and adaptive runtime sampling are now present.
  The imported “3–4 orders in accuracy” mapping is corrected to runtime.

## BLOCKED claims

Claims 1 and 2 require new proof-level arguments or theorem-level
counterexamples. Claim 5 requires an assumption-matched timing environment or
a more precisely scoped interpretation of the paper's empirical runtime
sentence. Their evidence is included because each is a terminal, honest
scientific result—not because BLOCKED is equivalent to full credit.

## Experiment and compute summary

The winning scientific lineage descends from the frozen 5/10 baseline through
source contracts, Claim 4 falsification, Claim 3 proof certificate, Claim 2
dependency audit, full Claim 5 accuracy, adaptive Claim 5 runtime, and the
four-route Claim 1 audit. The final cumulative science run was
`8e48d699-77f6-4924-93a8-f1cc62d50777` at
`9cbe9f7d90b6a2ec32d8bf1047450c5c26aa6ec3`, using HF `cpu-upgrade`.
Estimated allocation was 4 cores for 15–30 minutes; 64 logical CPUs were
exposed; the suite took `1036.093 s` (`17m46s` orchestrator duration).

Fixed command:

```bash
uv run --frozen python repro/src/run_campaign.py
```

Publication completed through a text-only additive commit to the existing
Space `DineshAI/QYpByrxSTg`; no second Space was created. Published revision
`0af4a5487541cbfa8e85a687a24483a1075c3454` was downloaded exactly, every
manifest hash passed, and the canonical evaluator traversal passed with 81
files opened and all 22 protected historical artifacts preserved. GitHub
`master` was confirmed at
`ff86be4c06d2a8f8b65c735478830e0c42db5e8a`. The paper is awaiting the live
judge, and the live score remains 5/10 until a new verdict is recorded.
