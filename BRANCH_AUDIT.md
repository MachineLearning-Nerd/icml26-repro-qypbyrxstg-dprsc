# Branch audit

The original repository used experiment-generated orx/* names. The final
public names describe the evidence role and do not expose the orchestration
namespace.

## Mapping

| Original branch | Final branch | Role |
| --- | --- | --- |
| master | main | Publication surface |
| orx/validated-5-10-baseline | baseline/validated-5-10 | Historical judged baseline |
| orx/claim-1-theorem-audit-and-cumulative-full-scale | audit/claim-1-theorem | Theorem 1.3 audit |
| orx/claim-2-imported-lower-bound-lemma-audit | audit/claim-2-lower-bound | Theorem 1.4 audit |
| orx/claim-3-pure-dp-proof-audit-and-visible-claim-4 | audit/claim-3-pure-dp | Pure-DP proof |
| orx/claim-4-estimatehs-negative-scale-counterexample | audit/claim-4-negative-scale | Approximate-DP counterexample |
| orx/claim-5-adaptive-rse-runtime-and-cumulative-accu | audit/claim-5-runtime | Runtime protocol |
| orx/claim-5-anchored-source-attribution-falsificatio | audit/claim-5-source-attribution | Source attribution contract |
| orx/claim-5-full-three-dataset-paper-protocol-reprod | audit/claim-5-accuracy | Full accuracy protocol |
| orx/claim-5-rejudge-release-packaging | main | Duplicate of the publication tip; collapsed |
| orx/evaluator-visible-cumulative-release-and-visual | release/evaluator-visible | Evaluator-visible release |
| orx/exact-source-contracts-and-visible-claim-5-verif | audit/exact-source-contracts | Source contract packaging |
| orx/five-exact-claim-contracts-and-recorded-claim-5 | audit/five-claim-contracts | Integrated five-claim ledger |

## Original tips

The pre-normalization remote tips were:

~~~text
master 048383751492f51e513a3f9ca4ac67b2176bfb2d
orx/validated-5-10-baseline f244cfff49a6f46b2c8f3470d2c92fc2bcfb84e1
orx/claim-1-theorem-audit-and-cumulative-full-scale 9cbe9f7d90b6a2ec32d8bf1047450c5c26aa6ec3
orx/claim-2-imported-lower-bound-lemma-audit 35e68600ce20e67c255359c3e63bc4e7f98723a2
orx/claim-3-pure-dp-proof-audit-and-visible-claim-4 9384a24b16673f6e70cac05477d530d8a2cc1929
orx/claim-4-estimatehs-negative-scale-counterexample 0f98574ffb380f01e027583eba5fa3b932d2946c
orx/claim-5-adaptive-rse-runtime-and-cumulative-accu 7d61d041ef45e929cf43b0839f9526189f674f9
orx/claim-5-anchored-source-attribution-falsificatio c4cb4544392008732b669b626de6b2c4c8867342
orx/claim-5-full-three-dataset-paper-protocol-reprod 787bb71940e650235118077312022e92a3859f4c
orx/claim-5-rejudge-release-packaging 048383751492f51e513a3f9ca4ac67b2176bfb2d
orx/evaluator-visible-cumulative-release-and-visual ff86be4c06d2a8f8b65c735478830e0c42db5e8a
orx/exact-source-contracts-and-visible-claim-5-verif 08ab3d805eb48a316ba78b890794cd36ba7cc352
orx/five-exact-claim-contracts-and-recorded-claim-5 121a1d11222e47cd65050f2cdc84aa330f8a5cc7
~~~

After normalization, non-main branch tips are recorded in
EVIDENCE_MANIFEST.json. The final publication tip is recorded in the
collection tracker because a manifest commit cannot contain its own final
commit hash; GitHub readback covers all 12 branches.
