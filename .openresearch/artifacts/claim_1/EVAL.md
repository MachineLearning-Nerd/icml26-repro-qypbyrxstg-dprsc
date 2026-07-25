# Claim 1 evaluator checklist

Current verdict: **BLOCKED**. Confidence: **LOW**.

The current executable is `repro/src/run_claim1_theorem_audit.py`; its
independent checker is `repro/src/verify_claim1_theorem_audit.py`. The four
required routes are recorded in `theorem_audit_run.json`.

The strongest direct result is that the paper's Algorithm 5 witness is not a
total randomized algorithm: a valid EstimateHS draw can be negative and is
then passed as a Laplace scale. This does not falsify the full existential
Theorem 1.3. Full-scale finite max-error calibration is corroborative only,
and the global “first efficient” priority statement remains non-exhaustive.
