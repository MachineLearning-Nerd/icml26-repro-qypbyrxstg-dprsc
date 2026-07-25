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
        "estimated_cores": 1,
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
    summary = {
        "schema": "dprsc-baseline-summary-v1",
        "verdict_scope": "historical 5/10 candidate regression only",
        "proof_checks": {
            "universal_smt": json.loads(universal.read_text()),
            "finite_enumeration": json.loads(finite.read_text()),
        },
        "historical_csv_inventory": inventory,
        "runtime_seconds": round(time.monotonic() - started, 3),
    }
    (ARTIFACTS / "baseline_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    print("BASELINE_SUMMARY", json.dumps(summary, sort_keys=True), flush=True)
    print("RUN_DONE", flush=True)


if __name__ == "__main__":
    main()
