# Source and version audit

## Paper

- Title: Differentially Private Range Subgraph Counting
- Authors: Xian Chen, Ruobing Bai, and Pan Peng
- arXiv record: https://arxiv.org/abs/2606.08179
- Pinned version: arXiv v1
- OpenReview record: https://openreview.net/forum?id=QYpByrxSTg
- Paper PDF: paper_2606.08179v1.pdf
- PDF SHA-256: 351293e30547a7241f81b73d1dc0075d3e4fe9104b1366fa7e50e07942d54016
- TeX/source archive: source/arxiv/2606.08179v1.tar
- Source archive SHA-256: 21698688374b4b6b50f6b1c944ff2092989f791a9636d6e1ad2c298121f54679
- Extracted main.tex SHA-256: ba23019fd6e80c8efa82a062cb1ebfe2235df4d26c2b57cd59236f97a58bba0c

The rendered HTML used for the Claim 5 source contract is committed at
repro/sources/2606.08179.html with SHA-256
9387c720239542f024ef31654e84ced6e2687818f8f17703945aa114aab02a5b. The
source verifier uses the committed bytes, not a live page.

## Official implementation

The author repository is [Airleave/DPRSC](https://github.com/Airleave/DPRSC),
pinned at commit aae89538544bddb1bc89961453f3cd6b6091de19. The snapshot is
vendored under upstream/ and includes the implementation, licenses, attributes,
and datasets used by the reproduction.

The released data snapshots contain:

| Dataset | Vertices | Edges | Snapshot location |
| --- | ---: | ---: | --- |
| CA-Netscience | 379 | 914 | upstream/ca-netscience/ |
| Wiki-Squirrel | 5,201 | 198,353 | upstream/musae-squirrel/ |
| WormNet-v3 | 16,347 | 762,822 | upstream/bio-WormNet-v3/ |

## Evidence source hierarchy

1. The pinned v1 source/PDF defines the paper claim and version boundary.
2. The pinned author code defines the released implementation under audit.
3. The committed run records and independent checkers define the reproduction
   result.
4. The narrative report is a readable index into those durable artifacts.

The repository does not silently substitute a later arXiv revision, an
uncommitted upstream checkout, or an unavailable author machine.

## Related primary sources

The C2 audit retains hashes and URLs for the discrepancy and reconstruction
sources in space_candidate/evidence/claim-2/primary_sources/. The C1 audit
retains the reviewed smooth-sensitivity, private-graph-structure, and
approximate-subgraph-counting sources in
space_candidate/evidence/claim-1/primary_sources/.
