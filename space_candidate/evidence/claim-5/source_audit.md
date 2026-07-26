# Claim 5 source audit

## Source and scope

- Paper: *Differentially Private Range Subgraph Counting*, arXiv:2606.08179.
- Archived URL: <https://ar5iv.labs.arxiv.org/html/2606.08179>
- Retrieval: `2026-07-25T06:41:27Z` with User-Agent `OpenResearch-Reproduction/1.0 (+https://github.com/MachineLearning-Nerd/icml26-repro-qypbyrxstg-dprsc)`.
- SHA-256: `9387c720239542f024ef31654e84ced6e2687818f8f17703945aa114aab02a5b`.
- Anchors: Section 5 (`S5`), setting (`S5.p3`), accuracy (`S5.p4` and `S5.p5`), runtime (`S5.p6`), Figures 5–6.

## Exact source interpretation

The paper's default accuracy protocol is \(\varepsilon=2\), \(\delta=10^{-5}\), \(d=1\), \(|Q|=\lceil n^{1.5}\rceil\), at least 20 independent runs, and mean relative error. It names three datasets and three subgraph patterns.

The paper's separate runtime protocol ranges \(|Q|\) from 1 to \(\Theta(n^2)\). It explicitly says exhaustive evaluation at \(\Theta(n^2)\) is prohibitive. Instead, it samples query times until relative standard error is below 5%, then extrapolates total time from the mean query time and preprocessing time. The 3–4-order statements apply to query latency and extrapolated total runtime at \(\Theta(n^2)\).

The paper reports an Intel Xeon Platinum 8562Y processor at 2.80 GHz with
768 GB RAM. It does not publish raw timing samples or a complete
OS/Python/dependency/threading environment.

The exact evaluator-anchored Claim 5 moves the 3–4-order magnitude from runtime
to accuracy and moves the default accuracy query budget from \(n^{1.5}\) to
\(n^2\). Because its grammatical predicate is “are reported,” it is a finite
claim about the contents of Section 5. The complete hash-pinned section
contradicts both coupled predicates. The anchored claim is therefore
`FALSIFIED` with `HIGH` confidence.

This source falsification does **not** falsify the paper's actual runtime
observation. The paper-faithful hardware-dependent runtime claim remains
separately `BLOCKED` with `MEDIUM` confidence.

## Quantifiers and assumptions

The empirical prose is not a universal theorem. The faithful reproduction domain is the Cartesian product of the three named datasets and the three named patterns, with the algorithms and protocols used by the corresponding paper plots. Accuracy statistics require at least 20 independent repetitions. Runtime estimates require i.i.d. uniform sampling over queries producing distinct induced subgraphs and an observed RSE below 5%.

For the anchored attribution, the complete stated finite domain is the pinned
Section 5 (`S5` through the appendix boundary). The primary verifier checks raw
anchors and ordering; an independent standard-library HTML parser reconstructs
the semantic text. Neither checker uses the empirical results to decide the
source attribution.
