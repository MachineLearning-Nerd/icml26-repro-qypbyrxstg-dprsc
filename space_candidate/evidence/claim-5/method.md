# Claim 5 method

The source verifier checks the archived HTML hash, named Section 5 anchors,
dataset names, and protocol ordering. An independent `HTMLParser` checker
reconstructs the attribution without sharing the first verifier's raw-markup
markers. The source negative control asserts the imported but unsupported
mapping “3–4 orders in accuracy at Theta(n^2)” and exits nonzero.

The accuracy route uses the exact three released graphs and public attributes.
For each dataset, pattern, and epsilon in `{0.5, 1, ..., 4}`, it evaluates
`ceil(n^1.5)` distinct-query noise terms across 20 deterministic seeds and
reports the paper's mean relative error. The independent checker recomputes
query cardinalities, all 144 pairwise orderings, hashes, and summary
statistics. Its query-budget control substitutes the old reduced budget and
must fail.

The runtime route draws intervals by exact rejection sampling from the
uniform distribution over distinct induced subgraphs. It times the released
range-tree query and exact baseline filtering/counting in batches of 10 after
30 samples, stopping at first hit of RSE below 5% or 2,000 samples. It reports
raw samples, 95% normal intervals, preprocessing, total time at `|Q|=n`, and
total time over the full distinct-query Theta(n^2) domain. The independent
checker recomputes every statistic. A deliberately biased interval sampler is
the negative control and exits nonzero.

The paper's fixed query counts and stop rule were selected before observing
the results; no theorem-derived threshold was used as an acceptance cutoff.
