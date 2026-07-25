#!/usr/bin/env python3
"""Extract one exact JSON record from an ``orx logs`` stream."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    raw = sys.stdin.buffer.read()
    prefix = args.prefix.encode() + b" "
    matches = [
        line[len(prefix) :]
        for line in raw.splitlines()
        if line.startswith(prefix)
    ]
    if len(matches) != 1:
        raise AssertionError(
            f"expected one {args.prefix} record, found {len(matches)}"
        )
    payload = json.loads(matches[0])
    envelope = {
        "schema": "dprsc-orx-log-extract-v1",
        "run_id": args.run_id,
        "record_prefix": args.prefix,
        "source_log_sha256": hashlib.sha256(raw).hexdigest(),
        "payload_sha256": hashlib.sha256(matches[0]).hexdigest(),
        "payload": payload,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(envelope, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "status": "PASS",
                "run_id": args.run_id,
                "record_prefix": args.prefix,
                "source_log_sha256": envelope["source_log_sha256"],
                "payload_sha256": envelope["payload_sha256"],
                "out": str(args.out),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
