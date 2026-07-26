#!/usr/bin/env python3
"""Fixed OpenResearch entrypoint for cumulative DPRSC claim checks.

Every experiment node invokes this file through the same locked ``uv`` command.
Children extend the checks and committed configuration in code; the command and
environment contract remain unchanged.
"""

from __future__ import annotations

import csv
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / ".openresearch" / "artifacts" / "baseline"


def run(*args: str) -> None:
    print("EXEC", " ".join(args), flush=True)
    subprocess.run(args, cwd=ROOT, check=True)


def run_expected_failure(*args: str) -> None:
    print("EXEC_EXPECTED_FAILURE", " ".join(args), flush=True)
    completed = subprocess.run(
        args,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.stdout:
        print(completed.stdout, end="", flush=True)
    if completed.stderr:
        print(completed.stderr, end="", file=sys.stderr, flush=True)
    if completed.returncode == 0:
        raise AssertionError("negative control unexpectedly passed")
    print(
        "EXPECTED_FAILURE_CONFIRMED",
        json.dumps({"returncode": completed.returncode}),
        flush=True,
    )


def run_expected_failure_record(out: Path, *args: str) -> None:
    print("EXEC_EXPECTED_FAILURE", " ".join(args), flush=True)
    completed = subprocess.run(
        args,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    record = {
        "schema": "dprsc-negative-control-v1",
        "command": list(args),
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "expected_nonzero": True,
        "status": "PASS" if completed.returncode != 0 else "FAIL",
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    if completed.stdout:
        print(completed.stdout, end="", flush=True)
    if completed.stderr:
        print(completed.stderr, end="", file=sys.stderr, flush=True)
    if completed.returncode == 0:
        raise AssertionError("negative control unexpectedly passed")
    print(
        "EXPECTED_FAILURE_CONFIRMED",
        json.dumps({"returncode": completed.returncode, "record": str(out)}),
        flush=True,
    )


def git_sha() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def package_versions() -> dict[str, str]:
    packages = ("numpy", "pandas", "matplotlib", "pytest", "z3-solver", "marimo")
    return {name: importlib.metadata.version(name) for name in packages}


def historical_csv_inventory() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for path in sorted((ROOT / "outputs").glob("*.csv")):
        with path.open(newline="") as handle:
            rows = list(csv.DictReader(handle))
        if not rows:
            raise AssertionError(f"historical CSV has no data rows: {path}")
        records.append(
            {
                "path": str(path.relative_to(ROOT)),
                "rows": len(rows),
                "columns": list(rows[0]),
            }
        )
    if len(records) < 9:
        raise AssertionError(f"expected at least 9 historical CSVs, found {len(records)}")
    return records


def main() -> None:
    started = time.monotonic()
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    metadata = {
        "schema": "dprsc-run-metadata-v1",
        "git_sha": git_sha(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "estimated_cores": 4,
        "estimated_runtime_minutes": "15-30",
        "selected_backend": "hf",
        "selected_flavor": "cpu-upgrade",
        "selected_image": "ghcr.io/astral-sh/uv:python3.12-bookworm-slim",
        "actual_logical_cpu_allocation": os.cpu_count(),
        "selected_compute_policy": (
            "local only if <=1 core and <=5 minutes; otherwise hf cpu-upgrade"
        ),
        "packages": package_versions(),
    }
    print("RUN_METADATA", json.dumps(metadata, sort_keys=True), flush=True)

    universal = ARTIFACTS / "c2_universal_smt_certificate.json"
    finite = ARTIFACTS / "c2_finite_certificate.json"
    run(
        sys.executable,
        "repro/src/verify_universal_lower_bound.py",
        "--out",
        str(universal),
    )
    run(
        sys.executable,
        "repro/src/verify_lower_bound.py",
        "--out",
        str(finite),
    )
    run(
        sys.executable,
        "-m",
        "pytest",
        "repro/test_universal_lower_bound.py",
        "repro/test_lower_bound.py",
        "-q",
    )

    inventory = historical_csv_inventory()
    claim5_dir = ROOT / ".openresearch" / "artifacts" / "claim_5"
    run(
        sys.executable,
        "repro/src/verify_claim5_source.py",
        "--out",
        str(claim5_dir / "source_verifier_run.json"),
    )
    run(
        sys.executable,
        "repro/src/verify_claim5_source_independent.py",
        "--out",
        str(claim5_dir / "source_independent_run.json"),
    )
    for control in ("accept-misattribution", "conflate-query-budgets"):
        run_expected_failure_record(
            claim5_dir / f"source_control_{control}.json",
            sys.executable,
            "repro/src/verify_claim5_source.py",
            "--negative-control",
            control,
        )
    run(sys.executable, "repro/src/verify_claim_sources.py")
    for control in (
        "claim1-quantifiers",
        "claim2-gs",
        "claim3-average",
        "claim4-skip-hs",
    ):
        run_expected_failure(
            sys.executable,
            "repro/src/verify_claim_sources.py",
            "--negative-control",
            control,
        )
    run(sys.executable, "repro/src/verify_claim4_counterexample.py")
    run(sys.executable, "repro/src/verify_claim4_counterexample_independent.py")
    run_expected_failure(
        sys.executable,
        "repro/src/verify_claim4_counterexample.py",
        "--clipped-control",
    )
    claim3_certificate = (
        ROOT / ".openresearch" / "artifacts" / "claim_3" / "pure_dp_certificate_run.json"
    )
    run(
        sys.executable,
        "repro/src/verify_claim3_pure_dp.py",
        "--out",
        str(claim3_certificate),
    )
    run(
        sys.executable,
        "repro/src/verify_claim3_pure_dp_independent.py",
        str(claim3_certificate),
    )
    run_expected_failure(
        sys.executable,
        "repro/src/verify_claim3_pure_dp.py",
        "--negative-control",
        "tied-boundary",
    )
    run_expected_failure(
        sys.executable,
        "repro/src/verify_claim3_pure_dp.py",
        "--negative-control",
        "under-noised",
    )
    claim2_dependency_audit = (
        ROOT / ".openresearch" / "artifacts" / "claim_2"
        / "dependency_audit_run.json"
    )
    run(
        sys.executable,
        "repro/src/verify_claim2_dependency_audit.py",
        "--out",
        str(claim2_dependency_audit),
    )
    run(
        sys.executable,
        "repro/src/verify_claim2_dependency_independent.py",
        str(claim2_dependency_audit),
    )
    run_expected_failure(
        sys.executable,
        "repro/src/verify_claim2_dependency_audit.py",
        "--negative-control",
        "omit-recursion-rounds",
    )
    run_expected_failure(
        sys.executable,
        "repro/src/verify_claim2_dependency_audit.py",
        "--negative-control",
        "promote-squared-error",
    )
    claim5_accuracy = (
        ROOT / ".openresearch" / "artifacts" / "claim_5"
        / "full_accuracy_run.json"
    )
    run(
        sys.executable,
        "repro/src/run_claim5_accuracy.py",
        "--out",
        str(claim5_accuracy),
    )
    run(
        sys.executable,
        "repro/src/verify_claim5_accuracy.py",
        str(claim5_accuracy),
    )
    run_expected_failure(
        sys.executable,
        "repro/src/verify_claim5_accuracy.py",
        str(claim5_accuracy),
        "--negative-control",
    )
    claim5_runtime = (
        ROOT / ".openresearch" / "artifacts" / "claim_5"
        / "full_runtime_run.json"
    )
    run(
        sys.executable,
        "repro/src/run_claim5_runtime.py",
        "--accuracy",
        str(claim5_accuracy),
        "--out",
        str(claim5_runtime),
    )
    run(
        sys.executable,
        "repro/src/verify_claim5_runtime.py",
        str(claim5_runtime),
    )
    run_expected_failure(
        sys.executable,
        "repro/src/verify_claim5_runtime.py",
        str(claim5_runtime),
        "--negative-control",
    )
    claim1_audit = (
        ROOT / ".openresearch" / "artifacts" / "claim_1"
        / "theorem_audit_run.json"
    )
    run(
        sys.executable,
        "repro/src/run_claim1_theorem_audit.py",
        "--out",
        str(claim1_audit),
    )
    run(
        sys.executable,
        "repro/src/verify_claim1_theorem_audit.py",
        str(claim1_audit),
        "--paper",
        "repro/sources/2606.08179.html",
    )
    for control in ("ignore-undefined", "mean-for-max", "witness-for-existence"):
        run_expected_failure(
            sys.executable,
            "repro/src/run_claim1_theorem_audit.py",
            "--out",
            str(claim1_audit),
            "--negative-control",
            control,
        )
    run(sys.executable, "repro/src/build_release_assets.py")
    run(
        sys.executable,
        "repro/src/verify_release_candidate.py",
        "--phase",
        "final",
    )
    summary = {
        "schema": "dprsc-baseline-summary-v1",
        "verdict_scope": "cumulative scientific and evaluator-visible release regression",
        "proof_checks": {
            "universal_smt": json.loads(universal.read_text()),
            "finite_enumeration": json.loads(finite.read_text()),
        },
        "historical_csv_inventory": inventory,
        "claim_5_source_contract": {
            "status": "PASS",
            "independent_checker": "PASS",
            "negative_controls": 2,
            "anchored_claim_verdict": "FALSIFIED",
            "actual_paper_runtime_claim_verdict": "BLOCKED",
        },
        "claims_1_to_4_source_contracts": {
            "status": "PASS",
            "negative_controls": 4,
            "scientific_claim_status": "SEE_CLAIM_SPECIFIC_TERMINAL_RECORDS",
        },
        "claim_4_counterexample": {
            "verdict": "FALSIFIED",
            "analytic_checker": "PASS",
            "released_implementation_checker": "PASS",
            "independent_decimal_checker": "PASS",
            "clipped_control": "EXPECTED_FAILURE_CONFIRMED",
        },
        "claim_3_pure_dp": {
            "verdict": "VERIFIED",
            "general_proof_certificate": "PASS",
            "finite_functional_certificate": "PASS",
            "independent_checker": "PASS",
            "tied_boundary_control": "EXPECTED_FAILURE_CONFIRMED",
            "under_noised_control": "EXPECTED_FAILURE_CONFIRMED",
            "certificate": json.loads(claim3_certificate.read_text()),
        },
        "claim_2_dependency_audit": {
            "verdict": "BLOCKED",
            "primary_checker": "PASS",
            "independent_checker": "PASS",
            "negative_controls": 2,
            "record": json.loads(claim2_dependency_audit.read_text()),
        },
        "claim_5_full_accuracy": {
            "verdict": "CORROBORATES_ACTUAL_PAPER_ACCURACY_ORDERING",
            "primary_run": "PASS",
            "independent_checker": "PASS",
            "negative_control": "EXPECTED_FAILURE_CONFIRMED",
            "record": json.loads(claim5_accuracy.read_text()),
        },
        "claim_5_full_runtime": {
            "verdict": "BLOCKED_ACTUAL_PAPER_RUNTIME_CLAIM",
            "primary_run": "PASS",
            "independent_checker": "PASS",
            "negative_control": "EXPECTED_FAILURE_CONFIRMED",
            "record": json.loads(claim5_runtime.read_text()),
        },
        "claim_1_theorem_audit": {
            "verdict": "BLOCKED",
            "confidence": "LOW",
            "primary_run": "PASS",
            "independent_checker": "PASS",
            "negative_controls": 3,
            "record": json.loads(claim1_audit.read_text()),
        },
        "evaluator_visible_release": {
            "status": "PASS",
            "canonical_entrypoints": [
                "space_candidate/README.md",
                "space_candidate/logbook.json",
                "space_candidate/pages/index.md",
            ],
            "visibility_matrix": "COMPLETE",
            "protected_judged_bytes": 22,
            "negative_secret_scan": "PASS",
        },
        "runtime_seconds": round(time.monotonic() - started, 3),
    }
    (ARTIFACTS / "baseline_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    print("BASELINE_SUMMARY", json.dumps(summary, sort_keys=True), flush=True)
    print("RUN_DONE", flush=True)


if __name__ == "__main__":
    main()
