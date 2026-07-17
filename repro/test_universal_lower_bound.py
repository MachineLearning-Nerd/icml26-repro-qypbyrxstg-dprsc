"""Fail-closed tests for the arbitrary-parameter Claim 2 SMT certificate."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "src"))
import verify_universal_lower_bound as universal  # noqa: E402


def certificate():
    return universal.certify()


def test_all_quantified_obligations_are_unsat():
    result = certificate()
    assert result["status"] == "PASS"
    assert len(result["obligations"]) == 6
    assert all(item["status"] == "UNSAT" for item in result["obligations"])
    assert all(item["unsat_core"] for item in result["obligations"])


def test_certificate_is_not_finite_enumeration():
    result = certificate()
    assert "no finite graph enumeration" in result["certificate_kind"]
    assert "arbitrary" in result["quantifier_scope"]["mechanism"]
    assert "every epsilon" in result["quantifier_scope"]["epsilon"]
    assert "every 0 <= delta" in result["quantifier_scope"]["delta"]


def test_exponential_transfer_conclusion_is_explicit():
    result = certificate()
    transfer = next(
        item for item in result["obligations"]
        if item["name"] == "dimension_exponential_error_transfer"
    )
    assert transfer["status"] == "UNSAT"
    assert result["middle_regime_chain"][-1].endswith(
        "sensitivity * 2^(c*d) / 4"
    )


def test_pinned_paper_source_and_dependencies():
    result = certificate()
    source = result["paper_source"]
    assert source["main_tex_sha256"] == universal.PAPER_SHA256
    assert source["theorem"] == "thm:main_lower"
    assert source["paper_specific_lemmas"] == [
        "lem:discCalphaH", "lem:general-attacker"
    ]
