#!/usr/bin/env python3
"""Independent semantic-text check for the Section 5 contract."""

from __future__ import annotations

import hashlib
from html.parser import HTMLParser
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

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def main() -> None:
    payload = SOURCE.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != EXPECTED_SHA256:
        raise AssertionError(f"independent source hash mismatch: {digest}")

    parser = TextCollector()
    parser.feed(payload.decode("utf-8"))
    text = re.sub(r"\s+", " ", " ".join(parser.parts))
    section_start = text.index("5 Experiments")
    appendix_start = text.index("A Notation", section_start)
    section5 = text[section_start:appendix_start]

    required_text = [
        "n 1.5",
        "Runtime",
        "relative standard error",
        "3 to 4 orders of magnitude",
        "CA-Netscience",
        "Wiki-Squirrel",
        "WormNet-v3",
    ]
    missing = [marker for marker in required_text if marker not in section5]
    if missing:
        raise AssertionError(f"independent semantic markers missing: {missing}")
    if section5.index("n 1.5") > section5.index("Runtime"):
        raise AssertionError("default accuracy budget should precede runtime protocol")
    if section5.index("3 to 4 orders of magnitude") < section5.index("Runtime"):
        raise AssertionError("magnitude statement escaped runtime scope")

    result = {
        "schema": "dprsc-claim5-independent-source-check-v1",
        "method": "stdlib HTMLParser semantic text extraction",
        "sha256": digest,
        "section_scope": "Section 5 only",
        "result": "PASS",
        "claim_status": "BLOCKED_PENDING_EMPIRICAL_REPRODUCTION",
    }
    print("CLAIM5_INDEPENDENT_RESULT", json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
