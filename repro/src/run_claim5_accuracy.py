#!/usr/bin/env python3
"""Full Section 5 accuracy protocol for Claim 5.

This implements the released d=1 projection and range-tree mechanism without
materializing one Python object per query or one Python tuple per 2-star.
For every query, the noisy answer is the sum of the same independent Laplace
variables attached to the canonical 2D range-tree nodes as Algorithm 2.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import platform
import random
import time
from typing import Iterable

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
UPSTREAM = ROOT / "upstream"
EPSILONS = tuple(x / 10 for x in range(5, 45, 5))
DELTA = 1e-5
REPETITIONS = 20
DATASETS = (
    ("ca-netscience", 379, 914),
    ("musae-squirrel", 5201, 198353),
    ("bio-WormNet-v3", 16347, 762822),
)
PATTERNS = ("edge", "2star", "triangle")
ALGORITHMS = ("PDP_RSC", "ADP_RSC", "PDP_Comp", "ADP_Comp")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_graph(dataset: str, n: int) -> tuple[list[tuple[int, int]], list[list[int]], list[int]]:
    path = UPSTREAM / dataset / f"{dataset}_graph.txt"
    edges: set[tuple[int, int]] = set()
    for line in path.read_text().splitlines():
        u, v = map(int, line.split())
        if u == v:
            continue
        edges.add((u, v) if u < v else (v, u))
    adjacency = [[] for _ in range(n)]
    for u, v in sorted(edges):
        adjacency[u].append(v)
        adjacency[v].append(u)
    return sorted(edges), adjacency, [len(row) for row in adjacency]


def load_ranks(dataset: str, n: int) -> list[int]:
    path = UPSTREAM / dataset / f"{dataset}_attribute_d=1.txt"
    values = [float(line.strip().split()[0]) for line in path.read_text().splitlines()[:n]]
    if len(values) != n:
        raise AssertionError(f"{dataset}: expected {n} attributes, found {len(values)}")
    unique = sorted(set(values))
    mapping = {value: rank for rank, value in enumerate(unique)}
    ranks = [mapping[value] for value in values]
    if len(unique) != n:
        raise AssertionError(
            f"{dataset}: released standard-normal attributes contain ties; "
            "the upstream rank domain is not n"
        )
    return ranks


class IntervalAccumulator:
    """Aggregate projected occurrences only at query-relevant extremes."""

    def __init__(self, n: int, width: int) -> None:
        self.n = n
        self.width = width
        self.joint = np.zeros((width, width), dtype=np.uint64)
        self.low_only = np.zeros(width, dtype=np.uint64)
        self.high_only = np.zeros(width, dtype=np.uint64)
        self.neither = 0
        self.total = 0

    def add(self, low: int, high: int, count: int = 1) -> None:
        if count == 0:
            return
        if not (0 <= low <= high < self.n):
            raise AssertionError((low, high, self.n))
        low_key = low if low < self.width else None
        high_index = self.n - 1 - high
        high_key = high_index if high_index < self.width else None
        if low_key is not None and high_key is not None:
            self.joint[low_key, high_key] += count
        elif low_key is not None:
            self.low_only[low_key] += count
        elif high_key is not None:
            self.high_only[high_key] += count
        else:
            self.neither += count
        self.total += count

    def add_low(self, low: int, count: int) -> None:
        if count:
            self.low_only[low] += count
            self.total += count

    def add_high(self, high_index: int, count: int) -> None:
        if count:
            self.high_only[high_index] += count
            self.total += count

    def add_joint_outer(
        self,
        low_counts: Counter[int],
        high_counts: Counter[int],
    ) -> None:
        if not low_counts or not high_counts:
            return
        lows = np.fromiter(low_counts.keys(), dtype=np.intp)
        highs = np.fromiter(high_counts.keys(), dtype=np.intp)
        lv = np.fromiter(low_counts.values(), dtype=np.uint64)
        hv = np.fromiter(high_counts.values(), dtype=np.uint64)
        block = lv[:, None] * hv[None, :]
        self.joint[np.ix_(lows, highs)] += block
        self.total += int(block.sum(dtype=np.uint64))

    def matrix(self) -> np.ndarray:
        joint_suffix = (
            self.joint[::-1, ::-1]
            .cumsum(axis=0, dtype=np.uint64)
            .cumsum(axis=1, dtype=np.uint64)[::-1, ::-1]
        )
        low_suffix = self.low_only[::-1].cumsum(dtype=np.uint64)[::-1]
        high_suffix = self.high_only[::-1].cumsum(dtype=np.uint64)[::-1]
        result = joint_suffix
        result = result + low_suffix[:, None]
        result = result + high_suffix[None, :]
        result = result + np.uint64(self.neither)
        if int(result[0, 0]) != self.total:
            raise AssertionError(
                {"matrix_origin": int(result[0, 0]), "total": self.total}
            )
        return result


def min_pair_distribution(counts: Counter[int]) -> Counter[int]:
    """Counts unordered pairs by the minimum of their integer keys."""
    result: Counter[int] = Counter()
    remaining = sum(counts.values())
    for key in sorted(counts):
        count = counts[key]
        remaining -= count
        result[key] += count * remaining + count * (count - 1) // 2
    return result


def aggregate_edges(
    edges: Iterable[tuple[int, int]], ranks: list[int], n: int, width: int
) -> IntervalAccumulator:
    acc = IntervalAccumulator(n, width)
    for u, v in edges:
        ru, rv = ranks[u], ranks[v]
        acc.add(min(ru, rv), max(ru, rv))
    return acc


def aggregate_2stars(
    adjacency: list[list[int]], ranks: list[int], n: int, width: int
) -> IntervalAccumulator:
    """Exact O(m + sum_v k_low(v)k_high(v)) projected 2-star counter."""
    acc = IntervalAccumulator(n, width)
    high_start = n - width
    for center, neighbors in enumerate(adjacency):
        degree = len(neighbors)
        if degree < 2:
            continue
        c = ranks[center]
        low_neighbors: Counter[int] = Counter()
        high_neighbors: Counter[int] = Counter()
        mid_count = 0
        for vertex in neighbors:
            rank = ranks[vertex]
            if rank < width:
                low_neighbors[rank] += 1
            elif rank >= high_start:
                high_neighbors[n - 1 - rank] += 1
            else:
                mid_count += 1

        if width <= c < high_start:
            acc.add_joint_outer(low_neighbors, high_neighbors)
            for key, count in min_pair_distribution(low_neighbors).items():
                acc.add_low(key, count)
            for key, count in low_neighbors.items():
                acc.add_low(key, count * mid_count)
            for key, count in min_pair_distribution(high_neighbors).items():
                acc.add_high(key, count)
            for key, count in high_neighbors.items():
                acc.add_high(key, count * mid_count)
            middle_pairs = mid_count * (mid_count - 1) // 2
            acc.neither += middle_pairs
            acc.total += middle_pairs
        elif c < width:
            nonhigh_states: Counter[int] = Counter()
            for key, count in low_neighbors.items():
                nonhigh_states[min(c, key)] += count
            nonhigh_states[c] += mid_count
            acc.add_joint_outer(nonhigh_states, high_neighbors)
            for key, count in min_pair_distribution(nonhigh_states).items():
                acc.add_low(key, count)
            for key, count in min_pair_distribution(high_neighbors).items():
                acc.joint[c, key] += count
                acc.total += count
        else:
            center_high = n - 1 - c
            nonlow_states: Counter[int] = Counter()
            for key, count in high_neighbors.items():
                nonlow_states[min(center_high, key)] += count
            nonlow_states[center_high] += mid_count
            acc.add_joint_outer(low_neighbors, nonlow_states)
            for key, count in min_pair_distribution(nonlow_states).items():
                acc.add_high(key, count)
            for key, count in min_pair_distribution(low_neighbors).items():
                acc.joint[key, center_high] += count
                acc.total += count

        expected = degree * (degree - 1) // 2
        # The global total is checked against the degree formula after all centers.
        if expected < 0:
            raise AssertionError("unreachable")
    degree_total = sum(len(row) * (len(row) - 1) // 2 for row in adjacency)
    if acc.total != degree_total:
        raise AssertionError({"projected": acc.total, "degree_formula": degree_total})
    return acc


def aggregate_triangles(
    edges: list[tuple[int, int]],
    adjacency: list[list[int]],
    degrees: list[int],
    ranks: list[int],
    n: int,
    width: int,
) -> IntervalAccumulator:
    """Enumerate every triangle once using the released degree/id orientation."""
    out_bits = [0] * n
    out_neighbors = [[] for _ in range(n)]
    for u, v in edges:
        if (degrees[u], u) > (degrees[v], v):
            u, v = v, u
        out_neighbors[u].append(v)
        out_bits[u] |= 1 << v
    acc = IntervalAccumulator(n, width)
    for u, row in enumerate(out_neighbors):
        u_bits = out_bits[u]
        for v in row:
            common = u_bits & out_bits[v]
            while common:
                bit = common & -common
                w = bit.bit_length() - 1
                common ^= bit
                lo = min(ranks[u], ranks[v], ranks[w])
                hi = max(ranks[u], ranks[v], ranks[w])
                acc.add(lo, hi)
    return acc


def exact_2star_sensitivity(
    edges: list[tuple[int, int]], degrees: list[int]
) -> int:
    edge_set = set(edges)
    order = sorted(range(len(degrees)), key=lambda v: (-degrees[v], v))
    best = 0
    for i, u in enumerate(order):
        if i + 1 >= len(order) or degrees[u] + degrees[order[i + 1]] <= best:
            break
        for v in order[i + 1 :]:
            upper = degrees[u] + degrees[v]
            if upper <= best:
                break
            candidate = upper - (1 if (min(u, v), max(u, v)) in edge_set else 0)
            best = max(best, candidate)
    return best


def exact_triangle_sensitivity(adjacency: list[list[int]], degrees: list[int]) -> int:
    bits = [sum(1 << vertex for vertex in row) for row in adjacency]
    order = sorted(range(len(degrees)), key=lambda v: (-degrees[v], v))
    best = 0
    for i, u in enumerate(order):
        if degrees[u] <= best:
            break
        for v in order[i + 1 :]:
            if degrees[v] <= best:
                break
            best = max(best, (bits[u] & bits[v]).bit_count())
    return best


def segment_decompose(
    n: int, query_left: int, query_right: int, left: int = 0, right: int | None = None
) -> list[tuple[int, int]]:
    if right is None:
        right = n - 1
    if query_right < left or right < query_left:
        return []
    if query_left <= left and right <= query_right:
        return [(left, right)]
    middle = (left + right) // 2
    return segment_decompose(n, query_left, query_right, left, middle) + segment_decompose(
        n, query_left, query_right, middle + 1, right
    )


class CanonicalNoise:
    def __init__(self, n: int, width: int) -> None:
        self.width = width
        left_nodes = [segment_decompose(n, value, n - 1) for value in range(width)]
        right_nodes = [
            segment_decompose(n, 0, n - 1 - value) for value in range(width)
        ]
        left_unique = sorted({node for row in left_nodes for node in row})
        right_unique = sorted({node for row in right_nodes for node in row})
        left_index = {node: i for i, node in enumerate(left_unique)}
        right_index = {node: i for i, node in enumerate(right_unique)}
        self.left = [
            np.fromiter((left_index[node] for node in row), dtype=np.intp)
            for row in left_nodes
        ]
        self.right = [
            np.fromiter((right_index[node] for node in row), dtype=np.intp)
            for row in right_nodes
        ]
        self.shape = (len(left_unique), len(right_unique))
        self.average_canonical_nodes = float(
            np.mean([len(nodes) for nodes in self.left])
            * np.mean([len(nodes) for nodes in self.right])
        )

    def draw(self, rng: np.random.Generator) -> np.ndarray:
        node_noise = rng.laplace(0.0, 1.0, size=self.shape)
        left_sums = np.empty((self.width, self.shape[1]), dtype=np.float64)
        for row, nodes in enumerate(self.left):
            left_sums[row, :] = node_noise[nodes, :].sum(axis=0)
        result = np.empty((self.width, self.width), dtype=np.float64)
        for column, nodes in enumerate(self.right):
            result[:, column] = left_sums[:, nodes].sum(axis=1)
        return result


def query_coordinates(
    n: int, query_count: int, width: int, seed: int
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    a = rng.permutation(width)
    b = rng.permutation(width)
    left = np.repeat(a, width)
    high_index = np.tile(b, width)
    left = left[rng.permutation(width * width)][:query_count]
    high_index = high_index[rng.permutation(width * width)][:query_count]
    if len(left) != query_count or np.any(left >= width) or np.any(high_index >= width):
        raise AssertionError("invalid query coordinates")
    return left, high_index


def approximate_scale(
    n: int,
    comp_num: int,
    d_max: int,
    epsilon: float,
    pattern: str,
    rng: np.random.Generator,
) -> float:
    if pattern == "edge":
        return (
            math.sqrt(comp_num)
            * 2.0
            * math.sqrt(2.0 * math.log(1.0 / DELTA))
            / epsilon
        )
    m_h = 3 if pattern == "triangle" else 2
    epsilon_prime = epsilon / (m_h + 1.0)
    delta_prime = DELTA / max(
        2.0 * math.exp(m_h * epsilon_prime)
        + m_h * math.exp(epsilon_prime)
        + 1.0,
        m_h * math.exp(2.0 * epsilon_prime)
        + math.exp(epsilon_prime)
        + 2.0,
    )
    delta_double_prime = min(math.exp(-epsilon_prime / 8.0), delta_prime)
    if pattern == "triangle":
        hs_2 = (
            1.0
            + math.log(1.0 / delta_prime) / epsilon_prime
            + rng.laplace(0.0, 1.0 / epsilon_prime)
        )
        hs = (
            d_max
            + hs_2 * math.log(1.0 / delta_prime) / epsilon_prime
            + rng.laplace(0.0, hs_2 / epsilon_prime)
        )
    else:
        hs = (
            d_max
            + math.log(1.0 / delta_prime) / epsilon_prime
            + rng.laplace(0.0, 1.0 / epsilon_prime)
        )
    scale = (
        hs
        * math.sqrt(comp_num)
        * 2.0
        * math.sqrt(2.0 * math.log(1.0 / delta_double_prime))
        / epsilon_prime
    )
    if not math.isfinite(scale) or scale <= 0:
        raise ValueError(
            f"Algorithm 4 produced invalid scale {scale} for {pattern}, eps={epsilon}"
        )
    return scale


def pure_scale(n: int, comp_num: int, epsilon: float, pattern: str) -> float:
    gs = 1 if pattern == "edge" else n - 2
    return gs * comp_num / epsilon


def stats(sum_value: float, sum_square: float, count: int) -> tuple[float, float]:
    mean = sum_value / count
    variance = max(0.0, (sum_square - sum_value * mean) / (count - 1))
    return mean, math.sqrt(variance)


def validate_small_projection() -> dict[str, int]:
    """Independent exhaustive query checker for all three projection counters."""
    n = 8
    width = 3
    checks = 0
    graph_instances = 40
    for instance in range(graph_instances):
        rng = random.Random(90210 + instance)
        probability = 0.05 + 0.9 * instance / (graph_instances - 1)
        edges = [
            (u, v)
            for u in range(n)
            for v in range(u + 1, n)
            if rng.random() < probability
        ]
        adjacency = [[] for _ in range(n)]
        for u, v in edges:
            adjacency[u].append(v)
            adjacency[v].append(u)
        degrees = list(map(len, adjacency))
        ranks = list(range(n))
        rng.shuffle(ranks)
        accumulators = {
            "edge": aggregate_edges(edges, ranks, n, width),
            "2star": aggregate_2stars(adjacency, ranks, n, width),
            "triangle": aggregate_triangles(
                edges, adjacency, degrees, ranks, n, width
            ),
        }
        for pattern, accumulator in accumulators.items():
            matrix = accumulator.matrix()
            for left in range(width):
                for high_index in range(width):
                    right = n - 1 - high_index
                    included = {v for v in range(n) if left <= ranks[v] <= right}
                    selected_edges = [
                        (u, v) for u, v in edges if u in included and v in included
                    ]
                    if pattern == "edge":
                        expected = len(selected_edges)
                    elif pattern == "2star":
                        deg = Counter(
                            vertex for edge in selected_edges for vertex in edge
                        )
                        expected = sum(
                            value * (value - 1) // 2 for value in deg.values()
                        )
                    else:
                        edge_set = set(selected_edges)
                        expected = sum(
                            (u, v) in edge_set
                            and (u, w) in edge_set
                            and (v, w) in edge_set
                            for u in included
                            for v in included
                            for w in included
                            if u < v < w
                        )
                    observed = int(matrix[left, high_index])
                    if observed != expected:
                        raise AssertionError(
                            (instance, pattern, left, high_index, observed, expected)
                        )
                    checks += 1
    return {"graph_instances": graph_instances, "query_pattern_checks": checks}


def run_dataset(dataset: str, n: int, expected_edges: int, seed: int) -> dict[str, object]:
    started = time.monotonic()
    edges, adjacency, degrees = load_graph(dataset, n)
    ranks = load_ranks(dataset, n)
    if len(edges) != expected_edges:
        raise AssertionError(
            f"{dataset}: expected {expected_edges} unique edges, found {len(edges)}"
        )
    query_count = math.ceil(n**1.5)
    width = math.ceil(math.sqrt(query_count))
    query_left, query_high = query_coordinates(n, query_count, width, seed)
    projection_started = time.monotonic()
    accumulators = {
        "edge": aggregate_edges(edges, ranks, n, width),
        "2star": aggregate_2stars(adjacency, ranks, n, width),
        "triangle": aggregate_triangles(edges, adjacency, degrees, ranks, n, width),
    }
    projection_seconds = time.monotonic() - projection_started
    sensitivities = {
        "edge": 0,
        "2star": exact_2star_sensitivity(edges, degrees),
        "triangle": exact_triangle_sensitivity(adjacency, degrees),
    }
    denominators: dict[str, np.ndarray] = {}
    pattern_metadata: dict[str, object] = {}
    for pattern, accumulator in accumulators.items():
        truth = accumulator.matrix()
        selected_truth = truth[query_left, query_high].astype(np.float64)
        denominators[pattern] = np.maximum(selected_truth, 0.001 * n)
        pattern_metadata[pattern] = {
            "total_occurrences": accumulator.total,
            "true_answer_min": int(selected_truth.min()),
            "true_answer_max": int(selected_truth.max()),
            "true_answer_mean": float(selected_truth.mean()),
            "d_max": sensitivities[pattern],
        }

    canonical = CanonicalNoise(n, width)
    accum = {
        pattern: {
            algorithm: {
                epsilon: {"sum": 0.0, "sum_square": 0.0}
                for epsilon in EPSILONS
            }
            for algorithm in ALGORITHMS
        }
        for pattern in PATTERNS
    }
    noise_rng = np.random.default_rng(seed + 1)
    scale_rngs = {
        (pattern, algorithm): np.random.default_rng(
            seed + 1000 + 101 * PATTERNS.index(pattern) + 7 * ALGORITHMS.index(algorithm)
        )
        for pattern in PATTERNS
        for algorithm in ("ADP_RSC", "ADP_Comp")
    }
    simulation_started = time.monotonic()
    for repetition in range(REPETITIONS):
        rsc_pure = canonical.draw(noise_rng)[query_left, query_high]
        rsc_approx = canonical.draw(noise_rng)[query_left, query_high]
        base_pure = noise_rng.laplace(0.0, 1.0, size=query_count)
        base_approx = noise_rng.laplace(0.0, 1.0, size=query_count)
        standard = {
            "PDP_RSC": rsc_pure,
            "ADP_RSC": rsc_approx,
            "PDP_Comp": base_pure,
            "ADP_Comp": base_approx,
        }
        for pattern in PATTERNS:
            denominator = denominators[pattern]
            base_moments: dict[str, tuple[float, float]] = {}
            for algorithm, draw in standard.items():
                normalized = np.abs(draw) / denominator
                base_moments[algorithm] = (
                    float(normalized.sum(dtype=np.float64)),
                    float(np.square(normalized).sum(dtype=np.float64)),
                )
            tree_components = (math.ceil(math.log2(n)) + 1) ** 2
            for epsilon in EPSILONS:
                scales = {
                    "PDP_RSC": pure_scale(n, tree_components, epsilon, pattern),
                    "ADP_RSC": approximate_scale(
                        n,
                        tree_components,
                        sensitivities[pattern],
                        epsilon,
                        pattern,
                        scale_rngs[(pattern, "ADP_RSC")],
                    ),
                    "PDP_Comp": pure_scale(n, query_count, epsilon, pattern),
                    "ADP_Comp": approximate_scale(
                        n,
                        query_count,
                        sensitivities[pattern],
                        epsilon,
                        pattern,
                        scale_rngs[(pattern, "ADP_Comp")],
                    ),
                }
                for algorithm, scale in scales.items():
                    first, second = base_moments[algorithm]
                    accum[pattern][algorithm][epsilon]["sum"] += first * scale
                    accum[pattern][algorithm][epsilon]["sum_square"] += (
                        second * scale * scale
                    )
        print(
            "CLAIM5_PROGRESS",
            json.dumps(
                {
                    "dataset": dataset,
                    "repetition": repetition + 1,
                    "repetitions": REPETITIONS,
                    "elapsed_seconds": round(time.monotonic() - simulation_started, 3),
                },
                sort_keys=True,
            ),
            flush=True,
        )

    count = query_count * REPETITIONS
    rows = []
    for pattern in PATTERNS:
        for epsilon in EPSILONS:
            row: dict[str, object] = {"pattern": pattern, "epsilon": epsilon}
            for algorithm in ALGORITHMS:
                record = accum[pattern][algorithm][epsilon]
                mean, standard_deviation = stats(
                    record["sum"], record["sum_square"], count
                )
                row[algorithm] = {
                    "mean_relative_error": mean,
                    "standard_deviation": standard_deviation,
                }
            rows.append(row)
    comparisons = []
    for row in rows:
        for proposed, baseline in (
            ("PDP_RSC", "PDP_Comp"),
            ("ADP_RSC", "ADP_Comp"),
        ):
            proposed_mean = row[proposed]["mean_relative_error"]  # type: ignore[index]
            baseline_mean = row[baseline]["mean_relative_error"]  # type: ignore[index]
            comparisons.append(
                {
                    "pattern": row["pattern"],
                    "epsilon": row["epsilon"],
                    "proposed": proposed,
                    "baseline": baseline,
                    "ratio_baseline_over_proposed": baseline_mean / proposed_mean,
                    "paper_ordering_holds": proposed_mean < baseline_mean,
                }
            )
    return {
        "dataset": dataset,
        "nodes": n,
        "unique_edges": len(edges),
        "max_degree": max(degrees),
        "query_count": query_count,
        "query_grid_width": width,
        "repetitions": REPETITIONS,
        "epsilon_values": EPSILONS,
        "delta": DELTA,
        "dimension": 1,
        "graph_sha256": sha256(UPSTREAM / dataset / f"{dataset}_graph.txt"),
        "attribute_sha256": sha256(
            UPSTREAM / dataset / f"{dataset}_attribute_d=1.txt"
        ),
        "canonical_noise_shape": canonical.shape,
        "average_canonical_nodes_per_query": canonical.average_canonical_nodes,
        "projection_seconds": projection_seconds,
        "simulation_seconds": time.monotonic() - simulation_started,
        "runtime_seconds": time.monotonic() - started,
        "patterns": pattern_metadata,
        "rows": rows,
        "comparisons": comparisons,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    self_check = validate_small_projection()
    results = []
    for index, (dataset, nodes, edges) in enumerate(DATASETS):
        result = run_dataset(dataset, nodes, edges, 260608179 + index * 100_003)
        results.append(result)
        print("CLAIM5_DATASET_RESULT", json.dumps(result, sort_keys=True), flush=True)
    all_orderings = all(
        comparison["paper_ordering_holds"]
        for result in results
        for comparison in result["comparisons"]  # type: ignore[union-attr]
    )
    record = {
        "schema": "dprsc-claim5-full-accuracy-v1",
        "source_anchor": "S5.p3,S5.p4,A7.SS1",
        "implementation": (
            "exact d=1 projection and Algorithm-2 canonical-node Laplace mechanism; "
            "batched over the released structured query grid"
        ),
        "seeds": [260608179 + index * 100_003 for index in range(len(DATASETS))],
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "logical_cpus_visible": __import__("os").cpu_count(),
        },
        "self_check": self_check,
        "datasets": results,
        "all_proposed_vs_corresponding_baseline_orderings_hold": all_orderings,
        "runtime_seconds": time.monotonic() - started,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print("CLAIM5_ACCURACY_RESULT", json.dumps(record, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
