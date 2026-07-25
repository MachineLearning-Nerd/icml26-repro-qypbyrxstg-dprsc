# Claim 3 source audit

Theorem 3.3 bounds the maximum absolute error, not mean relative error, with probability at least \(1-1/n\). It explicitly hides \(c^{O(d)}\) constants. Algorithm 3 depends on both Proj and TreeConst.

The paper assumes without loss of generality that queries generate distinct
induced subgraphs. Direct endpoint counting gives
\(|Q|\le(n+1)^{2d}\), consistent with the paper's
\(O(\min(n^{2d},2^n))\) statement. The concentration proof needs this bound.
Definition 3.2 also uses set-valued `argmin`/`argmax`
when public attributes tie. The verified deterministic completion sorts by
`(attribute, vertex id)` and chooses the minimum rank among lower-bound ties
and maximum rank among upper-bound ties; this is necessary for the paper's
stated equivalence between the original and discretized induced subgraphs.
