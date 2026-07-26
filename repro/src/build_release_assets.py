#!/usr/bin/env python3
"""Build deterministic reader-facing figures and the text-only Space evidence tree."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "reports" / "dprsc-reproduction-2026-07-26"
IMAGES = REPORT / "images"
SPACE = ROOT / "space_candidate"
DASHBOARD_FILES = Path(
    "/Users/dineshjinjala/Documents/AllCode/ICMLPapers/OpenSearch/files/"
    "icml26-repro-qypbyrxstg-dprsc"
)


def load_payload(path: Path) -> dict:
    record = json.loads(path.read_text())
    if "payload" not in record:
        # Fresh campaign runs write the machine-readable payload directly.
        return record

    # Archived log extracts wrap the same payload with its printed-record hash.
    payload = record["payload"]
    canonical = json.dumps(payload, sort_keys=True).encode()
    digest = hashlib.sha256(canonical).hexdigest()
    if digest != record["payload_sha256"]:
        raise AssertionError(f"payload hash mismatch: {path}")
    return payload


def save(fig: plt.Figure, name: str) -> None:
    path = IMAGES / name
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def style() -> None:
    plt.rcParams.update(
        {
            "font.size": 10,
            "axes.titlesize": 13,
            "axes.labelsize": 10,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.figsize": (10, 5.4),
            "figure.dpi": 120,
        }
    )


def label(dataset: str, pattern: str) -> str:
    short = {
        "ca-netscience": "CA",
        "musae-squirrel": "Wiki",
        "bio-WormNet-v3": "Worm",
    }[dataset]
    return f"{short}\n{pattern.replace('2star', '2-star')}"


def accuracy_figure(accuracy: dict) -> dict:
    labels: list[str] = []
    pure: list[float] = []
    approximate: list[float] = []
    for dataset in accuracy["datasets"]:
        for row in dataset["rows"]:
            if row["epsilon"] != 2.0:
                continue
            labels.append(label(dataset["dataset"], row["pattern"]))
            pure.append(
                row["PDP_Comp"]["mean_relative_error"]
                / row["PDP_RSC"]["mean_relative_error"]
            )
            approximate.append(
                row["ADP_Comp"]["mean_relative_error"]
                / row["ADP_RSC"]["mean_relative_error"]
            )
    x = np.arange(len(labels))
    fig, ax = plt.subplots()
    ax.bar(x - 0.19, pure, 0.38, label="PDP_Comp / PDP_RSC", color="#155e75")
    ax.bar(
        x + 0.19,
        approximate,
        0.38,
        label="ADP_Comp / ADP_RSC",
        color="#f59e0b",
    )
    ax.axhline(1, color="#991b1b", linewidth=1.2, linestyle="--")
    ax.set_yscale("log")
    ax.set_ylabel("baseline error ÷ proposed error (log scale)")
    ax.set_title("Paper-protocol accuracy at ε=2: every matched ratio exceeds 1")
    ax.set_xticks(x, labels)
    ax.legend(frameon=False, ncols=2)
    ax.grid(axis="y", which="both", alpha=0.2)
    save(fig, "headline_accuracy_ratios.png")
    return {
        "matched_comparisons_all_eps": sum(
            len(dataset["comparisons"]) for dataset in accuracy["datasets"]
        ),
        "matched_comparisons_holding": sum(
            comparison["paper_ordering_holds"]
            for dataset in accuracy["datasets"]
            for comparison in dataset["comparisons"]
        ),
        "epsilon_2_pure_ratio_range": [min(pure), max(pure)],
        "epsilon_2_approx_ratio_range": [min(approximate), max(approximate)],
    }


def runtime_figure(runtime: dict) -> dict:
    labels: list[str] = []
    means: list[float] = []
    lowers: list[float] = []
    for dataset in runtime["datasets"]:
        for comparison in dataset["comparisons"]:
            labels.append(label(dataset["dataset"], comparison["pattern"]))
            total = comparison["total_at_all_distinct_theta_n2"]
            means.append(total["mean_speedup"])
            lowers.append(total["conservative_95_speedup_lower"])
    x = np.arange(len(labels))
    fig, ax = plt.subplots()
    ax.bar(x, means, color="#2563eb", alpha=0.85, label="mean speedup")
    ax.scatter(x, lowers, color="#111827", marker="_", s=180, label="95% conservative lower")
    ax.axhline(1000, color="#991b1b", linewidth=1.2, linestyle="--", label="3 orders")
    ax.axhline(10000, color="#7f1d1d", linewidth=1.2, linestyle=":", label="4 orders")
    ax.set_yscale("log")
    ax.set_ylabel("extrapolated total-time speedup (log scale)")
    ax.set_title("Runtime at the full distinct-query Θ(n²) domain")
    ax.set_xticks(x, labels)
    ax.legend(frameon=False, ncols=2)
    ax.grid(axis="y", which="both", alpha=0.2)
    save(fig, "runtime_theta_n2_speedups.png")
    return {
        "mean_speedup_range": [min(means), max(means)],
        "conservative_95_lower_range": [min(lowers), max(lowers)],
    }


def crossover_figure(runtime: dict) -> None:
    labels: list[str] = []
    at_n: list[float] = []
    at_n2: list[float] = []
    for dataset in runtime["datasets"]:
        for comparison in dataset["comparisons"]:
            labels.append(label(dataset["dataset"], comparison["pattern"]))
            at_n.append(comparison["total_at_n"]["mean_speedup"])
            at_n2.append(
                comparison["total_at_all_distinct_theta_n2"]["mean_speedup"]
            )
    x = np.arange(len(labels))
    fig, ax = plt.subplots()
    ax.plot(x, at_n, "o-", color="#ea580c", label="|Q| = n")
    ax.plot(x, at_n2, "o-", color="#0369a1", label="full distinct Θ(n²) domain")
    ax.axhline(1, color="#991b1b", linewidth=1.2, linestyle="--")
    ax.set_yscale("log")
    ax.set_ylabel("mean total-time speedup (log scale)")
    ax.set_title("Preprocessing matters at small Q; query latency dominates at Θ(n²)")
    ax.set_xticks(x, labels)
    ax.legend(frameon=False)
    ax.grid(axis="y", which="both", alpha=0.2)
    save(fig, "runtime_crossover.png")


def theorem_calibration_figure(claim1: dict) -> dict:
    route = next(route for route in claim1["routes"] if route["route"] == 2)
    fig, ax = plt.subplots()
    colors = {"edge": "#0284c7", "2star": "#d97706", "triangle": "#7c3aed"}
    all_values: list[float] = []
    for dataset in ("ca-netscience", "musae-squirrel", "bio-WormNet-v3"):
        for pattern in ("edge", "2star", "triangle"):
            rows = [
                row
                for row in route["summaries"]
                if row["dataset"] == dataset and row["pattern"] == pattern
            ]
            eps = [row["epsilon"] for row in rows]
            values = [row["normalized_max_error_p95"] for row in rows]
            all_values.extend(values)
            ax.plot(
                eps,
                values,
                color=colors[pattern],
                alpha=0.28,
                linewidth=1.4,
            )
    for pattern, color in colors.items():
        grouped: dict[float, list[float]] = {}
        for row in route["summaries"]:
            if row["pattern"] == pattern:
                grouped.setdefault(row["epsilon"], []).append(
                    row["normalized_max_error_p95"]
                )
        eps = sorted(grouped)
        means = [sum(grouped[value]) / len(grouped[value]) for value in eps]
        ax.plot(
            eps,
            means,
            "o-",
            color=color,
            linewidth=2.5,
            label=pattern.replace("2star", "2-star"),
        )
    ax.set_xlabel("ε")
    ax.set_ylabel("p95 max error ÷ explicit unhidden normalizer")
    ax.set_title("Claim 1 calibration is finite corroboration, not a Big-O verdict")
    ax.legend(frameon=False)
    ax.grid(alpha=0.2)
    save(fig, "claim1_finite_calibration.png")
    return {"p95_normalized_range": [min(all_values), max(all_values)]}


def invalid_scale_figure(claim1: dict) -> None:
    route = next(route for route in claim1["routes"] if route["route"] == 4)
    selected = [
        row
        for row in route["sweep"]
        if row["epsilon"] == 2.0 and row["delta"] in (0.1, 0.5, 0.9)
    ]
    fig, ax = plt.subplots()
    for delta, color in ((0.1, "#0f766e"), (0.5, "#d97706"), (0.9, "#be123c")):
        rows = [row for row in selected if row["delta"] == delta]
        ax.plot(
            [row["n"] for row in rows],
            [row["negative_scale_probability"] for row in rows],
            "o-",
            color=color,
            label=f"negative scale, δ={delta}",
        )
    ns = sorted({row["n"] for row in selected})
    ax.plot(ns, [1 / n for n in ns], "k--", linewidth=2, label="theorem failure budget 1/n")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("n")
    ax.set_ylabel("probability")
    ax.set_title("Algorithm 5 witness: undefined-draw probability can exceed 1/n")
    ax.legend(frameon=False, ncols=2)
    ax.grid(which="both", alpha=0.2)
    save(fig, "claim4_negative_scale_probability.png")


def copy_text_evidence() -> list[str]:
    destinations: list[str] = []

    # These zero-length synchronization markers are part of the immutable
    # judged tree. Materialize them exactly so local candidate subset checks
    # model the server tree without needing the old temporary download.
    for name in (".serve.log", ".sync.log", ".sync_lock"):
        (SPACE / name).write_bytes(b"")

    def copy(source: Path, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        # The released Python files use CRLF. Normalize only the evaluator
        # mirror so it remains ordinary text for the text-only API; the pinned
        # upstream bytes in ``upstream/`` remain untouched.
        text = source.read_text()
        if source.suffix == ".py":
            text = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
        destination.write_text(text)
        destinations.append(destination.relative_to(SPACE).as_posix())

    for claim in range(1, 6):
        source_dir = ROOT / ".openresearch" / "artifacts" / f"claim_{claim}"
        destination_dir = SPACE / "evidence" / f"claim-{claim}"
        for source in sorted(source_dir.rglob("*")):
            if not source.is_file() or source.suffix.lower() == ".pdf":
                continue
            if "primary_sources" in source.relative_to(source_dir).parts:
                continue
            copy(source, destination_dir / source.relative_to(source_dir))

    scripts = [
        "run_campaign.py",
        "build_release_assets.py",
        "run_claim1_theorem_audit.py",
        "run_claim5_accuracy.py",
        "run_claim5_runtime.py",
        "verify_claim1_theorem_audit.py",
        "verify_claim2_dependency_audit.py",
        "verify_claim2_dependency_independent.py",
        "verify_claim3_pure_dp.py",
        "verify_claim3_pure_dp_independent.py",
        "verify_claim4_counterexample.py",
        "verify_claim4_counterexample_independent.py",
        "verify_claim5_accuracy.py",
        "verify_claim5_runtime.py",
        "verify_claim5_source.py",
        "verify_claim5_source_independent.py",
        "verify_claim_sources.py",
        "verify_lower_bound.py",
        "verify_release_candidate.py",
        "verify_universal_lower_bound.py",
    ]
    for name in scripts:
        copy(
            ROOT / "repro" / "src" / name,
            SPACE / "evidence" / "reproduction" / "repro" / "src" / name,
        )
    for name in (
        "ourAlg.py",
        "baseline.py",
        "find_patterns.py",
        "preprocessing.py",
        "range_tree.py",
        "PINNED_SOURCE.md",
        "LICENSE",
    ):
        copy(
            ROOT / "upstream" / name,
            SPACE / "evidence" / "reproduction" / "upstream" / name,
        )
    for dataset in ("ca-netscience", "musae-squirrel", "bio-WormNet-v3"):
        for source in sorted((ROOT / "upstream" / dataset).glob("*.txt")):
            copy(
                source,
                SPACE
                / "evidence"
                / "reproduction"
                / "upstream"
                / dataset
                / source.name,
            )
    for name in ("pyproject.toml", "uv.lock"):
        copy(ROOT / name, SPACE / "evidence" / "reproduction" / name)
    return destinations


def sync_dashboard_report() -> str | None:
    if not DASHBOARD_FILES.is_dir():
        return None
    destination = (
        DASHBOARD_FILES
        / "reports"
        / "icml26-repro-qypbyrxstg-dprsc-2026-07-26"
    )
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(REPORT / "report.md", destination / "report.md")
    shutil.copyfile(REPORT / "summary_data.json", destination / "summary_data.json")
    image_destination = destination / "images"
    image_destination.mkdir(parents=True, exist_ok=True)
    for source in sorted(IMAGES.glob("*.png")):
        shutil.copyfile(source, image_destination / source.name)
    return str(destination)


def main() -> None:
    IMAGES.mkdir(parents=True, exist_ok=True)
    accuracy = load_payload(
        ROOT / ".openresearch" / "artifacts" / "claim_5" / "cumulative_accuracy_run.json"
    )
    runtime = load_payload(
        ROOT / ".openresearch" / "artifacts" / "claim_5" / "cumulative_runtime_run.json"
    )
    claim1 = load_payload(
        ROOT / ".openresearch" / "artifacts" / "claim_1" / "theorem_audit_run.json"
    )
    style()
    summary = {
        "schema": "dprsc-release-summary-v1",
        "accuracy": accuracy_figure(accuracy),
        "runtime": runtime_figure(runtime),
        "claim1_calibration": theorem_calibration_figure(claim1),
        "source_records": {
            "claim1": "theorem_audit_run.json",
            "claim5_accuracy": "cumulative_accuracy_run.json",
            "claim5_runtime": "cumulative_runtime_run.json",
        },
    }
    crossover_figure(runtime)
    invalid_scale_figure(claim1)
    (REPORT / "summary_data.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    destinations = copy_text_evidence()
    dashboard_report = sync_dashboard_report()
    print(
        json.dumps(
            {
                "figures": sorted(path.name for path in IMAGES.glob("*.png")),
                "space_text_evidence_files": len(destinations),
                "dashboard_report": dashboard_report,
                "summary": summary,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
