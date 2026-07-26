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
The current cumulative verdicts are: Claim 3 **VERIFIED**, Claim 4
**FALSIFIED**, and Claims 1, 2, and 5 **BLOCKED**. “Blocked” is not presented
as a pass.

The current verifier is the fixed command
`uv run --frozen python repro/src/run_campaign.py` at terminal release Git SHA
`ff86be4c06d2a8f8b65c735478830e0c42db5e8a`. HF `cpu-upgrade` run
`7749e3aa-7f7d-44cd-ba3f-c25f5784b525` completed in 11m40s with 64 logical
CPUs visible. Published revision
`0af4a5487541cbfa8e85a687a24483a1075c3454` passed an exact-download manifest
check and evaluator traversal. The reproduction is awaiting the live judge;
the recorded score remains 5/10 until that evaluation.

Every file from judged revision
`6d5d785bb7f0386ef5d46b609fb529dbd1058fcb` remains reachable under
[Historical rejected baseline](#/index). The protected historical copy is
immutable and is not the current verifier.
