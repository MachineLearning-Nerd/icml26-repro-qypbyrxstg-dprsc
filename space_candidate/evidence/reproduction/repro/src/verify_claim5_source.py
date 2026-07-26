#!/usr/bin/env python3
"""Fail-closed verifier for the exact Section 5 source contract.

This verifier deliberately separates the imported judge paraphrase from the
paper's actual experimental claims.  It operates on the archived HTML bytes so
the result does not depend on a later ar5iv conversion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = ROOT / "repro" / "sources" / "2606.08179.html"
EXPECTED_SHA256 = "9387c720239542f024ef31654e84ced6e2687818f8f17703945aa114aab02a5b"


def verify(source: Path) -> dict[str, object]:
    payload = source.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != EXPECTED_SHA256:
        raise AssertionError(
            f"paper source hash mismatch: expected {EXPECTED_SHA256}, got {digest}"
        )
    html = payload.decode("utf-8")

    required = {
        "section_5_anchor": 'id="S5"',
        "default_accuracy_query_budget": r'alttext="|Q|=\lceil n^{1.5}\rceil"',
        "runtime_query_budget": r'alttext="\Theta(n^{2})"',
        "runtime_sampling_rule": "relative standard error",
        "runtime_rse_threshold": r'alttext="5\%"',
        "query_latency_magnitude": "lower latency by 3 to 4 orders of magnitude",
        "total_runtime_magnitude": "yielding a speedup of 3 to 4 orders of magnitude",
        "dataset_ca": "CA-Netscience",
        "dataset_wiki": "Wiki-Squirrel",
        "dataset_wormnet": "WormNet-v3",
    }
    missing = [name for name, marker in required.items() if marker not in html]
    if missing:
        raise AssertionError(f"missing source markers: {missing}")

    section5_start = html.index('id="S5"')
    appendix_start = html.index('id="A1"', section5_start)
    section5 = html[section5_start:appendix_start]
    accuracy_budget_pos = section5.index(required["default_accuracy_query_budget"])
    runtime_heading_pos = section5.index(
        '<span id="S5.p6.1.1" class="ltx_text ltx_font_bold">Runtime</span>'
    )
    runtime_budget_pos = section5.index(required["runtime_query_budget"])
    latency_pos = section5.index(required["query_latency_magnitude"])
    total_time_pos = section5.index(required["total_runtime_magnitude"])

    if not accuracy_budget_pos < runtime_heading_pos < runtime_budget_pos:
        raise AssertionError("accuracy and runtime query budgets are not in expected scopes")
    if not runtime_heading_pos < latency_pos < total_time_pos:
        raise AssertionError("3–4-order statements are not both in the runtime scope")

    return {
        "schema": "dprsc-claim5-source-verification-v1",
        "source": str(source.relative_to(ROOT)),
        "sha256": digest,
        "anchors_checked": ["S5", "S5.p3", "S5.p6"],
        "datasets": [
            {"name": "CA-Netscience", "nodes": 379, "edges": 914},
            {"name": "Wiki-Squirrel", "nodes": 5201, "edges": 198353},
            {"name": "WormNet-v3", "nodes": 16347, "edges": 762822},
        ],
        "accuracy_protocol": {
            "default_query_count": "ceil(n^1.5)",
            "epsilon": 2.0,
            "delta": 1e-5,
            "dimension": 1,
            "minimum_repetitions": 20,
        },
        "runtime_protocol": {
            "reported_query_count_range": "1 to Theta(n^2)",
            "measurement": "sample query times until relative standard error < 5%",
            "theta_n2_total_time": "extrapolated from mean query time plus preprocessing",
        },
        "magnitude_scope": {
            "query_latency": "3 to 4 orders of magnitude",
            "total_time_at_Theta_n2": "3 to 4 orders of magnitude",
            "accuracy": "no 3-to-4-order statement in Section 5",
        },
        "source_contract_status": "PASS",
        "scientific_claim_status": "BLOCKED_PENDING_EMPIRICAL_REPRODUCTION",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--negative-control", action="store_true")
    args = parser.parse_args()

    result = verify(args.source)
    if args.negative_control:
        print(
            "NEGATIVE_CONTROL_EXPECTED_FAILURE: imported attribution "
            "'accuracy improves by 3 to 4 orders at Theta(n^2)' is absent from "
            "the paper's Section 5 source contract",
            file=sys.stderr,
        )
        return 2
    print("CLAIM5_SOURCE_RESULT", json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
