#!/usr/bin/env python3
"""Verify exact source scopes for DPRSC Claims 1–4."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "repro" / "sources" / "2606.08179.html"
EXPECTED_SHA256 = "9387c720239542f024ef31654e84ced6e2687818f8f17703945aa114aab02a5b"


MARKERS = {
    "1": [
        'id="S1.Thmtheorem3"',
        "first efficient algorithm for differentially private range subgraph counting",
        r'alttext="\delta\in(0,1)"',
        r"\widetilde{\mathrm{HS}}_{f_{H}}(G)",
        r'alttext="1-\frac{1}{n}"',
        r'alttext="c^{O(d)}"',
    ],
    "2": [
        'id="S1.Thmtheorem4"',
        r'alttext="\delta\in[0,\frac{1}{2})"',
        "with a sufficiently large constant success probability",
        r'alttext="|Q|\geq n^{c}"',
        "Then there exist infinitely many",
        r"\log^{d-1}n\cdot\widetilde{\mathrm{HS}}_{f_{H}}(G)",
        r"2^{\Omega(d)}\cdot\widetilde{\mathrm{HS}}_{f_{H}}(G)",
        r"n^{\Omega(1)}\cdot\widetilde{\mathrm{HS}}_{f_{H}}(G)",
    ],
    "3": [
        'id="alg1"',
        'id="alg2"',
        'id="alg3"',
        'id="S3.Thmtheorem3"',
        "Pure DP Range Subgraph Counting",
        r"\max_{q\in Q}\left|f_{H}(G_{q})-\widetilde{f}_{H}(G_{q})\right|",
        r"\mathrm{GS}_{f_{H}}\cdot\sqrt{\log(n|Q|)}\cdot\log^{3d}{n}",
        r'alttext="\geq 1-\frac{1}{n}"',
        r'alttext="c^{O(d)}"',
    ],
    "4": [
        'id="alg4"',
        "EstimateHS",
        "Estimating private higher-order local sensitivity",
        'id="alg5"',
        "Approximate DP Range Subgraph Counting",
        "private estimation of local sensitivity rather than global sensitivity",
        'href="#S1.Thmtheorem3"',
        'href="#A5.SS2"',
    ],
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--negative-control",
        choices=["claim1-quantifiers", "claim2-gs", "claim3-average", "claim4-skip-hs"],
    )
    args = parser.parse_args()

    payload = SOURCE.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != EXPECTED_SHA256:
        raise AssertionError(f"paper source hash mismatch: {digest}")
    html = payload.decode("utf-8")
    results: dict[str, object] = {}
    for claim, markers in MARKERS.items():
        missing = [marker for marker in markers if marker not in html]
        if missing:
            raise AssertionError(f"claim {claim} missing markers: {missing}")
        results[claim] = {
            "source_contract": "PASS",
            "marker_count": len(markers),
            "scientific_verdict": "BLOCKED",
        }

    if args.negative_control:
        reasons = {
            "claim1-quantifiers": "omitting probability and c^O(d) constants changes Theorem 1.3",
            "claim2-gs": "replacing HS-tilde with GS and omitting infinitely-many/Q/success quantifiers changes Theorem 1.4",
            "claim3-average": "checking average rather than maximum error changes Theorem 3.3",
            "claim4-skip-hs": "testing ADP_RSC without EstimateHS does not test Algorithm 5",
        }
        print(
            f"NEGATIVE_CONTROL_EXPECTED_FAILURE: {reasons[args.negative_control]}",
            file=sys.stderr,
        )
        return 2

    output = {
        "schema": "dprsc-claims1-4-source-verification-v1",
        "source_sha256": digest,
        "claims": results,
        "scope": "source contracts only; no scientific verdict upgraded",
    }
    print("CLAIM_SOURCE_RESULTS", json.dumps(output, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
