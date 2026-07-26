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
`uv run --frozen python repro/src/run_campaign.py` at release-child revision
`9abbfe44-94b7-4fc9-9cf7-0a9cbfa7fbc2` (final Git SHA is recorded after the
release regression). It supersedes the judged revision's verification code.

Every file from judged revision
`6d5d785bb7f0386ef5d46b609fb529dbd1058fcb` remains reachable under
[Historical rejected baseline](#/index). The protected historical copy is
immutable and is not the current verifier.
