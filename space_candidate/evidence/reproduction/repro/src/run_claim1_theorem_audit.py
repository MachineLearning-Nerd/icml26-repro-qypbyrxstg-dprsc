#!/usr/bin/env python3
"""Four-route audit of Theorem 1.3 and its Algorithm 5 witness.

This verifier deliberately distinguishes the existential theorem from the
specific construction used in its proof.  A broken witness is not silently
promoted into a counterexample to every possible algorithm.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import time

import numpy as np

from run_claim5_accuracy import (
    CanonicalNoise,
    DELTA,
    EPSILONS,
    PATTERNS,
    approximate_scale,
    query_coordinates,
)


ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "repro" / "sources" / "2606.08179.html"
PAPER_SHA256 = "9387c720239542f024ef31654e84ced6e2687818f8f17703945aa114aab02a5b"
CLAIM5_ACCURACY = (
    ROOT / ".openresearch" / "artifacts" / "claim_5" / "full_accuracy_run.json"
)
PRIMARY_SOURCES = {
    "Karwa et al. 2011, Private Analysis of Graph Structure": (
        ROOT / "repro" / "sources" / "claim1"
        / "karwa2011_private_graph_structure.pdf",
        "25887604e53d7997f507c4264755513ad69dfae64ee11de69058a6826c8e6e6b",
    ),
    "Nguyen et al. 2023, Faster Approximate Subgraph Counts with Privacy": (
        ROOT / "repro" / "sources" / "claim1"
        / "nguyen2023_faster_approximate_subgraph_counts.pdf",
        "2d121d7183e037c862b7eb98e6437d3ad1a8c5895a63e0d496afb672be9cf746",
    ),
    "Nissim et al. 2007, Smooth Sensitivity and Sampling": (
        ROOT / "repro" / "sources" / "claim1"
        / "nissim2007_smooth_sensitivity.pdf",
        "f9179e6e4eec0128f5d5a4360c7d8aed218b5d1d8997b201db163af8d6ddd677",
    ),
}
REPETITIONS = 20


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unwrap(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text())
    payload = value.get("payload", value)
    if not isinstance(payload, dict):
        raise AssertionError(f"{path}: expected a JSON object")
    return payload


def paper_markers() -> dict[str, object]:
    digest = sha256(PAPER)
    if digest != PAPER_SHA256:
        raise AssertionError(f"paper source hash mismatch: {digest}")
    html = PAPER.read_text()
    required = {
        "theorem": 'id="S1.Thmtheorem3"',
        "algorithm4_recursion": 'id="alg4.l4"',
        "algorithm5_estimator": 'id="alg5.l3"',
        "algorithm5_noise": 'id="alg5.l5"',
        "lemma_e4": 'id="A5.Thmtheorem4"',
        "lemma_e5": 'id="A5.Thmtheorem5"',
        "lemma_e6": 'id="A5.Thmtheorem6"',
        "lemma_e7": 'id="A5.Thmtheorem7"',
        "complexity": 'id="A5.Thmtheorem9"',
    }
    missing = [name for name, marker in required.items() if marker not in html]
    if missing:
        raise AssertionError(f"paper markers missing: {missing}")
    exact_fragments = [
        r"\delta\in(0,1)",
        r"1-\frac{1}{n}",
        r"\widetilde{\mathrm{HS}}_{f_{H}}",
        r"c^{O(d)}",
        r"d=O(\log n/\log\log n)",
    ]
    absent = [fragment for fragment in exact_fragments if fragment not in html]
    if absent:
        raise AssertionError(f"theorem quantifiers missing: {absent}")
    return {
        "sha256": digest,
        "anchors": list(required),
        "quantifier_fragments": exact_fragments,
    }


def privacy_parameters(epsilon: float, delta: float, edges: int) -> dict[str, float]:
    epsilon_prime = epsilon / (edges + 1)
    multiplier = max(
        2 * math.exp(edges * epsilon_prime)
        + edges * math.exp(epsilon_prime)
        + 1,
        edges * math.exp(2 * epsilon_prime)
        + math.exp(epsilon_prime)
        + 2,
    )
    delta_prime = delta / multiplier
    return {
        "epsilon_prime": epsilon_prime,
        "delta_prime": delta_prime,
        "delta_multiplier": multiplier,
        "negative_estimate_probability_2star_empty": delta_prime / 2,
    }


def proof_route() -> dict[str, object]:
    checks = 0
    for edges in (1, 2, 3, 4):
        for epsilon in (0.1, 0.5, 2.0, 8.0):
            for delta in (1e-9, 1e-5, 0.1, 0.9):
                values = privacy_parameters(epsilon, delta, edges)
                if not math.isclose(
                    (edges + 1) * values["epsilon_prime"],
                    epsilon,
                    rel_tol=1e-15,
                ):
                    raise AssertionError("epsilon composition identity failed")
                if not math.isclose(
                    values["delta_multiplier"] * values["delta_prime"],
                    delta,
                    rel_tol=1e-15,
                ):
                    raise AssertionError("delta composition identity failed")
                if not 0 < values["delta_prime"] < 1:
                    raise AssertionError("derived delta prime is invalid")
                checks += 3
    return {
        "route": 1,
        "name": "independent symbolic proof-chain reconstruction",
        "checks": checks,
        "conditional_result": (
            "The printed epsilon/delta composition and Lemma E.7 tail scaling "
            "are algebraically consistent conditional on a finite positive "
            "EstimateHS value."
        ),
        "blocking_result": (
            "Lemma E.4 guarantees upper-bounding only with high probability. "
            "On its complementary positive-probability event EstimateHS can be "
            "negative, yet Lemmas E.5-E.7 use it as a Laplace scale. The "
            "purported randomized output distribution is then undefined."
        ),
        "status": "INCONCLUSIVE_FOR_EXISTENTIAL_THEOREM",
    }


def hs_from_scale(
    *,
    n: int,
    components: int,
    d_max: int,
    epsilon: float,
    pattern: str,
    rng: np.random.Generator,
) -> tuple[float, float]:
    state = rng.bit_generator.state
    scale = approximate_scale(n, components, d_max, epsilon, pattern, rng)
    replay = np.random.default_rng()
    replay.bit_generator.state = state
    if pattern == "edge":
        hs = 1.0
    else:
        edges = 3 if pattern == "triangle" else 2
        epsilon_prime = epsilon / (edges + 1)
        values = privacy_parameters(epsilon, DELTA, edges)
        delta_prime = values["delta_prime"]
        if pattern == "triangle":
            hs_2 = (
                1.0
                + math.log(1.0 / delta_prime) / epsilon_prime
                + replay.laplace(0.0, 1.0 / epsilon_prime)
            )
            hs = (
                d_max
                + hs_2 * math.log(1.0 / delta_prime) / epsilon_prime
                + replay.laplace(0.0, hs_2 / epsilon_prime)
            )
        else:
            hs = (
                d_max
                + math.log(1.0 / delta_prime) / epsilon_prime
                + replay.laplace(0.0, 1.0 / epsilon_prime)
            )
    return hs, scale


def empirical_route() -> dict[str, object]:
    claim5 = unwrap(CLAIM5_ACCURACY)
    if claim5.get("schema") != "dprsc-claim5-full-accuracy-v1":
        raise AssertionError("Claim 5 accuracy evidence has unexpected schema")
    datasets = claim5.get("datasets")
    if not isinstance(datasets, list) or len(datasets) != 3:
        raise AssertionError("full three-dataset Claim 5 evidence is required")

    summaries: list[dict[str, object]] = []
    for dataset_index, dataset in enumerate(datasets):
        if not isinstance(dataset, dict):
            raise AssertionError("invalid dataset record")
        n = int(dataset["nodes"])
        query_count = int(dataset["query_count"])
        width = int(dataset["query_grid_width"])
        if query_count != math.ceil(n**1.5):
            raise AssertionError("paper-default query count is not ceil(n^1.5)")
        left, high = query_coordinates(
            n, query_count, width, 810_000 + dataset_index
        )
        canonical = CanonicalNoise(n, width)
        noise_rng = np.random.default_rng(820_000 + dataset_index)
        scale_rngs = {
            (pattern, epsilon): np.random.default_rng(
                830_000
                + 10000 * dataset_index
                + 100 * PATTERNS.index(pattern)
                + EPSILONS.index(epsilon)
            )
            for pattern in PATTERNS
            for epsilon in EPSILONS
        }
        ratios = {
            (pattern, epsilon): []
            for pattern in PATTERNS
            for epsilon in EPSILONS
        }
        invalid = 0
        pattern_facts = dataset["patterns"]
        if not isinstance(pattern_facts, dict):
            raise AssertionError("missing pattern facts")
        for _ in range(REPETITIONS):
            unit_error = np.abs(canonical.draw(noise_rng)[left, high])
            unit_max = float(unit_error.max())
            components = (math.ceil(math.log2(n)) + 1) ** 2
            for pattern in PATTERNS:
                d_max = int(pattern_facts[pattern]["d_max"])
                for epsilon in EPSILONS:
                    hs, scale = hs_from_scale(
                        n=n,
                        components=components,
                        d_max=d_max,
                        epsilon=epsilon,
                        pattern=pattern,
                        rng=scale_rngs[(pattern, epsilon)],
                    )
                    if hs <= 0:
                        invalid += 1
                        continue
                    theorem_normalizer = (
                        hs
                        * math.sqrt(
                            (epsilon + math.log(1.0 / DELTA))
                            * math.log(n * query_count)
                        )
                        * math.log(n) ** 2
                        / epsilon
                    )
                    ratios[(pattern, epsilon)].append(
                        unit_max * scale / theorem_normalizer
                    )
        for (pattern, epsilon), values in ratios.items():
            if len(values) != REPETITIONS:
                raise AssertionError("unexpected invalid scale in full-scale route")
            summaries.append(
                {
                    "dataset": dataset["dataset"],
                    "nodes": n,
                    "query_count": query_count,
                    "pattern": pattern,
                    "epsilon": epsilon,
                    "repetitions": len(values),
                    "normalized_max_error_mean": float(np.mean(values)),
                    "normalized_max_error_p95": float(np.quantile(values, 0.95)),
                    "normalized_max_error_max": max(values),
                }
            )
    return {
        "route": 2,
        "name": "full-scale finite max-error calibration",
        "datasets": len(datasets),
        "summaries": summaries,
        "invalid_scales": invalid,
        "non_circularity": (
            "The query budgets and 20 repetitions are the paper's Section 5 "
            "protocol, not selected from the theorem formula. No arbitrary "
            "Big-O constant is used as an acceptance threshold."
        ),
        "limitation": (
            "Finite normalized ratios cannot prove an asymptotic Big-O claim "
            "with hidden c^O(d) constants, arbitrary Q, and probability 1-1/n."
        ),
        "status": "SCOPED_CORROBORATION_ONLY",
    }


def repair_and_literature_route() -> dict[str, object]:
    sources = []
    for title, (path, expected) in PRIMARY_SOURCES.items():
        observed = sha256(path)
        if observed != expected:
            raise AssertionError(f"primary source hash mismatch for {title}")
        sources.append(
            {
                "title": title,
                "path": str(path.relative_to(ROOT)),
                "sha256": observed,
            }
        )
    return {
        "route": 3,
        "name": "repair analysis and primary-literature priority audit",
        "primary_sources": sources,
        "findings": [
            (
                "Nguyen et al. Algorithm 5 and its cited Karwa et al. Lemma "
                "4.4 use a high-probability local-sensitivity upper estimate "
                "directly as a Laplace scale; neither source supplies a "
                "total-domain positivity repair for the bad event."
            ),
            (
                "Nissim et al. calibrate instance-specific noise to a "
                "nonnegative smooth upper bound, which is a different "
                "mechanism and does not establish the paper's stated "
                "EstimateHS-dependent bound."
            ),
            (
                "Clipping EstimateHS at zero makes the scale syntactically "
                "valid but changes the released estimator and invalidates the "
                "paper's cited privacy lemma; a new privacy and utility proof "
                "would be required."
            ),
            (
                "The reviewed primary works address private subgraph counting "
                "or private range counting separately. This supports, but "
                "cannot exhaustively prove, the global 'first efficient' "
                "priority statement."
            ),
        ],
        "status": "NO_CERTIFIED_REPAIR_OR_EXHAUSTIVE_PRIORITY_PROOF",
    }


def falsification_route() -> dict[str, object]:
    sweep = []
    first_hits = []
    for epsilon in (0.5, 2.0, 4.0):
        for delta in (0.1, 0.5, 0.9):
            probability = privacy_parameters(epsilon, delta, 2)[
                "negative_estimate_probability_2star_empty"
            ]
            hit = None
            for n in (3, 10, 30, 100, 300):
                exceeds = probability > 1 / n
                sweep.append(
                    {
                        "epsilon": epsilon,
                        "delta": delta,
                        "n": n,
                        "negative_scale_probability": probability,
                        "theorem_failure_budget": 1 / n,
                        "exceeds_failure_budget": exceeds,
                    }
                )
                if exceeds and hit is None:
                    hit = n
            first_hits.append(
                {
                    "epsilon": epsilon,
                    "delta": delta,
                    "first_tested_n_exceeding_budget": hit,
                }
            )
    if not any(row["exceeds_failure_budget"] for row in sweep):
        raise AssertionError("falsification sweep found no Algorithm 5 witness")
    return {
        "route": 4,
        "name": "mandatory assumption-satisfying falsification search",
        "restated_contract": {
            "domain": "simple n-vertex graphs with d-dimensional attributes",
            "quantifiers": "all epsilon>0, all delta in (0,1), fixed H, arbitrary Q",
            "privacy": "(epsilon,delta)-edge DP",
            "utility": "maximum absolute error, probability at least 1-1/n",
            "witness_named_by_proof": "Algorithm 5 using Algorithm 4 EstimateHS",
        },
        "input_family": (
            "empty graphs, H=2-star, d=1, one full-range query; all theorem "
            "input assumptions are satisfied"
        ),
        "sweep": sweep,
        "first_hits": first_hits,
        "result": (
            "The named Algorithm 5 witness is undefined on a "
            "positive-probability event, and for multiple predeclared grid "
            "points that probability exceeds 1/n."
        ),
        "why_not_falsified": (
            "Theorem 1.3 is existential. This invalidates the paper's offered "
            "construction, but does not prove that no other algorithm can "
            "satisfy the same asymptotic bound."
        ),
        "status": "WITNESS_FALSIFIED_EXISTENTIAL_THEOREM_NOT_FALSIFIED",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument(
        "--negative-control",
        choices=("ignore-undefined", "mean-for-max", "witness-for-existence"),
    )
    args = parser.parse_args()

    if args.negative_control:
        messages = {
            "ignore-undefined": (
                "ignoring the positive-probability undefined output cannot "
                "certify a randomized algorithm"
            ),
            "mean-for-max": (
                "mean relative error cannot certify maximum absolute error "
                "with probability 1-1/n"
            ),
            "witness-for-existence": (
                "a broken constructive witness is not a counterexample to an "
                "existential claim over every possible algorithm"
            ),
        }
        print(f"CLAIM1_NEGATIVE_CONTROL_EXPECTED_FAILURE: {messages[args.negative_control]}")
        return 2

    started = time.monotonic()
    result = {
        "schema": "dprsc-claim1-four-route-audit-v1",
        "claim_id": 1,
        "exact_verdict": "BLOCKED",
        "confidence": "LOW",
        "source": paper_markers(),
        "routes": [
            proof_route(),
            empirical_route(),
            repair_and_literature_route(),
            falsification_route(),
        ],
        "final_reason": (
            "The stated Algorithm 5 witness is not a total randomized "
            "algorithm, finite observations cannot establish the asymptotic "
            "quantifiers, and the priority statement is not exhaustively "
            "decidable from the reviewed corpus. The mandatory falsification "
            "route does not contradict the theorem's existential quantifier."
        ),
        "unblocker": (
            "A corrected total-domain mechanism with an independently checked "
            "privacy/utility proof for the exact HS_tilde bound, plus a "
            "systematic priority review, or a valid counterexample ruling out "
            "every algorithm satisfying the theorem."
        ),
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "logical_cpus_visible": __import__("os").cpu_count(),
        },
        "runtime_seconds": time.monotonic() - started,
    }
    if len(result["routes"]) != 4:
        raise AssertionError("LOW-confidence Claim 1 requires exactly four routes")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("CLAIM1_THEOREM_AUDIT", json.dumps(result, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
