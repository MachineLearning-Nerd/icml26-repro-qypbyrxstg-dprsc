#!/usr/bin/env python3
"""Independent fail-closed checker for the Claim 1 four-route record."""

from __future__ import annotations

import argparse
from decimal import Decimal, getcontext
import hashlib
import json
from pathlib import Path


PAPER_SHA256 = "9387c720239542f024ef31654e84ced6e2687818f8f17703945aa114aab02a5b"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=Path)
    parser.add_argument("--paper", type=Path, required=True)
    args = parser.parse_args()

    record = json.loads(args.record.read_text())
    if record.get("schema") != "dprsc-claim1-four-route-audit-v1":
        raise AssertionError("unexpected Claim 1 record schema")
    if record.get("exact_verdict") != "BLOCKED" or record.get("confidence") != "LOW":
        raise AssertionError("Claim 1 must remain BLOCKED/LOW")
    routes = record.get("routes")
    if not isinstance(routes, list) or [route.get("route") for route in routes] != [1, 2, 3, 4]:
        raise AssertionError("expected the three verification routes plus route 4")
    if hashlib.sha256(args.paper.read_bytes()).hexdigest() != PAPER_SHA256:
        raise AssertionError("paper source hash mismatch")

    empirical = routes[1]
    summaries = empirical.get("summaries")
    if not isinstance(summaries, list) or len(summaries) != 3 * 3 * 4:
        raise AssertionError("expected 36 full-scale calibration summaries")
    if {row["query_count"] for row in summaries} != {7379, 375086, 2090053}:
        raise AssertionError("paper-default query budgets are missing")
    if any(row["repetitions"] != 20 for row in summaries):
        raise AssertionError("paper-required 20 repetitions are missing")
    if any(not 0 < row["normalized_max_error_max"] < 100 for row in summaries):
        raise AssertionError("invalid normalized maximum-error calibration")

    getcontext().prec = 60
    epsilon = Decimal(2)
    delta = Decimal("0.9")
    edges = Decimal(2)
    epsilon_prime = epsilon / (edges + 1)
    multiplier = max(
        Decimal(2) * (edges * epsilon_prime).exp()
        + edges * epsilon_prime.exp()
        + 1,
        edges * (Decimal(2) * epsilon_prime).exp()
        + epsilon_prime.exp()
        + 2,
    )
    negative_probability = delta / multiplier / 2
    if not negative_probability > Decimal(1) / Decimal(100):
        raise AssertionError("independent falsification point does not exceed 1/n")
    falsification = routes[3]
    matching = [
        row
        for row in falsification["sweep"]
        if row["epsilon"] == 2.0 and row["delta"] == 0.9 and row["n"] == 100
    ]
    if len(matching) != 1 or not matching[0]["exceeds_failure_budget"]:
        raise AssertionError("falsification grid is missing the independent witness")
    if falsification.get("status") != "WITNESS_FALSIFIED_EXISTENTIAL_THEOREM_NOT_FALSIFIED":
        raise AssertionError("existential quantifier was handled unsafely")

    print(
        "CLAIM1_INDEPENDENT_AUDIT "
        + json.dumps(
            {
                "result": "PASS",
                "verdict": "BLOCKED",
                "confidence": "LOW",
                "routes": 4,
                "full_scale_summaries": len(summaries),
                "decimal_negative_probability_eps2_delta0.9": str(
                    negative_probability
                ),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
