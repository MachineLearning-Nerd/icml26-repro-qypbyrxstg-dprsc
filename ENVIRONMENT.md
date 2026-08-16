# Reproduction environment

## Locked software

- Python: 3.12 (requires-python >=3.12,<3.13)
- Dependency manager: uv
- Lockfile: uv.lock
- NumPy constraint: >=2.3,<3
- Z3: 4.15.3.0
- Test configuration: pyproject.toml

The fixed entry point is:

~~~bash
uv run --frozen python repro/src/run_campaign.py
~~~

The campaign invokes the claim runners and independent checkers. It is the
only command referenced by the claim branch records.

## Compute boundary

Proof, certificate, and counterexample checks are CPU-only and
single-threaded. Their recorded local runs expose eight logical CPUs but use
one workload thread. The longer accuracy and runtime protocols used a
CPU-only environment with an estimated four cores and 64 logical CPUs visible.
No GPU was used or required for the evidence reported here.

The runtime environment is not the paper's reported machine: the source audit
records an Intel Xeon Platinum 8562Y at 2.80 GHz with 768 GB RAM, while this
reproduction does not have the complete author environment or raw timing
samples.

## Experimental protocol

- Datasets: CA-Netscience, Wiki-Squirrel, and WormNet-v3
- Patterns: edge, 2-star, and triangle
- Dimension: one for the full accuracy/runtime protocol
- Epsilon values: eight values from 0.5 through 4.0
- Accuracy repetitions: 20
- Default accuracy query budget: ceil(n^1.5)
- Runtime stopping rule: relative standard error below 5%
- Runtime query domain: extrapolated to the full distinct-query domain of
  order n^2

These choices reproduce the pinned paper protocol where the source permits it.
A finite protocol is reported as finite evidence, not as an asymptotic
guarantee.

## What a fresh clone needs

The official code and data are included in upstream/; the paper artifacts and
source archive are included at the repository root. No private cache,
OpenResearch worktree, GPU, or author-only checkpoint is required for the
documented checks.
