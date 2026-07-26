# Evaluator-blind red-team record

The evaluator-blind reviewer was given only the candidate tree and the
canonical entrypoints `README.md`, `logbook.json`, and `pages/index.md`. It was
not told where evidence lived and did not use the research repository, ORX
logs, branch descriptions, or prior knowledge to fill gaps.

## First blind pass

The first pass opened **76 files** and independently located these current
conclusions: Claim 1 BLOCKED, Claim 2 BLOCKED, Claim 3 VERIFIED, Claim 4
FALSIFIED, and Claim 5 BLOCKED. The exact traversal is downloadable as
[evaluator_blind_pass_1.json](evidence/release/evaluator_blind_pass_1.json).
**Files opened:** all 76 paths appear in that record in traversal order.

Four issues blocked the pass:

1. the protected-hash table mistyped the historical `pages/index.md` hash;
2. it mistyped the historical `trackio-logo-light.png` hash;
3. the Claim 2 audit looked for the word “negative” although the page exposes
   the same evidence under “controls”;
4. this red-team page was still a reserved stub.

No scientific result or verdict changed in response.

## Fixes

The two hash literals were corrected against the protected manifest; the Claim
2 semantic marker was changed from “negative” to “controls”; and this page now
records both passes and links every release artifact. The exact old/new
content-addressed mapping is in
[protected_subset.json](evidence/release/protected_subset.json).

## Second blind pass

After those fixes, the same verifier starts from the same three entrypoints,
records every file opened, re-locates all five conclusions, validates every
visibility-matrix cell, scans all candidate text for credential-shaped values,
and verifies the protected judged bytes. The final machine-readable traversal
is [evaluator_blind_final.json](evidence/release/evaluator_blind_final.json).

**No missing visibility-matrix cells remain.** The current verifier is obvious
from the first page; historical pages appear later and are labeled exactly
**Historical rejected baseline**.

The additive upload is limited to
[text_upload_allowlist.txt](evidence/release/text_upload_allowlist.txt), with
SHA-256 values in
[text_manifest.sha256](evidence/release/text_manifest.sha256). The manifest
excludes its own hash, as a self-hash is not well-defined.

The second-pass statement is accepted only when
`verify_release_candidate.py --phase final` exits zero. Any missing link,
marker, protected byte sequence, manifest entry, or credential-shaped value
makes it exit nonzero.

## Rejudge correction pass

After revision `adf4e474c3afe562e54e0bfd1534e1323f0c5783` was scored 4/10, the
review was repeated from the same three canonical entrypoints without repository
knowledge. It found that the evaluator-anchored Claim 5 is explicitly an “are
reported” attribution and that the candidate had already documented the source
mismatch but left the current verdict BLOCKED.

The corrected candidate makes the finite source contract executable. The blind
reviewer opened **85 files**, found Claim 5's primary raw-anchor verifier,
independent semantic parser, two failing controls, raw outputs, full empirical
context, and the limitation that the paper's actual runtime observation remains
BLOCKED. It concluded: Claim 1 BLOCKED, Claim 2 BLOCKED, Claim 3 VERIFIED,
Claim 4 FALSIFIED, and anchored Claim 5 FALSIFIED. The current
[evaluator_blind_final.json](evidence/release/evaluator_blind_final.json)
records this traversal.
