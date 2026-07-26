#!/usr/bin/env python3
"""Assumption-satisfying counterexample to Algorithm 4/5 well-definedness."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "repro" / "sources" / "2606.08179.html"
EXPECTED_SHA256 = "9387c720239542f024ef31654e84ced6e2687818f8f17703945aa114aab02a5b"


def parameters(epsilon: float, delta: float, pattern_edges: int) -> dict[str, float]:
    epsilon_prime = epsilon / (pattern_edges + 1)
    multiplier = max(
        2 * math.exp(pattern_edges * epsilon_prime)
        + pattern_edges * math.exp(epsilon_prime)
        + 1,
        pattern_edges * math.exp(2 * epsilon_prime)
        + math.exp(epsilon_prime)
        + 2,
    )
    delta_prime = delta / multiplier
    negative_probability = delta_prime / 2
    threshold = math.log(1 / delta_prime) / epsilon_prime
    return {
        "epsilon_prime": epsilon_prime,
        "delta_prime": delta_prime,
        "delta_multiplier": multiplier,
        "negative_threshold": threshold,
        "negative_probability": negative_probability,
    }


def implementation_check(values: dict[str, float]) -> dict[str, object]:
    sys.path.insert(0, str(ROOT / "upstream"))
    preprocessing = importlib.import_module("preprocessing")
    range_tree = importlib.import_module("range_tree")

    original_laplace = preprocessing.np.random.laplace
    forced_draw = -values["negative_threshold"] - 1.0
    preprocessing.np.random.laplace = lambda *_args, **_kwargs: forced_draw
    try:
        magnitude = preprocessing.approx_DP_mag(
            n=3,
            comp_num=1,
            d_max=0,
            eps=2.0,
            delta=1e-5,
            pattern="2star",
        )
    finally:
        preprocessing.np.random.laplace = original_laplace

    if magnitude >= 0:
        raise AssertionError(f"forced valid tail draw did not create negative scale: {magnitude}")
    try:
        range_tree.np.random.laplace(0, magnitude)
    except ValueError as exc:
        observed = type(exc).__name__
    else:
        raise AssertionError("NumPy unexpectedly accepted a negative Laplace scale")
    return {
        "released_code_negative_scale": magnitude,
        "released_code_exception": observed,
        "released_code_path": "preprocessing.approx_DP_mag -> range_tree Laplace node noise",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--clipped-control", action="store_true")
    args = parser.parse_args()

    payload = SOURCE.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != EXPECTED_SHA256:
        raise AssertionError(f"paper source hash mismatch: {digest}")
    html = payload.decode("utf-8")
    required = [
        'id="alg4.l4"',
        r"\mathrm{Lap}(\widetilde{\mathrm{HS}}^{(k+1)}_{f_{H}}(G)/\varepsilon^{\prime})",
        'id="alg5.l3"',
        r"\textsc{EstimateHS}(G,H,\varepsilon^{\prime},\delta^{\prime})",
        'id="S2.Thmtheorem5"',
        r"\mathrm{Lap}(b)=\frac{1}{2b}e^{-\frac{|x|}{b}}",
    ]
    missing = [marker for marker in required if marker not in html]
    if missing:
        raise AssertionError(f"counterexample source markers missing: {missing}")

    values = parameters(epsilon=2.0, delta=1e-5, pattern_edges=2)
    if not 0 < values["delta_prime"] < 1:
        raise AssertionError("derived delta' is outside the Laplace-tail domain")
    if not values["negative_probability"] > 0:
        raise AssertionError("counterexample event does not have positive probability")

    # Empty 3-vertex graph, H=2-star: f_H^(2)(G)=1 and f_H^(1)(G)=0.
    # EstimateHS therefore returns log(1/delta')/epsilon' + Lap(1/epsilon').
    # Its negative tail has exact probability delta'/2.
    inverse_cdf_u = values["negative_probability"] / 2
    inverse_cdf_draw = math.log(2 * inverse_cdf_u) / values["epsilon_prime"]
    constructed_output = values["negative_threshold"] + inverse_cdf_draw
    if not constructed_output < 0:
        raise AssertionError("independent inverse-CDF witness is not negative")

    if args.clipped_control:
        clipped = max(0.0, constructed_output)
        if clipped < 0:
            raise AssertionError("clipped repair remained negative")
        print(
            "CLIPPED_CONTROL_EXPECTED_FAILURE: clipping removes the negative-scale "
            "counterexample, so the counterexample checker correctly rejects it",
            file=sys.stderr,
        )
        return 2

    implementation = implementation_check(values)
    result = {
        "schema": "dprsc-claim4-counterexample-v1",
        "verdict": "FALSIFIED",
        "claim_scope": "Algorithm 5 attains Theorem 1.3 by using Algorithm 4 EstimateHS",
        "assumption_satisfying_input": {
            "graph": "empty simple graph on 3 vertices",
            "pattern": "2-star",
            "dimension": 1,
            "query_set": "one full-range query",
            "epsilon": 2.0,
            "delta": 1e-5,
            "f_H^(2)(G)": 1,
            "f_H^(1)(G)": 0,
        },
        "derived": values,
        "analytic_witness": {
            "event": "EstimateHS < 0",
            "exact_probability": "delta_prime / 2",
            "inverse_cdf_u": inverse_cdf_u,
            "constructed_estimate_hs": constructed_output,
        },
        "contradiction": (
            "Algorithm 5 uses the negative EstimateHS value as a Laplace scale; "
            "Definition 2.5 requires a positive scale, so the named randomized "
            "algorithm is undefined on a positive-probability event."
        ),
        "implementation": implementation,
        "source_sha256": digest,
    }
    print("CLAIM4_COUNTEREXAMPLE", json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
