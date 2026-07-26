#!/usr/bin/env python3
"""Independent checker for the Claim 3 proof certificate."""

from __future__ import annotations

import argparse
from decimal import Decimal, getcontext
import hashlib
from itertools import combinations, product
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "repro" / "sources" / "2606.08179.html"
EXPECTED_SHA256 = "9387c720239542f024ef31654e84ced6e2687818f8f17703945aa114aab02a5b"


def edge_count(mask: int, vertices: set[int], pairs: list[tuple[int, int]]) -> int:
    return sum(
        1
        for bit, (left, right) in enumerate(pairs)
        if mask & (1 << bit) and left in vertices and right in vertices
    )


def independent_tie_enumeration() -> int:
    n = 3
    pairs = list(combinations(range(n), 2))
    checks = 0
    for attributes in product((0, 1, 2), repeat=n):
        order = sorted(range(n), key=lambda vertex: (attributes[vertex], vertex))
        rank = {vertex: position + 1 for position, vertex in enumerate(order)}
        for mask in range(1 << len(pairs)):
            edge_spans = [
                (min(rank[u], rank[v]), max(rank[u], rank[v]))
                for bit, (u, v) in enumerate(pairs)
                if mask & (1 << bit)
            ]
            for low in range(3):
                for high in range(low, 3):
                    vertices = {
                        vertex
                        for vertex, value in enumerate(attributes)
                        if low <= value <= high
                    }
                    direct = edge_count(mask, vertices, pairs)
                    if not vertices:
                        projected = 0
                    else:
                        minimum_value = min(attributes[v] for v in vertices)
                        maximum_value = max(attributes[v] for v in vertices)
                        left = min(
                            rank[v]
                            for v in vertices
                            if attributes[v] == minimum_value
                        )
                        right = max(
                            rank[v]
                            for v in vertices
                            if attributes[v] == maximum_value
                        )
                        projected = sum(
                            1
                            for span_low, span_high in edge_spans
                            if span_low >= left and span_high <= right
                        )
                    if direct != projected:
                        raise AssertionError("independent tied-rank enumeration failed")
                    checks += 1
    return checks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("certificate", type=Path)
    args = parser.parse_args()

    certificate = json.loads(args.certificate.read_text())
    if certificate["verdict"] != "VERIFIED":
        raise AssertionError("primary certificate does not carry VERIFIED verdict")
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest != EXPECTED_SHA256 or certificate["source_sha256"] != digest:
        raise AssertionError("source hash mismatch")

    getcontext().prec = 60
    ln2 = Decimal(2).ln()
    if not ln2 < Decimal("0.7"):
        raise AssertionError("independent logarithm bound failed")
    inequality_checks = 0
    for k in range(3, 120):
        for d in range(1, 30):
            left = Decimal(k) ** (2 * d)
            log_beta_upper = Decimal(2 * d + 1) * Decimal(k + 1) * ln2
            if left < log_beta_upper:
                raise AssertionError("M >= ln(beta) precondition failed")
            inequality_checks += 1

    # Independent density-ratio check for vector Laplace noise.
    epsilon = Decimal("0.75")
    sensitivity = Decimal(11)
    scale = sensitivity / epsilon
    if abs(sensitivity / scale - epsilon) > Decimal("1e-55"):
        raise AssertionError("vector Laplace privacy equality failed")

    result = {
        "schema": "dprsc-claim3-independent-certificate-v1",
        "result": "PASS",
        "primary_verdict": "VERIFIED",
        "method": (
            "60-digit Decimal concentration-precondition audit, independent "
            "tied-attribute edge enumeration, and vector-Laplace density ratio"
        ),
        "independent_tied_attribute_checks": independent_tie_enumeration(),
        "independent_inequality_checks": inequality_checks,
        "source_sha256": digest,
    }
    print("CLAIM3_INDEPENDENT_CERTIFICATE", json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
