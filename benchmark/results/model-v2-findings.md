# Model v2 — Findings Report (Round 1 complete)

Per the pre-registered protocol (`eval/PROTOCOL.md`), a v2 model ships only by clearing both
gates. The final candidate (**v12**) clears the clean gate and holds every adjudicated v1 win
while fixing the class v1 gets wrong. It still does **not auto-ship**: the gold gate as written
requires human adjudication, and the current evidence is LLM-adjudicated. The `model-v2` feature
stays off pending that call.

## Where v12 landed

| Axis | v1 (shipped) | v12 (candidate) | Verdict |
|---|---|---|---|
| Clean gate (upstream held-out, 159 rows) | 100.00% | **100.00%** | matched |
| Adjudicated v1-wins held (28 contested records) | — | **28 / 28** | no regressions |
| Saint-name class (31 records, v1 adjudicated wrong) | wrong | **fixed** | improvement |
| Single-core speed (5k rows) | ~137k/sec | ~125k/sec | ~9% slower |
| Model size | 134 KB | 252 KB | larger |
| Remaining differences on messy data | — | 49 rows (3.3%), 18 outside the saint class | unadjudicated |

On every axis that has been measured against ground truth, v12 is equal to or better than v1. The
honest caveats: it is ~9% slower with a larger model, and 18 messy-data differences outside the
saint-name class have never been adjudicated — they could be wins, losses, or a mix.

## How it got there (12 recipes)

| Recipe | Change | Clean | Regressions |
|---|---|---|---|
| r1–r2 | county distant supervision, volume tuning | 95.60% | — |
| r3 | synthetic patterns, **wrong label conventions** | 93.08% | — |
| r4 | upstream-only control | 95.60% | — |
| r5 | corrected conventions | 98.11% | — |
| r6 | + 3 targeted generators | 100.00% | — |
| v3 | + v1 distillation | 97.48% | 17 |
| v4 | + shape-preserving augmentation of v1's wins | 98.11% | 7 |
| v5 | + landmark generators | 96.86% | 1 |
| v6 | narrowed landmark vocabulary | 98.11% | 3 |
| v7 | fixed invalid `SecondStreetName` label; tail-triggered landmarks | 100.00% | 2 |
| v8 | directional landmark heads; corrected intersection shape | 99.37% | 0 |
| v9–v11 | street-then-building shape; city contrast pair | 98.74–99.37% | 0 |
| **v12** | **building vocabulary split by street-type collision** | **100.00%** | **0** |

## Four lessons the record should keep

**1. My synthetic labels encoded my errors.** Recipe 3 scored *worse* than no synthetic data
because the generators contradicted the gold convention (`#` labeled as a type rather than part of
the identifier; route qualifiers as post-types). The model learned the mistakes faithfully.
`training/validate_synth.py` now asserts those conventions.

**2. I published a wrong conclusion and had to retract it.** Three recipes converged on exactly
95.60% across wildly different corpora, which looked like a hard data ceiling — I wrote that down
as a finding. It was wrong: the convergence was the same mislabeled patterns failing identically
each time. Corrected conventions moved it to 98.11% and targeted generators to 100%.

**3. A label that does not exist is worse than a wrong label.** The intersection generator emitted
`SecondStreetName`, which is not in the model's 26-label set (usaddress adds the "Second" prefix
during `tag()` grouping, not in the model). The validator now checks label-set membership.

**4. The last plateau was a vocabulary collision, not a tuning problem.** Rounds v8–v11 kept
trading the clean gate against regressions. Cause: words like `Place`, `Court`, `Park`, `Center`
are *street types* in usaddress's vocabulary, and flooding building position with them taught the
model that a street type can be a building name — which weakened `Blvd -> StreetNamePostType`.
Splitting the building vocabulary by street-type collision (keeping ambiguous words as a deliberate
minority, since real addresses do use them) resolved both axes at once.

## What "better in every way" does and does not mean here

It means: on the clean gate, on every contested record where v1 was adjudicated correct, and on
the saint-name class, v12 is at least as good as v1 and strictly better on one class.

It does not mean: proven better overall. 18 messy-data differences remain unadjudicated
(`eval/gold/ADJUDICATION.md`, regenerated for v12: 49 records in 16 groups), the adjudication
backing the regression set was LLM-produced rather than human, and v12 costs ~9% speed. A
"more accurate" claim in public copy still requires the human gate the protocol specifies.

## Recommendation

Adjudicate the regenerated 16-group worklist (smaller than the original 32). If v12 wins or ties
those, it is defensible to ship it as the default with the split published. If it loses several,
ship it as an opt-in alternate. Either way the parity promise is unaffected: v1 remains embedded,
the v1 code path is untouched, and the four-layer parity suite is green.
