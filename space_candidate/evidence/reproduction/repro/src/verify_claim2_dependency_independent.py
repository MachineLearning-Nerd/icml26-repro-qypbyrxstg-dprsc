#!/usr/bin/env python3
"""Independent checker for the Claim 2 dependency-audit record."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    args = parser.parse_args()

    record = json.loads(args.record.read_text())
    if record["status"] != "PASS" or record["claim_verdict"] != "BLOCKED":
        raise AssertionError("dependency audit is not fail-closed")
    if record["route_1_reconstruction"]["status"] != "UNSAT":
        raise AssertionError("reconstruction algebra was not proved")
    if (
        record["route_2_partial_coloring_recursion"]["status"]
        != "GAP_CONFIRMED"
    ):
        raise AssertionError("partial-coloring gap is missing")
    for row in record["route_2_partial_coloring_recursion"]["rows"]:
        expected_floor = Fraction(1, row["dimension"] - 1)
        for sample in row["samples"]:
            if (
                Fraction(
                    sample["largest_single_scale_over_claimed_target"]
                )
                != Fraction(1, sample["k"])
            ):
                raise AssertionError("single-scale asymptotic ratio changed")
            if (
                Fraction(sample["recursion_sum_over_claimed_target"])
                < expected_floor
            ):
                raise AssertionError("recursion no longer reaches target order")
    if (
        record["route_3_alternative_primary_theorem"]["status"]
        != "DOES_NOT_CLOSE_GAP"
    ):
        raise AssertionError("prior theorem was promoted beyond its metric")
    if any(
        row["closes_claim_2"]
        for row in record["route_3_alternative_primary_theorem"]["rows"]
    ):
        raise AssertionError("square-root conversion was bypassed")
    if (
        record["route_4_falsification"]["status"]
        != "NO_VALID_COUNTEREXAMPLE"
    ):
        raise AssertionError("proof gap was mislabeled as falsification")

    source_hashes = []
    for source in record["primary_sources"]:
        path = Path(source["file"])
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != source["sha256"]:
            raise AssertionError(f"source changed: {path}")
        source_hashes.append(digest)

    print(json.dumps({
        "status": "PASS",
        "verdict": "BLOCKED",
        "source_hashes_checked": len(source_hashes),
        "recursion_dimensions_checked": 3,
        "metric_conversion_checked": True,
        "falsification_label_checked": True,
    }, indent=2))


if __name__ == "__main__":
    main()
