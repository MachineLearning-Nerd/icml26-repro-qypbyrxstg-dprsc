#!/usr/bin/env python3
"""Faithful Section 5 adaptive-RSE runtime protocol for Claim 5."""

from __future__ import annotations

import argparse
import importlib
import json
import math
from pathlib import Path
import statistics
import sys
import time
from typing import Callable

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
UPSTREAM = ROOT / "upstream"
sys.path.insert(0, str(UPSTREAM))
find_patterns = importlib.import_module("find_patterns")
range_tree = importlib.import_module("range_tree")

from run_claim5_accuracy import DATASETS, PATTERNS, load_graph, load_ranks  # noqa: E402


MIN_SAMPLES = 30
BATCH_SIZE = 10
MAX_SAMPLES = 2000
RSE_TARGET = 0.05


def load_accuracy(path: Path) -> dict[str, object]:
    record = json.loads(path.read_text())
    if record.get("schema") == "dprsc-orx-log-extract-v1":
        return record["payload"]
    return record


def uniform_distinct_intervals(
    n: int, count: int, seed: int
) -> list[tuple[int, int]]:
    """Exact rejection sampler uniform over {(l,r): 0<=l<=r<n}."""
    rng = np.random.default_rng(seed)
    result: list[tuple[int, int]] = []
    while len(result) < count:
        endpoints = rng.integers(0, n, size=(2 * (count - len(result)), 2))
        for left, right in endpoints:
            if left <= right:
                result.append((int(left), int(right)))
                if len(result) == count:
                    break
    return result


def summarize_times(values: list[float]) -> dict[str, float | int]:
    mean = statistics.fmean(values)
    standard_deviation = statistics.stdev(values)
    standard_error = standard_deviation / math.sqrt(len(values))
    rse = standard_error / mean
    return {
        "samples": len(values),
        "mean_seconds": mean,
        "standard_deviation_seconds": standard_deviation,
        "standard_error_seconds": standard_error,
        "relative_standard_error": rse,
        "ci95_low_seconds": max(0.0, mean - 1.96 * standard_error),
        "ci95_high_seconds": mean + 1.96 * standard_error,
    }


def adaptive_measure(
    function: Callable[[tuple[int, int]], object],
    queries: list[tuple[int, int]],
) -> tuple[dict[str, float | int], list[float]]:
    values: list[float] = []
    for query in queries[:3]:
        function(query)
    for query in queries:
        started = time.perf_counter_ns()
        function(query)
        elapsed = (time.perf_counter_ns() - started) / 1e9
        if elapsed <= 0:
            raise AssertionError("nonpositive query time")
        values.append(elapsed)
        if len(values) >= MIN_SAMPLES and len(values) % BATCH_SIZE == 0:
            summary = summarize_times(values)
            if summary["relative_standard_error"] < RSE_TARGET:
                return summary, values
    return summarize_times(values), values


class ReleasedRangeTreeQuery:
    """Actual released querySplit implementation, prewarmed on timed queries."""

    def __init__(self, n: int, queries: list[tuple[int, int]]) -> None:
        self.n = n
        self.root = None
        for left, right in queries:
            query = [(left, n - 1), (0, right)]
            self.root, _, _ = range_tree.querySplit(
                self.root, 0, n - 1, query, 0, n, 1, 1.0
            )

    def __call__(self, interval: tuple[int, int]) -> float:
        left, right = interval
        query = [(left, self.n - 1), (0, right)]
        self.root, weight, noise = range_tree.querySplit(
            self.root, 0, self.n - 1, query, 0, self.n, 1, 1.0
        )
        return weight + noise


class ReleasedBaselineQuery:
    """Released exact filtering/counting path, with deterministic DP-noise draw."""

    def __init__(
        self,
        edges: list[tuple[int, int]],
        ranks: list[int],
        n: int,
        pattern: str,
        seed: int,
    ) -> None:
        self.edges = edges
        self.ranks = ranks
        self.n = n
        self.pattern = pattern
        self.rng = np.random.default_rng(seed)

    def __call__(self, interval: tuple[int, int]) -> float:
        left, right = interval
        degrees = np.zeros(self.n, dtype=int)
        selected_edges = []
        for u, v in self.edges:
            if (
                left <= self.ranks[u] <= right
                and left <= self.ranks[v] <= right
            ):
                selected_edges.append((u, v))
                degrees[u] += 1
                degrees[v] += 1
        if self.pattern == "triangle":
            answer = find_patterns.enumerate_triangles(
                selected_edges, degrees, self.n
            )
        elif self.pattern == "2star":
            answer = find_patterns.enumerate_2stars(degrees, self.n)
        else:
            answer = len(selected_edges)
        return answer + self.rng.laplace(0.0, 1.0)


def ratio_interval(
    numerator: dict[str, float | int],
    denominator: dict[str, float | int],
) -> dict[str, float]:
    mean = float(numerator["mean_seconds"]) / float(denominator["mean_seconds"])
    low = float(numerator["ci95_low_seconds"]) / float(
        denominator["ci95_high_seconds"]
    )
    high_denominator = float(denominator["ci95_low_seconds"])
    high = (
        float("inf")
        if high_denominator == 0
        else float(numerator["ci95_high_seconds"]) / high_denominator
    )
    return {"mean": mean, "ci95_conservative_low": low, "ci95_conservative_high": high}


def total_ratio(
    query_count: int,
    baseline: dict[str, float | int],
    proposed: dict[str, float | int],
    proposed_preprocessing_upper_seconds: float,
) -> dict[str, float | int]:
    baseline_mean = query_count * float(baseline["mean_seconds"])
    proposed_mean = proposed_preprocessing_upper_seconds + query_count * float(
        proposed["mean_seconds"]
    )
    conservative_baseline = query_count * float(baseline["ci95_low_seconds"])
    conservative_proposed = proposed_preprocessing_upper_seconds + query_count * float(
        proposed["ci95_high_seconds"]
    )
    return {
        "query_count": query_count,
        "baseline_total_mean_seconds": baseline_mean,
        "proposed_total_mean_seconds": proposed_mean,
        "mean_speedup": baseline_mean / proposed_mean,
        "conservative_95_speedup_lower": conservative_baseline
        / conservative_proposed,
    }


def run_dataset(
    dataset: str,
    n: int,
    expected_edges: int,
    accuracy: dict[str, object],
    seed: int,
) -> dict[str, object]:
    started = time.monotonic()
    edges, _, _ = load_graph(dataset, n)
    ranks = load_ranks(dataset, n)
    if len(edges) != expected_edges:
        raise AssertionError((dataset, len(edges), expected_edges))
    queries = uniform_distinct_intervals(n, MAX_SAMPLES, seed)
    if any(not (0 <= left <= right < n) for left, right in queries):
        raise AssertionError("invalid interval sample")
    proposed_query = ReleasedRangeTreeQuery(n, queries)
    proposed_stats, proposed_raw = adaptive_measure(proposed_query, queries)
    baselines: dict[str, object] = {}
    for index, pattern in enumerate(PATTERNS):
        baseline_query = ReleasedBaselineQuery(
            edges, ranks, n, pattern, seed + 100 + index
        )
        baseline_stats, baseline_raw = adaptive_measure(baseline_query, queries)
        baselines[pattern] = {
            "summary": baseline_stats,
            "raw_seconds": baseline_raw,
        }
        print(
            "CLAIM5_RUNTIME_PROGRESS",
            json.dumps(
                {
                    "dataset": dataset,
                    "pattern": pattern,
                    "samples": baseline_stats["samples"],
                    "rse": baseline_stats["relative_standard_error"],
                    "elapsed_seconds": round(time.monotonic() - started, 3),
                },
                sort_keys=True,
            ),
            flush=True,
        )
    preprocessing_upper = float(accuracy["runtime_seconds"]) - float(
        accuracy["simulation_seconds"]
    )
    comparisons = []
    full_distinct_query_count = n * (n + 1) // 2
    for pattern in PATTERNS:
        baseline_stats = baselines[pattern]["summary"]  # type: ignore[index]
        comparisons.append(
            {
                "pattern": pattern,
                "query_latency_speedup": ratio_interval(
                    baseline_stats, proposed_stats  # type: ignore[arg-type]
                ),
                "total_at_n": total_ratio(
                    n,
                    baseline_stats,  # type: ignore[arg-type]
                    proposed_stats,
                    preprocessing_upper,
                ),
                "total_at_all_distinct_theta_n2": total_ratio(
                    full_distinct_query_count,
                    baseline_stats,  # type: ignore[arg-type]
                    proposed_stats,
                    preprocessing_upper,
                ),
            }
        )
    return {
        "dataset": dataset,
        "nodes": n,
        "unique_edges": len(edges),
        "query_distribution": (
            "i.i.d. exact rejection sampling, uniform over all (l,r) with "
            "0<=l<=r<n; unique released attributes make these distinct induced subgraphs"
        ),
        "distinct_query_domain_size": full_distinct_query_count,
        "rse_target": RSE_TARGET,
        "minimum_samples": MIN_SAMPLES,
        "maximum_samples": MAX_SAMPLES,
        "proposed_query": {
            "implementation": "released range_tree.querySplit, fully prewarmed",
            "summary": proposed_stats,
            "raw_seconds": proposed_raw,
        },
        "baselines": baselines,
        "proposed_preprocessing_upper_seconds": preprocessing_upper,
        "preprocessing_upper_basis": (
            "entire full-accuracy dataset runtime minus simulation time; includes "
            "all three projections, sensitivity calculations, data loading, and checks"
        ),
        "baseline_preprocessing_seconds_for_conservative_total": 0.0,
        "comparisons": comparisons,
        "runtime_seconds": time.monotonic() - started,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accuracy", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    accuracy_record = load_accuracy(args.accuracy)
    accuracy_by_dataset = {
        item["dataset"]: item for item in accuracy_record["datasets"]  # type: ignore[index]
    }
    datasets = []
    for index, (dataset, n, edges) in enumerate(DATASETS):
        result = run_dataset(
            dataset,
            n,
            edges,
            accuracy_by_dataset[dataset],
            5260608179 + index * 100_003,
        )
        datasets.append(result)
        print("CLAIM5_RUNTIME_DATASET", json.dumps(result, sort_keys=True), flush=True)
    record = {
        "schema": "dprsc-claim5-runtime-v1",
        "source_anchor": "S5.p6",
        "seeds": [5260608179 + index * 100_003 for index in range(len(DATASETS))],
        "datasets": datasets,
        "all_rse_below_5_percent": all(
            float(dataset["proposed_query"]["summary"]["relative_standard_error"])  # type: ignore[index]
            < RSE_TARGET
            and all(
                float(item["summary"]["relative_standard_error"]) < RSE_TARGET
                for item in dataset["baselines"].values()  # type: ignore[union-attr]
            )
            for dataset in datasets
        ),
        "runtime_seconds": time.monotonic() - started,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print("CLAIM5_RUNTIME_RESULT", json.dumps(record, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
