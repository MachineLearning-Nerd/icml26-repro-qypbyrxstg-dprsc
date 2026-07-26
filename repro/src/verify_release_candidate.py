#!/usr/bin/env python3
"""Evaluator-blind traversal, visibility audit, and additive release manifests."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
SPACE = ROOT / "space_candidate"
RELEASE = SPACE / "evidence" / "release"
HISTORICAL = (
    SPACE
    / "historical"
    / "judged-6d5d785bb7f0386ef5d46b609fb529dbd1058fcb"
)

JUDGED_SHA = "6d5d785bb7f0386ef5d46b609fb529dbd1058fcb"
OLD_HASHES = {
    ".gitattributes": "11ad7efa24975ee4b0c3c3a38ed18737f0658a5f75a0a96787b576a78a023361",
    ".serve.log": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    ".sync.log": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    ".sync_lock": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "README.md": "f0d365d1b935c7ac7645f33eb8b5f0ad8102cdc5304c33714683c81866033898",
    "bucket-icon.svg": "d1c28fc0a4e07f2688d013f576cf76ffc422d278d56a52a82989e0b93b3b3964",
    "index.html": "301c34db2f0b122b644a4287f64ac0c31e0d5d92e5b6300bc28e708a1ee17420",
    "logbook.css": "64e1de4358c79ec0d5f2697c56f98258c025e992c94ad7b3b7801739222ca41d",
    "logbook.js": "69d73869184f936613668569980f31984be65229e77c4df4ba9604d3de70c02b",
    "logbook.json": "fc2e5142e291f0c89b86cfcf5aad88eb38fc34ed08c958dd85167480308b6ab5",
    "pages/claim-1-efficient-algorithm/page.md": "0853e0463f9aefdd2067cf1a77bf6961b2402859101338c94dffa315b9bc07c2",
    "pages/claim-2-lower-bound-theory/page.md": "ecb444ceb6d8d60fe415040fb80d5f4735b69324552e0c3c08dd1a6f422cce54",
    "pages/claim-3-accuracy/page.md": "31a5ce97fcd74ddf440f824cdb6f181f8d7d1820d9c5968fd55c58b8d85b72d8",
    "pages/conclusion/page.md": "7cfe12dc77b6df1d926cf807dd624f5e8c830c7616fa913e09c8b37e78e7cd91",
    "pages/independent-verification/page.md": "0c9c9e83fd8da61017dba00a4dfffb487e2beaea5cc5f9d9f56771b0abcea325",
    "pages/index.md": "716c3964f856e4247c25912afd551fb73d9b345b259f71b607ad2cc539867dec",
    "pages/methods-environment/page.md": "ac33165ef16187f63e503528b995b165d6421e7bc8fffed444a3132836eb82cd",
    "pages/overview/page.md": "a01de5ee0cabbe6c377db8a8c6c06f77291112982bdb3fb89a5488e5704a76d1",
    "style.css": "789bfd541c9f06658ac410d968e9c39fa8c63a48a08643b36071b984c699a9f4",
    "trackio-logo-light.png": "a6eb72253c0128ce79b526a86b7943eed37beec186b5f57ff6c1701d0e9ff596",
    "trackio-logo.png": "3e3792061d4d095759da30d7cfe7f14b621901793cd4d677b61b2896f5bf472b",
    "trackio-wordmark-dark.png": "71da94795855710d214801eb9b9b7b8898e9a8757abac0e22966a0531bbb2f4f",
}

CANONICAL = [
    "README.md",
    "logbook.json",
    "pages/index.md",
    "pages/current-status/page.md",
    "pages/current-claim-1/page.md",
    "pages/current-claim-2/page.md",
    "pages/current-claim-3/page.md",
    "pages/current-claim-4/page.md",
    "pages/current-claim-5/page.md",
    "pages/release-report/page.md",
    "pages/red-team/page.md",
]

REQUIREMENTS = {
    "pages/current-claim-1/page.md": [
        "Verdict: BLOCKED",
        "Confidence: LOW",
        "theorem_audit_run.json",
        "Independent checker",
        "controls",
        "exact contract",
    ],
    "pages/current-claim-2/page.md": [
        "Verdict: BLOCKED",
        "dependency_audit_run.json",
        "Independent checker",
        "Four verification routes",
        "controls",
    ],
    "pages/current-claim-3/page.md": [
        "Verdict: VERIFIED",
        "pure_dp_certificate_run.json",
        "Independent",
        "Negative controls",
        "Exact contract",
    ],
    "pages/current-claim-4/page.md": [
        "Verdict: FALSIFIED",
        "counterexample_run.json",
        "Independent",
        "control",
        "Exact contract",
    ],
    "pages/current-claim-5/page.md": [
        "Scientific verdict: BLOCKED",
        "Confidence: MEDIUM",
        "cumulative_accuracy_run.json",
        "cumulative_runtime_run.json",
        "Accuracy checker",
        "Runtime checker",
        "controls",
    ],
}

LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
SECRET_PATTERNS = {
    "hf_token": re.compile(r"\bhf_[A-Za-z0-9]{20,}\b"),
    "github_token": re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    "openai_key": re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    "aws_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_text(path: Path) -> bool:
    data = path.read_bytes()
    if b"\x00" in data:
        return False
    if any(byte < 32 and byte not in (9, 10, 13) for byte in data):
        return False
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def route_target(link: str) -> str | None:
    target = link.split("#", 1)[0] if not link.startswith("#/") else link
    if link.startswith(("https://", "http://", "mailto:")):
        return None
    if link.startswith("#/"):
        slug = link[2:].strip("/")
        return "pages/index.md" if slug == "index" else f"pages/{slug}/page.md"
    target = target.lstrip("./")
    return target or None


def traverse() -> tuple[list[str], list[str]]:
    queue = ["README.md", "logbook.json", "pages/index.md"]
    opened: list[str] = []
    missing: list[str] = []
    seen: set[str] = set()
    while queue:
        relative = queue.pop(0)
        if relative in seen:
            continue
        seen.add(relative)
        path = SPACE / relative
        if not path.is_file():
            missing.append(f"linked target missing: {relative}")
            continue
        opened.append(relative)
        if path.suffix.lower() != ".md":
            continue
        text = path.read_text()
        for link in LINK.findall(text):
            target = route_target(link)
            if target and target not in seen:
                queue.append(target)
    return opened, missing


def protected_subset() -> tuple[list[dict[str, str]], list[str]]:
    mappings: list[dict[str, str]] = []
    errors: list[str] = []
    for relative, expected in OLD_HASHES.items():
        current = SPACE / relative
        historical = HISTORICAL / relative
        if current.is_file() and sha256(current) == expected:
            preserved = current
            mode = "original_path_unchanged"
        elif historical.is_file() and sha256(historical) == expected:
            preserved = historical
            mode = "exact_historical_copy_after_navigation_update"
        else:
            errors.append(f"protected byte sequence missing: {relative}")
            continue
        mappings.append(
            {
                "judged_path": relative,
                "preserved_path": preserved.relative_to(SPACE).as_posix(),
                "sha256": expected,
                "mode": mode,
            }
        )
    return mappings, errors


def visibility_issues(phase: str, opened: list[str]) -> list[str]:
    issues: list[str] = []
    for relative in CANONICAL:
        if relative not in opened:
            issues.append(f"canonical file unreachable: {relative}")
    status = (SPACE / "pages/current-status/page.md").read_text()
    matrix_header = (
        "| Claim | Canonical page | Code visible | Data inline | Raw link | "
        "Checker | Control | Exact claim tested | Reviewer verdict |"
    )
    if matrix_header not in status:
        issues.append("visibility matrix header missing")
    for relative, markers in REQUIREMENTS.items():
        text = (SPACE / relative).read_text()
        for marker in markers:
            if marker.lower() not in text.lower():
                issues.append(f"{relative}: missing marker {marker!r}")
    index = (SPACE / "pages/index.md").read_text()
    current_position = index.find("Current verification status")
    historical_position = index.find("Historical rejected baseline")
    if not (0 <= current_position < historical_position):
        issues.append("current navigation does not precede historical baseline")
    if index.count("Historical rejected baseline") < 7:
        issues.append("historical navigation labels incomplete")
    report = (SPACE / "pages/release-report/page.md").read_text()
    for marker in (
        "Previous live judged score: `5/10`",
        "Conservative projected score range",
        "Best-supported possible new score",
        "| Claim | Current points | Possible points | Confidence | Evidence status | Basis and remaining risk |",
    ):
        if marker not in report:
            issues.append(f"release report missing {marker!r}")
    red_team = (SPACE / "pages/red-team/page.md").read_text()
    if phase == "initial":
        if "placeholder" in red_team.lower():
            issues.append("red-team page is still a placeholder")
    else:
        for marker in (
            "First blind pass",
            "Second blind pass",
            "Files opened",
            "No missing visibility-matrix cells",
            "protected_subset.json",
            "text_upload_allowlist.txt",
        ):
            if marker.lower() not in red_team.lower():
                issues.append(f"red-team page missing {marker!r}")
        if "placeholder" in red_team.lower():
            issues.append("red-team placeholder language remains")
    return issues


def scan_secrets() -> list[str]:
    findings: list[str] = []
    for path in sorted(SPACE.rglob("*")):
        if not path.is_file() or not is_text(path):
            continue
        text = path.read_text()
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{name}: {path.relative_to(SPACE)}")
    return findings


def upload_paths() -> list[str]:
    result: list[str] = []
    for path in sorted(SPACE.rglob("*")):
        if not path.is_file() or not is_text(path):
            continue
        relative = path.relative_to(SPACE).as_posix()
        if relative.startswith("evidence/claim-2/primary_sources/"):
            continue
        if relative in OLD_HASHES and sha256(path) == OLD_HASHES[relative]:
            continue
        result.append(relative)
    for relative in (
        "evidence/release/text_manifest.sha256",
        "evidence/release/text_upload_allowlist.txt",
    ):
        if relative not in result:
            result.append(relative)
    return sorted(result)


def write_release_manifests(
    audit: dict, mappings: list[dict[str, str]]
) -> tuple[list[str], str]:
    RELEASE.mkdir(parents=True, exist_ok=True)
    subset_record = {
        "schema": "dprsc-protected-subset-v1",
        "judged_revision": JUDGED_SHA,
        "old_file_count": len(OLD_HASHES),
        "preserved_file_count": len(mappings),
        "all_old_bytes_preserved": len(mappings) == len(OLD_HASHES),
        "mappings": mappings,
    }
    (RELEASE / "protected_subset.json").write_text(
        json.dumps(subset_record, indent=2, sort_keys=True) + "\n"
    )
    (RELEASE / "evaluator_blind_final.json").write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n"
    )
    paths = upload_paths()
    allowlist_path = RELEASE / "text_upload_allowlist.txt"
    allowlist_path.write_text("\n".join(paths) + "\n")
    paths = upload_paths()
    allowlist_path.write_text("\n".join(paths) + "\n")
    manifest_relative = "evidence/release/text_manifest.sha256"
    manifest_lines = []
    for relative in paths:
        if relative == manifest_relative:
            continue
        path = SPACE / relative
        if not path.is_file():
            raise AssertionError(f"allowlisted path missing: {relative}")
        manifest_lines.append(f"{sha256(path)}  {relative}")
    manifest_path = RELEASE / "text_manifest.sha256"
    manifest_path.write_text("\n".join(manifest_lines) + "\n")
    return paths, sha256(manifest_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("initial", "final"), required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    RELEASE.mkdir(parents=True, exist_ok=True)
    if args.phase == "final":
        # Materialize the four self-referential release links before traversal.
        # They are deterministically replaced with their complete contents
        # after the audit passes.
        for name in (
            "protected_subset.json",
            "evaluator_blind_final.json",
            "text_upload_allowlist.txt",
            "text_manifest.sha256",
        ):
            path = RELEASE / name
            if not path.exists():
                path.write_text("{}\n" if path.suffix == ".json" else "\n")
    opened, link_issues = traverse()
    mappings, subset_issues = protected_subset()
    issues = link_issues + subset_issues + visibility_issues(args.phase, opened)
    secret_findings = scan_secrets()
    issues.extend(f"secret scan: {finding}" for finding in secret_findings)
    audit = {
        "schema": "dprsc-evaluator-blind-audit-v1",
        "phase": args.phase,
        "canonical_entrypoints": ["README.md", "logbook.json", "pages/index.md"],
        "files_opened": opened,
        "files_opened_count": len(opened),
        "claim_conclusions": {
            "1": "BLOCKED",
            "2": "BLOCKED",
            "3": "VERIFIED",
            "4": "FALSIFIED",
            "5": "BLOCKED",
        },
        "issues": issues,
        "protected_old_file_count": len(OLD_HASHES),
        "protected_mappings_found": len(mappings),
        "secret_findings": secret_findings,
        "status": "PASS" if not issues else "FAIL",
    }
    out = args.out or (
        RELEASE / f"evaluator_blind_{args.phase}.json"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    if args.phase == "final" and not issues:
        paths, manifest_hash = write_release_manifests(audit, mappings)
        print(
            json.dumps(
                {
                    "status": "PASS",
                    "files_opened": len(opened),
                    "protected_files": len(mappings),
                    "text_upload_paths": len(paths),
                    "manifest_sha256": manifest_hash,
                },
                sort_keys=True,
            )
        )
    else:
        print(json.dumps(audit, sort_keys=True))
    if issues:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
