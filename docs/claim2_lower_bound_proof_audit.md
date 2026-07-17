# Claim 2 proof audit — universal dimension-dependent DPRSC lower bound

This audit checks the proof of Theorem `thm:main_lower` in arXiv
`2606.08179v1`, source SHA-256
`ba23019fd6e80c8efa82a062cb1ebfe2235df4d26c2b57cd59236f97a58bba0c`.
It replaces the invalid inference that measurements from the released
algorithms could establish a statement about every DP algorithm.

## Dependency audit

1. The orthogonal-range discrepancy lemma supplies point/box incidence
   matrices with discrepancy Ω(log(n)^(d−1)), 2^Ω(d), or n^Ω(1) in the three
   dimension regimes. Its appendix proof reduces the restricted-coloring
   version to the cited hereditary-discrepancy construction.
2. The paper maps every private bit to one matching edge in `G(x)`. Thus
   Hamming-neighboring databases map to edge-neighboring graphs exactly; this
   preserves the DP adjacency relation.
3. Lemma `lem:discCalphaH` lifts point discrepancy to pattern-count discrepancy
   by Ω(global-sensitivity). Its dominant one-private-edge term is the point
   incidence sum times the number of pattern copies containing that edge. The
   zero-private-edge term cancels, and terms with at least two private edges are
   lower order.
4. Lemma `lem:general-attacker` is a triangle-inequality decoding argument:
   two databases separated by more than αn bits cannot both lie within less
   than half the lifted discrepancy of the same answer vector.
5. Deterministic decoding is post-processing, so a hypothetical overly
   accurate DPRSC mechanism would be an `(ε,δ)`-DP reconstruction mechanism.
6. The cited reconstruction lemma requires expected Hamming error at least
   `exp(-ε)(1/2−δ)n`. Choosing α below this value and a sufficiently high
   constant success probability contradicts that bound.
7. Substituting the three incidence-discrepancy regimes proves respectively
   Ω(log(n)^(d−1)·GS), 2^Ω(d)·GS, and n^Ω(1)·GS. The middle regime is the
   claimed unavoidable exponential dependence on dimension.

The universal quantifier is valid because the contradiction begins with an
arbitrary `(ε,δ)`-DP DPRSC mechanism; it never assumes the mechanism is one of
the authors’ algorithms.

## Machine-checked certificates

The primary certificate is now `repro/src/verify_universal_lower_bound.py`.
It translates six arbitrary-parameter proof obligations into SMT and asks Z3
to satisfy each obligation's hypotheses together with the negation of its
conclusion. All six queries are `UNSAT`:

1. private-bit/edge adjacency preservation, per arbitrary coordinate;
2. deterministic-decoder separation by the triangle inequality;
3. valid decoder constants for every theorem-allowed privacy lower-bound
   fraction `k = exp(-epsilon) * (1/2-delta)`;
4. the discrepancy lift for arbitrary positive pattern sensitivity and point
   discrepancy after the appendix's asymptotic remainder bound;
5. transfer of the imported `2^(Omega(d))` point discrepancy to a
   `sensitivity * 2^(Omega(d))` DPRSC error lower bound; and
6. contradiction between the arbitrary mechanism's expected reconstruction
   error and the DP decoder lemma.

This certificate ranges over symbolic reals (a relaxation of arbitrary
positive integer database sizes and dimensions); it contains no enumerated
graph size or fixed dimension. The cited orthogonal-range discrepancy theorem
and DP reconstruction lemma remain explicit imported lemmas, exactly as in the
paper. Output: `outputs/c2_universal_smt_certificate.json`.

The secondary construction certificate,
`repro/src/verify_lower_bound.py`, exhaustively checks the paper’s graph
encoding, adjacency preservation, discrepancy lift, and reconstruction
separation on all 16 private databases for a concrete 2-D common-intersection
box system. It does this independently for edge, triangle, and 2-star counting.

For these three
patterns the discrepancy multiplier is exact (not merely asymptotic) because a
three-vertex occurrence cannot contain two disjoint private matching edges.

The certificate also checks explicit `(ε,δ,α,β)` choices in the decoder
contradiction for four privacy settings. Output:
`outputs/c2_proof_certificate.json`.

## Scope and trust boundary

The SMT certificate proves the paper-specific implication for arbitrary
parameters, but deliberately does not relabel imported mathematics as new
experimental evidence. The orthogonal-range discrepancy lower bound supplies
`point_disc >= 2^(c*d)` in the middle regime, and the standard DP reconstruction
lemma supplies expected Hamming error at least
`exp(-epsilon)*(1/2-delta)*n`. Both dependencies are identified by exact paper
labels and the source is pinned by SHA-256. Z3 checks that these premises imply
the claimed DPRSC lower bound and that no arbitrary DP mechanism can evade the
reconstruction contradiction.
