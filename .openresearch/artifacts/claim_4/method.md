# Claim 4 method

The source checker verifies the Algorithm 4/5 linkage and proof anchors. The counterexample checker derives the exact negative-tail probability, constructs a valid inverse-CDF witness, and forces the same tail draw through the released implementation, where NumPy rejects the resulting negative scale. A separate 60-digit Decimal checker reconstructs the probability and statically confirms that the released code has no clipping.

The repaired clipped control uses `max(0, EstimateHS)`. It removes the counterexample, so the counterexample verifier must exit nonzero on that control. This demonstrates that the verifier is sensitive to the exact defect.
