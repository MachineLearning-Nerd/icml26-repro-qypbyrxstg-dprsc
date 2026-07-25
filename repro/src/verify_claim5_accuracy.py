#!/usr/bin/env python3
"""Independent structural/statistical checker for Claim 5 accuracy evidence."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys


EXPECTED = {
    "ca-netscience": (379, 914),
    "musae-squirrel": (5201, 198353),
    "bio-WormNet-v3": (16347, 762822),
}
PATTERNS = {"edge", "2star", "triangle"}
ALGORITHMS = {"PDP_RSC", "ADP_RSC", "PDP_Comp", "ADP_Comp"}
EPSILONS = {x / 10 for x in range(5, 45, 5)}


def verify(record: dict[str, object], negative_control: bool) -> dict[str, object]:
    datasets = record["datasets"]
    assert isinstance(datasets, list)
    if {item["dataset"] for item in datasets} != set(EXPECTED):  # type: ignore[index]
        raise AssertionError("not all three exact datasets are present")
    checks = 0
    for item in datasets:
        name = item["dataset"]
        n, edges = EXPECTED[name]  # type: ignore[index]
        if item["nodes"] != n or item["unique_edges"] != edges:  # type: ignore[index]
            raise AssertionError(f"{name}: graph cardinality mismatch")
        exact_q = math.ceil(n**1.5)
        if negative_control:
            exact_q += 1
        if item["query_count"] != exact_q:  # type: ignore[index]
            raise AssertionError(f"{name}: query count is not ceil(n^1.5)")
        if item["repetitions"] < 20:  # type: ignore[index]
            raise AssertionError(f"{name}: fewer than 20 repetitions")
        if item["dimension"] != 1 or item["delta"] != 1e-5:  # type: ignore[index]
            raise AssertionError(f"{name}: protocol parameters differ")
        rows = item["rows"]  # type: ignore[index]
        if {(row["pattern"], row["epsilon"]) for row in rows} != {  # type: ignore[index]
            (pattern, epsilon) for pattern in PATTERNS for epsilon in EPSILONS
        }:
            raise AssertionError(f"{name}: incomplete pattern/epsilon Cartesian product")
        for row in rows:
            if set(row) != {"pattern", "epsilon"} | ALGORITHMS:  # type: ignore[arg-type]
                raise AssertionError(f"{name}: algorithm columns differ")
            for algorithm in ALGORITHMS:
                mean = row[algorithm]["mean_relative_error"]  # type: ignore[index]
                std = row[algorithm]["standard_deviation"]  # type: ignore[index]
                if not (math.isfinite(mean) and mean >= 0):
                    raise AssertionError((name, algorithm, mean))
                if not (math.isfinite(std) and std >= 0):
                    raise AssertionError((name, algorithm, std))
                checks += 1
        if not all(c["paper_ordering_holds"] for c in item["comparisons"]):  # type: ignore[index]
            raise AssertionError(f"{name}: at least one paper ordering is contradicted")
    return {
        "status": "PASS",
        "dataset_checks": len(datasets),
        "algorithm_statistic_checks": checks,
        "exact_query_budget": True,
        "minimum_repetitions": 20,
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
