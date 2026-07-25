# Claim 3 general proof certificate

The primary checker reconstructs the proof rather than trusting the paper's
conclusion:

1. `Proj` maps each occurrence once to its coordinatewise public-rank span.
   With explicit extreme-rank handling for tied attributes, a pattern is in an
   induced query iff its span lies in the transformed range.
2. Adding an edge changes the projection coordinatewise monotonically. Its
   L1 sensitivity is therefore exactly the scalar subgraph-count sensitivity,
   bounded by `f_H(K_n)-f_H(K_n-e)`.
3. Each projected coordinate contributes to at most
   `(ceil(log2(n))+1)^(2d)` released tree nodes. The concatenated node vector's
   L1 sensitivity is at most this multiplicity times `GS_fH`.
4. Independent Laplace noise at scale sensitivity divided by epsilon is one
   vector Laplace mechanism. Reusing the noisy tree for all queries is
   post-processing, so there is no per-query privacy composition.
5. An independent moment-generating-function derivation bounds each answer's
   sum of at most `ceil(log2(n))^(2d)` noises. The checker separately proves the
   concentration precondition from the distinct-query bound
   `|Q| <= (n+1)^(2d)` and applies a union bound over `Q`, yielding failure
   probability at most `1/n`.
6. Simplifying the scale, number of summed nodes, and logarithm gives the exact
   claimed order with the stated `c^O(d)` hidden constants.

The exhaustive certificate covers every four-vertex simple graph, all binary
public-attribute assignments (including ties), edge/2-star/triangle patterns,
all nonempty binary intervals, and every neighboring graph pair. This finite
part is a negative-control and implementation audit; the universal verdict
rests on the general derivation above.
