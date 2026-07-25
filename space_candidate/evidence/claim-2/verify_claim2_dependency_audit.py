#!/usr/bin/env python3
"""Fail-closed audit of the imported dependencies in Claim 2.

This verifier deliberately does not turn a proof gap into a theorem
falsification.  It pins the cited primary sources, independently proves the
DP reconstruction inequality, and checks whether the partial-coloring
recursion used in Appendix D preserves the claimed logarithmic exponent.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

import z3


ROOT = Path(__file__).resolve().parents[2]
CLAIM_DIR = ROOT / ".openresearch" / "artifacts" / "claim_2"
SOURCE_DIR = CLAIM_DIR / "primary_sources"

SOURCES = {
    "chazelle_lvov_2001.pdf": {
        "sha256": "8e017f6370f3876878c1f792d912d7d094ea7eb2ef8edfac219a628eb43c493a",
        "url": "https://www.cs.princeton.edu/~chazelle/pubs/NoteDiscBox.pdf",
        "role": "standard discrepancy 2^Omega(d), and n^Omega(1) when d=Omega(log n)",
    },
    "de_2012.pdf": {
        "sha256": "89454a3f8d40323783461c122f32773fb9505315d1d85276e0317115eea0f413",
        "url": "https://arxiv.org/pdf/1107.2183",
        "role": "reconstruction-attack background",
    },
    "eden_et_al_2023.pdf": {
        "sha256": "4682175819dac82210bf5f9eb7d18d3d61b3848323ea88c81b4cad3f93cca41f",
        "url": "https://arxiv.org/pdf/2305.02263",
        "role": "Lemma 3.9 DP reconstruction lower bound",
    },
    "matousek_nikolov_2015.pdf": {
        "sha256": "5c8b42958d30b30ed7ed2b2ab6621c4f7821e9d705094e4ad968fc182a8b634f",
        "url": (
            "https://drops.dagstuhl.de/storage/00lipics/"
            "lipics-vol034-socg2015/LIPIcs.SOCG.2015.1/"
            "LIPIcs.SOCG.2015.1.pdf"
        ),
        "role": "standard hereditary discrepancy Omega(log^(d-1) n)",
    },
    "muthukrishnan_nikolov_2012.pdf": {
        "sha256": "ac606ebeaf0f90d675173766bffac9c5682c449cac97c421ff78c136193adeae",
        "url": "https://arxiv.org/pdf/1203.5453",
        "role": "partial-coloring recursion and private range-counting lower bound",
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_sources() -> list[dict[str, str]]:
    records = []
    for filename, expected in SOURCES.items():
        path = SOURCE_DIR / filename
        if not path.is_file():
            raise AssertionError(f"missing pinned primary source: {path}")
        observed = sha256(path)
        if observed != expected["sha256"]:
            raise AssertionError(
                f"source hash mismatch for {filename}: {observed}"
            )
        records.append({
            "file": str(path.relative_to(ROOT)),
            "sha256": observed,
            "url": expected["url"],
            "role": expected["role"],
        })
    return records


def prove_reconstruction_inequality() -> dict[str, object]:
    """Prove the algebra in Eden et al. Lemma 3.9 without importing it."""
    exp_epsilon, delta, bit_error = z3.Reals(
        "exp_epsilon delta bit_error"
    )
    solver = z3.Solver()
    solver.add(exp_epsilon > 0)
    solver.add(delta >= 0, delta < z3.RealVal(1) / 2)
    solver.add(bit_error >= 0)
    solver.add(
        z3.RealVal(1) / 2 <= exp_epsilon * bit_error + delta
    )
    conclusion = (
        bit_error
        >= (z3.RealVal(1) / 2 - delta) / exp_epsilon
    )
    solver.add(z3.Not(conclusion))
    result = solver.check()
    if result != z3.unsat:
        raise AssertionError(f"reconstruction inequality not proved: {result}")
    return {
        "status": "UNSAT",
        "meaning": (
            "For each coordinate, DP implies error >= "
            "exp(-epsilon)*(1/2-delta); summing coordinates proves Lemma F.3."
        ),
        "smt2_sha256": hashlib.sha256(solver.sexpr().encode()).hexdigest(),
        "smt2": solver.sexpr(),
    }


def recursion_countermodel() -> dict[str, object]:
    """Check an asymptotic countermodel to Appendix D's inference.

    For alpha=1/2 there are k+1 recursion scales when n=2^k.  In d=2,
    setting every partial-discrepancy scale to one satisfies
    f(s)=o(log n), but the accumulated sum is k+1=Theta(log n).  Thus
    Lemma D.2 does not imply that full discrepancy is o(log n).

    The d=3 and d=4 rows show the same one-logarithm loss using exact
    power sums.
    """
    rows = []
    for dimension in (2, 3, 4):
        power = dimension - 2
        samples = []
        for k in (16, 32, 64, 128):
            terms = [j**power for j in range(1, k + 1)]
            target = k ** (dimension - 1)
            samples.append({
                "k": k,
                "n": f"2^{k}",
                "largest_single_scale_over_claimed_target": str(
                    Fraction(max(terms), target)
                ),
                "recursion_sum_over_claimed_target": str(
                    Fraction(sum(terms), target)
                ),
            })
        if not all(
            Fraction(item["largest_single_scale_over_claimed_target"])
            == Fraction(1, item["k"])
            for item in samples
        ):
            raise AssertionError("single-scale little-o witness is malformed")
        lower_bound = Fraction(1, dimension - 1)
        if not all(
            Fraction(item["recursion_sum_over_claimed_target"])
            >= lower_bound
            for item in samples
        ):
            raise AssertionError("recursion countermodel lost its target order")
        rows.append({
            "dimension": dimension,
            "scale_sequence": f"f_j=j^{power}",
            "claimed_target": f"k^{dimension - 1}",
            "single_scale_ratio": "1/k -> 0",
            "sum_ratio_lower_bound": str(lower_bound),
            "samples": samples,
        })
    return {
        "status": "GAP_CONFIRMED",
        "appendix_anchor": "A4.SS1, Lemmas D.2-D.4 and D.6",
        "alpha": "1/2",
        "rounds": "k+1 for n=2^k; therefore Theta(log n), not O(1)",
        "logical_scope": (
            "Countermodel to the claimed inference from Lemma D.2, "
            "not a box-incidence counterexample to Theorem 1.4."
        ),
        "rows": rows,
    }


def alternative_theorem_scope() -> dict[str, object]:
    """Record what the earlier orthogonal-range theorem actually controls."""
    rows = []
    for dimension in range(2, 9):
        squared_error_exponent = dimension - 1
        implied_max_absolute_exponent = Fraction(dimension - 1, 2)
        claimed_max_absolute_exponent = dimension - 1
        rows.append({
            "dimension": dimension,
            "prior_average_squared_error_exponent": squared_error_exponent,
            "implied_max_absolute_error_exponent": str(
                implied_max_absolute_exponent
            ),
            "claim_2_max_absolute_error_exponent": (
                claimed_max_absolute_exponent
            ),
            "closes_claim_2": (
                implied_max_absolute_exponent
                >= claimed_max_absolute_exponent
            ),
        })
    if any(row["closes_claim_2"] for row in rows):
        raise AssertionError("invalid squared-to-absolute-error promotion")
    return {
        "status": "DOES_NOT_CLOSE_GAP",
        "primary_source": "Muthukrishnan and Nikolov (2012), Theorem 3",
        "reason": (
            "The cited result lower-bounds average squared error. "
            "It only implies a square-root exponent for maximum absolute "
            "error, while Claim 2 asserts exponent d-1 for that maximum."
        ),
        "rows": rows,
    }


def falsification_route() -> dict[str, object]:
    return {
        "status": "NO_VALID_COUNTEREXAMPLE",
        "exact_scope_retested": {
            "pattern": "fixed connected O(1)-vertex H",
            "mechanism": "arbitrary (epsilon,delta)-DP mechanism",
            "privacy": "constant epsilon>0 and delta in [0,1/2)",
            "success": "sufficiently large constant",
            "query_size": "|Q| >= n^c for sufficiently small constant c>0",
            "sizes": "infinitely many n",
            "metric": "maximum absolute error",
            "scale": "random output HS_tilde_fH(G), not GS in the theorem",
        },
        "candidates_rejected": [
            {
                "candidate": "Appendix D recursion countermodel",
                "why_not_falsification": (
                    "It contradicts a proof inference but is not itself an "
                    "axis-parallel-box incidence family or a DP mechanism."
                ),
            },
            {
                "candidate": "finite 4-point exhaustive instance",
                "why_not_falsification": (
                    "It is finite corroboration and cannot contradict an "
                    "infinitely-many-n asymptotic statement."
                ),
            },
            {
                "candidate": "one-vertex connected pattern",
                "why_not_falsification": (
                    "Algorithm 4's output is undefined for zero-edge H; "
                    "ill-defined scope is not a numerical contradiction."
                ),
            },
        ],
        "verdict_effect": (
            "The theorem remains BLOCKED rather than FALSIFIED: the cited "
            "proof is incomplete at the exact exponent, but no "
            "assumption-satisfying counterexample was established."
        ),
    }


def certify() -> dict[str, object]:
    source_records = verify_sources()
    certificate = {
        "schema": "dprsc-claim2-dependency-audit-v1",
        "status": "PASS",
        "claim_verdict": "BLOCKED",
        "primary_sources": source_records,
        "route_1_reconstruction": prove_reconstruction_inequality(),
        "route_2_partial_coloring_recursion": recursion_countermodel(),
        "route_3_alternative_primary_theorem": alternative_theorem_scope(),
        "route_4_falsification": falsification_route(),
        "accepted_conditional_evidence": {
            "paper_specific_smt": "six arbitrary-parameter obligations",
            "finite_exhaustive": (
                "16 private databases on one 4-point/6-box instance"
            ),
            "effect": (
                "These validate the graph lift and decoder conditionally, "
                "but do not repair the discrepancy exponent."
            ),
        },
        "blocking_reason": (
            "Appendix D's Lemma D.2 recursion has Theta(log n) scales. "
            "The written argument treats per-scale o(log^(d-1) n) as if "
            "their sum were still o(log^(d-1) n). The pinned primary "
            "results establish standard/hereditary discrepancy, not the "
            "same-exponent partial discrepancy required by Lemma 4.3."
        ),
    }
    payload = json.dumps(certificate, sort_keys=True).encode()
    certificate["certificate_payload_sha256"] = hashlib.sha256(
        payload
    ).hexdigest()
    return certificate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=CLAIM_DIR / "dependency_audit_run.json",
    )
    parser.add_argument(
        "--negative-control",
        choices=("omit-recursion-rounds", "promote-squared-error"),
    )
    args = parser.parse_args()

    if args.negative_control == "omit-recursion-rounds":
        # This is the faulty inference under audit.  It must never pass.
        k = 64
        accumulated_rounds = k + 1
        assert accumulated_rounds <= 2, (
            "negative control failed as intended: the recursion has "
            f"{accumulated_rounds} rounds, not a constant number"
        )
    if args.negative_control == "promote-squared-error":
        dimension = 4
        implied = Fraction(dimension - 1, 2)
        claimed = dimension - 1
        assert implied >= claimed, (
            "negative control failed as intended: average squared error "
            "requires a square root before comparison with max absolute error"
        )

    result = certify()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
