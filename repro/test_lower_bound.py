"""Fail-closed tests for the Claim 2 proof certificate."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "src"))
import verify_lower_bound as lower_bound  # noqa: E402


def certificate():
    return lower_bound.certify()


def test_private_bits_map_exactly_to_edge_neighbors():
    result = certificate()["finite_exhaustive_certificate"]
    assert result["private_databases"] == 16
    assert result["neighbor_graph_checks"] == 64
    assert result["boxes_have_common_origin"] is True


def test_pattern_discrepancy_multiplier_is_exact():
    result = certificate()["finite_exhaustive_certificate"]
    assert result["count_identity_checks"] == 4608
    assert result["pattern_discrepancy"] == {
        "edge": 1, "triangle": 2, "2star": 4}
    assert all(result["exact_multiplier_verified"].values())


def test_reconstruction_separation_and_decoder_contradiction():
    result = certificate()
    finite = result["finite_exhaustive_certificate"]
    assert finite["reconstruction_separation_checks"] == 528
    for example in result["decoder_contradiction_examples"]:
        assert example["chosen_alpha"] < example["decoder_lower_error_fraction"]
        assert example["chosen_success_beta"] > example["minimum_success_beta"]
        assert (example["hypothetical_attack_upper_fraction"] <
                example["decoder_lower_error_fraction"])


def test_certificate_audits_universal_not_algorithm_specific_claim():
    result = certificate()
    assert result["status"] == "PASS"
    assert "arbitrary" in result["universal_quantifier_justification"]
    assert result["asymptotic_regimes"]["d_O_log_n"].startswith("2^Omega(d)")
