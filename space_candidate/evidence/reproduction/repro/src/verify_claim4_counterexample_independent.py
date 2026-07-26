#!/usr/bin/env python3
"""Independent Decimal/static-code check of the Claim 4 counterexample."""

from __future__ import annotations

from decimal import Decimal, getcontext
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    getcontext().prec = 60
    epsilon = Decimal(2)
    delta = Decimal("0.00001")
    m_h = Decimal(2)
    epsilon_prime = epsilon / (m_h + 1)
    first = (
        Decimal(2) * (m_h * epsilon_prime).exp()
        + m_h * epsilon_prime.exp()
        + 1
    )
    second = (
        m_h * (Decimal(2) * epsilon_prime).exp()
        + epsilon_prime.exp()
        + 2
    )
    delta_prime = delta / max(first, second)
    probability = delta_prime / 2
    if not probability > 0:
        raise AssertionError("Decimal derivation did not yield positive event mass")

    # For every uniform variate u in (0, delta'/2), the left-branch inverse
    # Laplace CDF gives an EstimateHS value below zero.  The interval length is
    # positive, independently confirming that this is not a measure-zero draw.
    u = probability / 2
    inverse_draw = (Decimal(2) * u).ln() / epsilon_prime
    threshold = (Decimal(1) / delta_prime).ln() / epsilon_prime
    estimate = threshold + inverse_draw
    if not estimate < 0:
        raise AssertionError("Decimal inverse-CDF witness is not negative")

    source = (ROOT / "upstream" / "preprocessing.py").read_text()
    function = source[source.index("def approx_DP_mag"):source.index("def generate_skewed_queries")]
    if "mag = HS *" not in function:
        raise AssertionError("released code no longer propagates HS into scale")
    if "max(0" in function or "abs(HS" in function:
        raise AssertionError("released code now appears to clip the scale")

    result = {
        "schema": "dprsc-claim4-independent-counterexample-v1",
        "method": "60-digit Decimal inverse-CDF derivation plus static released-code audit",
        "delta_prime": str(delta_prime),
        "negative_event_probability": str(probability),
        "constructed_estimate_hs": str(estimate),
        "released_code_has_clipping": False,
        "result": "PASS",
        "verdict": "FALSIFIED",
    }
    print("CLAIM4_INDEPENDENT_COUNTEREXAMPLE", json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
