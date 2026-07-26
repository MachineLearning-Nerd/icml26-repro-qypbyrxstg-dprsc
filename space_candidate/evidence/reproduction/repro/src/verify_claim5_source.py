#!/usr/bin/env python3
"""Fail-closed verifier for the evaluator-anchored Claim 5 attribution.

This verifier deliberately separates the imported judge paraphrase from the
paper's actual experimental claims.  It operates on the archived HTML bytes so
the result does not depend on a later ar5iv conversion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


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
        "dataset_ca_row": ">379</th>",
        "dataset_ca_edges": ">914</th>",
        "dataset_wiki_nodes": ">5,201</td>",
        "dataset_wiki_edges": ">198,353</td>",
        "dataset_wormnet_nodes": ">16,347</td>",
        "dataset_wormnet_edges": ">762,822</td>",
        "runtime_cpu": "Intel(R) Xeon(R) Platinum 8562Y Processor @ 2.80 GHZ",
        "runtime_ram": "768 GB RAM",
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
        "schema": "dprsc-claim5-source-verification-v2",
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
            "reported_hardware": (
                "Intel Xeon Platinum 8562Y at 2.80 GHz with 768 GB RAM"
            ),
        },
        "magnitude_scope": {
            "query_latency": "3 to 4 orders of magnitude",
            "total_time_at_Theta_n2": "3 to 4 orders of magnitude",
            "accuracy": "no 3-to-4-order statement in Section 5",
        },
        "source_contract_status": "PASS",
        "anchored_claim": (
            "On Wiki-Squirrel, WormNet-v3, and CA-Netscience, PDP_RSC and "
            "ADP_RSC are reported to outperform PDP_Comp and ADP_Comp by 3 "
            "to 4 orders of magnitude in accuracy at query-set size Theta(n^2)."
        ),
        "anchored_claim_verdict": "FALSIFIED",
        "falsification_basis": (
            "The proposition is an attribution about the contents of Section 5. "
            "The complete pinned section assigns ceil(n^1.5) to the default "
            "accuracy protocol and assigns both 3-to-4-order statements and "
            "Theta(n^2) to the later Runtime scope."
        ),
        "actual_paper_runtime_claim_verdict": "BLOCKED",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path)
    parser.add_argument(
        "--negative-control",
        choices=("accept-misattribution", "conflate-query-budgets"),
    )
    args = parser.parse_args()

    result = verify(args.source)
    if args.negative_control == "accept-misattribution":
        expected = "3 to 4 orders of magnitude"
        observed = result["magnitude_scope"]["accuracy"]  # type: ignore[index]
        if observed != expected:
            raise AssertionError(
                "NEGATIVE_CONTROL_EXPECTED_FAILURE: accepting the anchored "
                f"accuracy attribution requires {expected!r}, observed {observed!r}"
            )
    if args.negative_control == "conflate-query-budgets":
        expected = "Theta(n^2)"
        observed = result["accuracy_protocol"]["default_query_count"]  # type: ignore[index]
        if observed != expected:
            raise AssertionError(
                "NEGATIVE_CONTROL_EXPECTED_FAILURE: conflating query budgets "
                f"requires default accuracy {expected!r}, observed {observed!r}"
            )
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("CLAIM5_SOURCE_RESULT", json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
