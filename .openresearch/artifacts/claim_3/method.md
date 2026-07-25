# Claim 3 method

The source checker verifies Algorithms 1–3, Theorem 3.3, its maximum-error
formula, probability, and hidden constants. The proof checker independently
reconstructs projection correctness, projection and range-tree sensitivity,
vector-Laplace privacy, a moment-generating-function concentration bound, the
distinct-query precondition, and the final union bound.

The functional certificate exhausts all four-vertex simple graphs, all binary
public-attribute assignments including ties, three pattern families, all
binary intervals, and every neighboring graph pair. A separate implementation
shares no helpers and exhausts three-vertex edge queries over ternary
attributes.

Controls deliberately (1) replace maximum error by average error, (2) choose a
naive tied-attribute boundary that drops a vertex, and (3) omit the range-tree
multiplicity from the noise scale. Every control must exit nonzero.
