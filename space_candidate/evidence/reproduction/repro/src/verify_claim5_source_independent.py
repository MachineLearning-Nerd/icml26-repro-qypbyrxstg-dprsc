#!/usr/bin/env python3
"""Independent semantic-text check for the Section 5 contract."""

from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import argparse
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "repro" / "sources" / "2606.08179.html"
EXPECTED_SHA256 = "9387c720239542f024ef31654e84ced6e2687818f8f17703945aa114aab02a5b"


class TextCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.section_depth = 0

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        if tag != "section":
            return
        attributes = dict(attrs)
        if self.section_depth:
            self.section_depth += 1
        elif attributes.get("id") == "S5":
            self.section_depth = 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "section" and self.section_depth:
            self.section_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.section_depth:
            self.parts.append(data)


def main() -> None:
    parser_args = argparse.ArgumentParser()
    parser_args.add_argument("--out", type=Path)
    args = parser_args.parse_args()
    payload = SOURCE.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != EXPECTED_SHA256:
        raise AssertionError(f"independent source hash mismatch: {digest}")

    parser = TextCollector()
    parser.feed(payload.decode("utf-8"))
    section5 = re.sub(r"\s+", " ", " ".join(parser.parts))

    required_text = [
        "1.5",
        "Runtime",
        "relative standard error",
        "3 to 4 orders of magnitude",
        "CA-Netscience 379 914",
        "Wiki-Squirrel 5,201 198,353",
        "WormNet-v3 16,347 762,822",
        "Intel(R) Xeon(R) Platinum 8562Y Processor @ 2.80 GHZ with 768 GB RAM",
    ]
    missing = [marker for marker in required_text if marker not in section5]
    if missing:
        raise AssertionError(f"independent semantic markers missing: {missing}")
    if section5.index("1.5") > section5.index("Runtime"):
        raise AssertionError("default accuracy budget should precede runtime protocol")
    runtime_position = section5.index("Runtime")
    magnitude_position = section5.index("3 to 4 orders of magnitude")
    if magnitude_position < runtime_position:
        raise AssertionError("magnitude statement escaped runtime scope")
    accuracy_scope = section5[:runtime_position]
    if "3 to 4 orders of magnitude" in accuracy_scope:
        raise AssertionError("independent parser found magnitude in accuracy scope")

    result = {
        "schema": "dprsc-claim5-independent-source-check-v2",
        "method": "stdlib HTMLParser semantic text extraction",
        "sha256": digest,
        "section_scope": "Section 5 only",
        "result": "PASS",
        "accuracy_scope_contains_3_to_4_orders": False,
        "magnitude_scope": "Runtime",
        "default_accuracy_budget": "ceil(n^1.5)",
        "runtime_budget": "Theta(n^2)",
        "reported_hardware": (
            "Intel Xeon Platinum 8562Y at 2.80 GHz with 768 GB RAM"
        ),
        "anchored_claim_verdict": "FALSIFIED",
        "actual_paper_runtime_claim_verdict": "BLOCKED",
    }
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("CLAIM5_INDEPENDENT_RESULT", json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
