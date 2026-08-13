# Model v2 — Findings Report (Round 1: shelved, with a live follow-up path)

Per the pre-registered protocol (`eval/PROTOCOL.md`), a v2 model ships only by clearing both
gates. No recipe cleared the clean gate, so the v2 selection path stays disabled (the `model-v2`
cargo feature is off) and v1 remains the only shipped model. This report gets the same
prominence a ship would have.

## Results

| Recipe | Corpus | Clean exact match | Gate (≥ 99.0%) |
|---|---|---|---|
| **original (v1, shipped)** | not public (see below) | **100.00%** (159 rows) | baseline |
| r1: c1=0.1 c2=0.01 | 91,429 seqs (upstream + 40k county distant) | 95.60% | FAIL |
| r2: r1 + labeled.xml ×20 | 118,309 effective | 95.60% (same 7 misses) | FAIL |
| r3: capped distant + synthetic patterns | 79,663 | 93.08% | FAIL (regressed) |
| **r4: upstream-only control** | 58,268 (no county data at all) | 95.60% (same 7 misses) | FAIL |

Gold-set gate: not evaluable — 1,500 candidates exist, zero adjudicated (human adjudication
pending per protocol). Even a clean-gate pass could not have shipped this round.

## Three findings that matter

**1. The 95.60% ceiling is data, not method.** Recipes r1, r2, and r4 land on the *identical* seven
misses despite corpora ranging from upstream-only (58k) to county-augmented (118k). Distant
supervision was never the problem — it neither helped nor hurt. Every model trainable from the
public corpus converges to the same ceiling while the shipped v1 scores 100%. Upstream's public
training data does not reproduce the shipped model: only 7.1% of the clean-eval rows appear in
the public training set, so v1 genuinely generalizes to patterns our corpus cannot teach. **The
shipped model was trained on data that is not published.** Beating it on its home turf requires
labeled data we would have to create, not merely a better recipe.

**2. Hand-authored synthetic labels encoded my errors and measurably degraded the model.**
Recipe 3 targeted the failing patterns with 9,000 generated examples and scored *worse* (93.08%).
Cause: the generators contradicted the gold convention — `#` was labeled as a box/occupancy
*type* when upstream labels it as part of the *identifier*, and route qualifiers ("Business")
were labeled as post-types rather than street-name tokens. The model learned my mistakes exactly
as instructed. Fixed, and `training/validate_synth.py` now asserts both conventions so the class
of error cannot silently recur.

**3. The models disagree on only 5.4% of messy data — and that is the cheap path forward.**
Across the 1,500 messy gold candidates, v1 and v2 produce identical labels on 1,419 and differ on
81. Spot-checking those shows real wins on both sides: on `115 ST MARKS PLACE NEW YORK NY` the
incumbent mislabels the house number as a street name while v2 gets it right (the saint-name
crash class); on `1531 S GROVE AV 201` the incumbent is right and v2 is wrong.
`eval/gold/disagreements.jsonl` holds all 81 with both label sets and a blank verdict field.

## Recommendation

Adjudicate the 81 contested records rather than all 1,500. That is roughly an hour of human
work and it answers the actual question — *when the models differ on messy real-world data, which
is right more often?* Disclosed limitation: contested-only adjudication measures **relative**
accuracy on contested cases, not absolute accuracy, so it informs the next round; it does not
substitute for the protocol's full-set gate.

If that triage favors v2 materially, the round-2 recipe is clear: hand-label the failing clean
patterns (they are enumerable and few), keep the corrected synthetic generators, and re-run both
gates. If it favors v1 or splits evenly, the honest conclusion is that the incumbent model is
strong and this project's value stays where it already is — 10x speed with bit-exact parity.

## What survives regardless

Permanent infrastructure from this round: the pre-registered two-gate protocol; 1,500 prelabeled
gold candidates plus the 81-record triage worklist; the clean-set convention audit (which caught
that upstream's `us50_test_tagged.xml` uses a coarser labeling convention and would have made any
gate meaningless); runtime model loading in the eval binary; a reproducible corpus builder with
enforced train/eval separation (68 overlaps auto-excluded); the synthetic-convention validator;
and a gated dual-model engine (v1 parity untouched, feature off) ready for any future artifact.
The retrain-and-score loop is now about 20 minutes end to end.
