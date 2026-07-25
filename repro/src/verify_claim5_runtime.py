#!/usr/bin/env python3
"""Independent decision checker for the Claim 5 adaptive runtime record."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


EXPECTED = {
    "ca-netscience": (379, 914),
    "musae-squirrel": (5201, 198353),
    "bio-WormNet-v3": (16347, 762822),
}
PATTERNS = {"edge", "2star", "triangle"}


def verify(record: dict[str, object], negative_control: bool) -> dict[str, object]:
    if record["schema"] != "dprsc-claim5-runtime-v1":
        raise AssertionError("wrong schema")
    datasets = record["datasets"]
    if {item["dataset"] for item in datasets} != set(EXPECTED):  # type: ignore[index]
        raise AssertionError("three-dataset coverage is incomplete")
    checks = 0
    large_dataset_latency_lower = []
    for item in datasets:  # type: ignore[union-attr]
        name = item["dataset"]
        n, edges = EXPECTED[name]
        if item["nodes"] != n or item["unique_edges"] != edges:
            raise AssertionError(f"{name}: cardinality mismatch")
        if item["distinct_query_domain_size"] != n * (n + 1) // 2:
            raise AssertionError(f"{name}: domain is not the full Theta(n^2) interval set")
        summaries = [item["proposed_query"]["summary"]] + [
            entry["summary"] for entry in item["baselines"].values()
        ]
        for summary in summaries:
            rse = float(summary["relative_standard_error"])
            if negative_control:
                rse = 0.06
            if not (math.isfinite(rse) and rse < 0.05):
                raise AssertionError(f"{name}: RSE gate failed ({rse})")
            if summary["samples"] < 30:
                raise AssertionError(f"{name}: sample floor failed")
            if not (
                0
                <= summary["ci95_low_seconds"]
                <= summary["mean_seconds"]
                <= summary["ci95_high_seconds"]
            ):
                raise AssertionError(f"{name}: invalid confidence interval")
            checks += 1
        if {row["pattern"] for row in item["comparisons"]} != PATTERNS:
            raise AssertionError(f"{name}: pattern coverage incomplete")
        for row in item["comparisons"]:
            for field in ("query_latency_speedup", "total_at_n", "total_at_all_distinct_theta_n2"):
                values = row[field]
                if not all(
                    math.isfinite(float(value)) and float(value) >= 0
                    for value in values.values()
                ):
                    raise AssertionError((name, row["pattern"], field))
            if name != "ca-netscience":
                large_dataset_latency_lower.append(
                    row["query_latency_speedup"]["ci95_conservative_low"]
                )
    return {
        "status": "PASS",
        "timing_summary_checks": checks,
        "all_rse_below_5_percent": True,
        "minimum_large_dataset_query_speedup_lower": min(
            large_dataset_latency_lower
        ),
        "large_dataset_three_order_gate": min(large_dataset_latency_lower) >= 1000,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=Path)
    parser.add_argument("--negative-control", action="store_true")
    args = parser.parse_args()
    try:
        result = verify(json.loads(args.record.read_text()), args.negative_control)
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        print(json.dumps({"status": "FAIL", "reason": str(exc)}, sort_keys=True))
        raise SystemExit(2)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
