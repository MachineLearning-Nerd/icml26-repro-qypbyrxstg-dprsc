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

## Machine-checked certificate

`repro/src/verify_lower_bound.py` exhaustively checks the paper’s graph encoding,
adjacency preservation, discrepancy lift, and reconstruction separation on all
16 private databases for a concrete 2-D common-intersection box system. It does
this independently for edge, triangle, and 2-star counting. For these three
patterns the discrepancy multiplier is exact (not merely asymptotic) because a
three-vertex occurrence cannot contain two disjoint private matching edges.

The certificate also checks explicit `(ε,δ,α,β)` choices in the decoder
contradiction for four privacy settings. Output:
`outputs/c2_proof_certificate.json`.

## Scope

Python enumeration cannot prove the asymptotic discrepancy theorem by testing
larger dimensions. That component is verified by auditing its supplied appendix
proof and cited discrepancy theorem. The executable certificate targets the
paper-specific reduction where transcription or counting errors are most likely.
