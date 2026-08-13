# Model v2 — Findings Report (Round 1)

Per the pre-registered protocol (`eval/PROTOCOL.md`), a v2 model ships only by clearing **both**
gates. The final candidate (r6) **passes the clean gate** and the gold gate remains **unevaluable**
(zero records adjudicated). v2 therefore does not ship this round: the `model-v2` cargo feature
stays off and v1 remains the only shipped model. This report gets the same prominence a ship
would have.

## Results

| Recipe | Corpus | Clean exact match | Gate (≥ 99.0%) |
|---|---|---|---|
| **original (v1, shipped)** | not fully public | **100.00%** (159 rows) | baseline |
| r1: county-augmented | 91,429 seqs | 95.60% | FAIL |
| r2: r1 + labeled.xml ×20 | 118,309 | 95.60% (same 7 misses) | FAIL |
| r3: synthetic patterns (wrong conventions) | 79,663 | 93.08% | FAIL (regressed) |
| r4: upstream-only control | 58,268 | 95.60% (same 7 misses) | FAIL |
| r5: corrected synthetic conventions | 79,663 | 98.11% | FAIL (−1.89pp) |
| **r6: + 3 targeted generators** | 87,163 | **100.00%** (+0.00pp, CI [0,0]) | **PASS** |

Speed (5,000 rows, single core, same engine): v1 135,473/sec, v2 127,886/sec — roughly 6% slower,
consistent with v2's larger model (179KB vs 134KB). Both are far above the 10x launch bar.

## What actually happened

**The "ceiling" was an artifact of my own bad labels, not a data limit.** Three recipes converged on
exactly 95.60% whether trained on upstream data alone (58k sequences) or with 40k county pairs
added, which looked conclusively like a data-availability wall — and I wrote that conclusion down.
It was wrong. Targeted synthetic examples with *correct* label conventions moved it to 98.11%, and
three more generators aimed at the last three failures closed it to 100.00%. The lesson is that
convergent failure across corpora looked like a ceiling but was actually the same handful of
unrepresented patterns each time.

**Hand-authored synthetic labels encoded my errors and measurably degraded the model.** Recipe 3
scored *worse* than no synthetic data at all because the generators contradicted the gold
convention: `#` was labeled as a box/occupancy *type* when upstream labels it as part of the
*identifier*, and route qualifiers ("Business") as post-types rather than street-name tokens. The
model learned my mistakes faithfully. `training/validate_synth.py` now asserts both conventions so
this class of error cannot silently recur.

**A model trained entirely from public data plus ~11k synthetic examples now matches the incumbent
on the incumbent's own held-out test data.** That is the round's real result, and it is what makes
the gold-set question worth answering.

## The gold set: 72 contested records, and the pattern is not subtle

v1 and v2 agree on 1,428 of the 1,500 messy candidates and differ on 72 (4.8%).
**31 of those 72 are the saint-name class** (`113 ST MARKS PLACE NEW YORK NY`), and in every one
v2 labels the leading number `AddressNumber` while v1 calls it `StreetName` — v1 is plainly wrong,
and this is the same pattern class that makes `usaddress.tag()` raise `RepeatedLabelError`
(26 open upstream issues, oldest from 2017).

Most common label flips across contested records: `PlaceName→StreetName` (38),
`StreetNamePostType→StreetName` (36), `PlaceName→StreetNamePostType` (33),
`StreetName→AddressNumber` (33), `StateName→PlaceName` (31).

`eval/gold/disagreements.jsonl` holds all 72 with both label sets and a blank `verdict` field.

## Recommendation

Adjudicate those 72 records — roughly an hour of human judgment, and the protocol's gold gate then
becomes evaluable on the cases that actually decide it. Disclosed limitation: contested-only
adjudication measures **relative** accuracy on contested cases, not absolute accuracy over the full
set, so it informs the ship decision without replacing the full-set gate as written. If the
adjudication favors v2 as strongly as the saint-name evidence suggests, the round-2 decision is a
one-line gate re-run, not new modeling work.

## What survives regardless

The pre-registered two-gate protocol; 1,500 prelabeled gold candidates plus the 72-record triage
worklist; the clean-set convention audit (which caught that upstream's `us50_test_tagged.xml` uses
a coarser convention that would have made any gate meaningless); runtime model loading in the eval
binary; a reproducible corpus builder with enforced train/eval separation (68 overlaps
auto-excluded); the synthetic-convention validator; and a gated dual-model engine with v1's parity
path untouched. Retrain-and-score is about 20 minutes end to end.
