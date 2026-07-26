---
title: "Repro - DPRSC (DP Range Subgraph Counting)"
emoji: 🔒
colorFrom: yellow
colorTo: red
sdk: static
pinned: false
tags:
 - trackio
 - trackio-logbook
 - open-experiment
 - icml2026-repro
 - paper-QYpByrxSTg
---

# Repro - DPRSC (DP Range Subgraph Counting)

Start at the [current five-claim verification and visibility matrix](#/current-status).
The current cumulative verdicts are: Claim 3 **VERIFIED**, Claims 4 and 5
**FALSIFIED**, and Claims 1 and 2 **BLOCKED**. Claim 5's verdict applies to the
exact evaluator-anchored source attribution; the paper's separate runtime
observation remains BLOCKED.

The current verifier is the fixed command
`uv run --frozen python repro/src/run_campaign.py`. The previous published
revision `adf4e474c3afe562e54e0bfd1534e1323f0c5783` was rejudged at **4/10**.
This candidate forecasts at most 6/10; only a future live verdict can change
the recorded score.

Every file from judged revision
`6d5d785bb7f0386ef5d46b609fb529dbd1058fcb` remains reachable under
[Historical rejected baseline](#/index). The protected historical copy is
immutable and is not the current verifier.
