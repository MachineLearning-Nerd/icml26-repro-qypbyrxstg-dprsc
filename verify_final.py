from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EXPECTED_REPO = "MachineLearning-Nerd/icml26-differentially-private-range-subgraph-counting"
CANONICAL_NAME = "MachineLearning-Nerd"
CANONICAL_EMAIL = "MachineLearning-Nerd@users.noreply.github.com"


def fail(message: str) -> None:
    raise SystemExit(f"VERIFY_FINAL_FAIL: {message}")


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        fail(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout.strip()


def load_json(relative: str) -> dict:
    path = ROOT / relative
    try:
        value = json.loads(path.read_text())
    except Exception as exc:
        fail(f"invalid JSON {relative}: {exc}")
    if not isinstance(value, dict):
        fail(f"JSON root is not an object: {relative}")
    return value


def merged(record: dict) -> dict:
    value = dict(record)
    payload = record.get("payload")
    if isinstance(payload, dict):
        value.update(payload)
    return value


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with (ROOT / relative).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


manifest = load_json("EVIDENCE_MANIFEST.json")
claims = load_json("claims.json")

for relative in manifest["required_files"]:
    if not (ROOT / relative).is_file():
        fail(f"required file missing: {relative}")

for relative, expected in manifest["paper_artifact_sha256"].items():
    observed = sha256(relative)
    if observed != expected:
        fail(f"hash mismatch for {relative}: {observed} != {expected}")

if claims["overall_status"] != "MIXED_SCOPED":
    fail("unexpected overall claim status")
claim_by_id = {claim["id"]: claim for claim in claims["claims"]}
expected_statuses = {
    "C1": "BLOCKED_LOW",
    "C2": "BLOCKED_LOW",
    "C3": "VERIFIED_SCOPED",
    "C4": "FALSIFIED",
    "C5": "MIXED_SCOPED",
}
for claim_id, expected in expected_statuses.items():
    if claim_by_id.get(claim_id, {}).get("status") != expected:
        fail(f"claim {claim_id} status is not {expected}")

c1 = merged(load_json("space_candidate/evidence/claim-1/theorem_audit_run.json"))
if c1.get("exact_verdict") != "BLOCKED":
    fail("Claim 1 evidence is not BLOCKED")

c2 = merged(load_json("space_candidate/evidence/claim-2/dependency_audit_run.json"))
if c2.get("status") != "PASS" or c2.get("claim_verdict") != "BLOCKED":
    fail("Claim 2 evidence contract mismatch")

c3 = merged(load_json("space_candidate/evidence/claim-3/formal_run.json"))
if c3.get("verdict") != "VERIFIED":
    fail("Claim 3 formal run is not VERIFIED")
if c3.get("primary_checker") != "PASS" or c3.get("independent_checker") != "PASS":
    fail("Claim 3 checker did not pass")

c4 = merged(load_json("space_candidate/evidence/claim-4/counterexample_run.json"))
if c4.get("verdict") != "FALSIFIED":
    fail("Claim 4 evidence is not FALSIFIED")
if c4.get("released_code_exception") != "ValueError":
    fail("Claim 4 released-code exception is not ValueError")
if float(c4.get("negative_event_probability", 0)) <= 0:
    fail("Claim 4 negative event probability is not positive")

c5_source = merged(load_json("space_candidate/evidence/claim-5/source_verifier_run.json"))
actual_runtime = c5_source.get("actual_paper_runtime_claim_verdict") or c5_source.get(
    "actual_runtime_verdict"
)
if c5_source.get("anchored_claim_verdict") != "FALSIFIED":
    fail("Claim 5 anchored source verdict is not FALSIFIED")
if actual_runtime != "BLOCKED":
    fail("Claim 5 actual runtime verdict is not BLOCKED")
if c5_source.get("source_contract_status") != "PASS":
    fail("Claim 5 source contract did not pass")

c5_independent = merged(
    load_json("space_candidate/evidence/claim-5/source_independent_run.json")
)
if c5_independent.get("result") != "PASS":
    fail("Claim 5 independent source checker did not pass")
if c5_independent.get("anchored_claim_verdict") != "FALSIFIED":
    fail("Claim 5 independent anchored verdict is not FALSIFIED")

c5_accuracy = merged(
    load_json("space_candidate/evidence/claim-5/cumulative_accuracy_run.json")
)
if not c5_accuracy.get("all_proposed_vs_corresponding_baseline_orderings_hold"):
    fail("Claim 5 accuracy ordering is not recorded as complete")

c5_runtime = merged(
    load_json("space_candidate/evidence/claim-5/cumulative_runtime_run.json")
)
if not c5_runtime.get("all_rse_below_5_percent"):
    fail("Claim 5 runtime RSE gate did not pass")

origin = git("config", "--get", "remote.origin.url")
normalized_origin = re.sub(r"\.git$", "", origin).replace(
    "git@github.com:", "https://github.com/"
)
if normalized_origin != f"https://github.com/{EXPECTED_REPO}":
    fail(f"unexpected origin: {origin}")

branches = set(
    git("for-each-ref", "--format=%(refname:strip=2)", "refs/heads").splitlines()
)
expected_branches = set(manifest["expected_branches"])
if branches != expected_branches:
    fail(f"branch set mismatch: {sorted(branches)} != {sorted(expected_branches)}")
if any(branch == "master" or branch.startswith("orx/") for branch in branches):
    fail("legacy branch remains")

branch_tips = manifest.get("branch_tips")
non_main_branches = expected_branches - {"main"}
if set(branch_tips) != non_main_branches:
    fail("non-main branch_tips in EVIDENCE_MANIFEST.json is incomplete")
for branch, expected_tip in branch_tips.items():
    observed_tip = git("rev-parse", f"refs/heads/{branch}")
    if observed_tip != expected_tip:
        fail(f"tip mismatch for {branch}: {observed_tip} != {expected_tip}")
if git("branch", "--show-current") != "main":
    fail("final verifier must run from main")

identity_lines = git(
    "log",
    "--all",
    "--format=%an%x09%ae%x09%cn%x09%ce",
).splitlines()
if not identity_lines:
    fail("no commits found")
for line in identity_lines:
    fields = line.split("\t")
    if fields != [CANONICAL_NAME, CANONICAL_EMAIL, CANONICAL_NAME, CANONICAL_EMAIL]:
        fail(f"non-canonical commit identity: {line}")

messages = git("log", "--all", "--format=%B").lower()
if "co-authored-by:" in messages:
    fail("co-author trailer remains in reachable history")

print(
    f"VERIFY_FINAL_PASS: {len(manifest['required_files'])} required files, "
    f"{len(expected_branches)} branches, 5 claim contracts"
)
