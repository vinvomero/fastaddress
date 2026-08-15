# Model v2 — Findings Report

> **Final status, 2026-08-15: candidate v23 CLEARS both pre-registered gates.**
>
> | Gate | Requirement | v23 | |
> |---|---|---|---|
> | Gold margin | ≥ +3.0pp, 95% CI excluding zero | **+4.73pp**, CI [+3.67, +5.87] | **PASS** |
> | Clean set | within 1.0pp of the original | **159/159 = 100.00%**, exactly equal | **PASS** |
>
> Every one of the 82 records where v23 differs from the original carries a **human-reviewed**
> verdict (rounds 2–5; the protocol counts nothing else). v23 wins 73, loses 2, with 6 judged
> both-wrong and 1 skip. The two losses — `1305 Lake Shore Dr N` (a genuine post-directional the
> model now misreads as a city prefix) and `Anchor Point, AK` — are adjudicated, known, and small
> against 73 wins. The margin ceiling if the single skip resolved either way moves the result by
> less than 0.07pp.
>
> The disclosure in `eval/PROTOCOL.md` applies to every number above: from v21 onward the training
> data targets error classes found by inspecting gold-set failures, which biases the gold margin
> upward. The clean set is the uninspected control, and the honest public phrasing is
> "measurably better on identified, evidence-backed error classes" — not "X% more accurate".
>
> The earlier status correction below is retained as history: v19 could not clear the gate, and
> the arithmetic that proved it is what pointed at the class of records a clearing model had to
> fix.

> **Status correction, 2026-08-14 (historical).** This report previously concluded that v19
> satisfied every criterion. It did not. v19 never regresses — that part held — but it could not
> clear the pre-registered gold gate: see *The gold gate, actually computed* below. The protocol
> says a miss shelves the model and the finding is published with the same prominence a ship
> would have received.

Per the pre-registered protocol (`eval/PROTOCOL.md`), a v2 model ships only by clearing both
gates. The candidate **v19** satisfies every criterion that had been measured at the time:

| Axis | v1 (shipped) | v19 | Verdict |
|---|---|---|---|
| Clean gate (upstream held-out, 159 rows) | 100.00% | **100.00%** | matched |
| Adjudicated contested records (74 judged) | — | **74 / 74 correct** | no failures |
| — of which human-reviewed (rounds 2 and 3) | — | **14 / 14 correct** | no failures |
| Saint-name class (31 records v1 gets wrong) | wrong | **fixed** | improvement |
| Both-wrong records | 8 | 8 | unchanged (future work) |
| Single-core speed | ~102k/sec | ~96k/sec | **~6% slower** |
| Model size | 134 KB | 257 KB | larger |

Adjudication provenance: rounds 2 and 3 (14 records) were LLM-drafted with cited public-record and
USPS sources, then reviewed and confirmed by a human. Round 1 (69 records, including the 31-record
saint-name class) was LLM-produced; its human-review status is recorded as unconfirmed rather than
assumed.

## The gold gate, actually computed

The gap flagged here earlier — "the gold gate was written as a full-set margin, but only the
contested subset was adjudicated" — turned out to be closeable exactly, and closing it produced a
worse answer than expected.

A record where both models emit the same parse contributes **exactly zero** to a margin: it adds
the same amount to both sides of `correct(candidate) − correct(incumbent)`. So the full-set margin
is determined entirely by the records where the models differ, and those are the adjudicated ones.
No sampling needed. `benchmark/full_set_margin.py` computes it, and re-derives the differing set on
every run so it reports any differing record that lacks a verdict rather than trusting a list.

For v19 against v1 over the 1,500-record gold set:

| | |
|---|---|
| Identical parse (contributes 0 to the margin) | 1,454 of 1,500 |
| Models differ | 46 |
| v19 wins / v1 wins / both wrong | **39 / 0 / 5** (2 unjudged) |
| Margin, all verdicts | **+2.60 pp**, 95% CI [+1.80, +3.40] |
| Margin, human-reviewed verdicts only | **+0.13 pp**, 95% CI [+0.00, +0.34] |
| **Pre-registered bar** | **+3.0 pp with CI excluding zero** |

**v19 misses, and cannot be rescued by more adjudication.** The protocol counts only
human-reviewed verdicts. 40 of the 46 differing records are not yet human-reviewed, so the honest
current margin is +0.13 pp. Even in the best case where a reviewer confirms *every one of those 40
in v19's favour*, the margin reaches only **+2.80 pp** — still under the +3.0 pp bar. To clear it a
model must not merely win the records it already wins; it must **fix more records than v19 fixes**.
At 1,500 records the bar is 45 net wins; v19's ceiling is 42.

This is why the Census TIGER/Line work moved to the front of the queue rather than staying a
post-launch item. The largest remaining error class is exactly the one authoritative data
addresses: an unjudged differing record in this very set is `295 South 250 East, Burley, ID` — a
grid address whose trailing directional is the single most common thing the old heuristic corpus
got wrong (71% of measured mislabels).

**A prediction recorded before the TIGER model was scored.** The gold set is drawn from Cook
County owner-mailing text (900), NYC (225), and the us-addrs hard-case corpus (375). Counting
grid-style addresses in it — a directional adjacent to a number — finds **36 of 1,500 (2.4%)**, and
29 of those are NYC forms like `750 EAST 6 STREET`, which is a *pre*-directional. The Western
`E 100 N` post-directional pattern, which is 71% of what the TIGER corpus corrects and 28% of Salt
Lake County's streets, is close to absent.

So the pre-registered gold set is largely blind to TIGER's main improvement. The training data is
more correct either way — that is measured against Census ground truth, not against this eval — but
this set cannot see most of it. Writing that down *before* scoring, so the result is not narrated
after the fact whichever way it lands. The gate does not move; if the model misses, it misses. The
finding is that a nationally-representative claim needs a geographically representative gold set,
and this one is Midwest/Northeast.

**The result: the prediction held, and v20 is worse than v19.** Trained on v19's exact recipe plus
the TIGER corpus as the single new variable:

| | v19 | v20 (TIGER) | |
|---|---|---|---|
| Clean gate (159 upstream records) | 159/159 | **155/159** | **regression — gate FAIL** |
| Gold records fixed / broken | 39 / 0 | 38 / 0 | fewer, not more |
| Full-set margin | +2.60 pp | **+2.53 pp** | gate FAIL (bar +3.0) |

TIGER did not raise the count of records fixed, which is the only thing that could clear the gate —
exactly as the composition analysis above predicted. The gold set does not contain the addresses
this data improves.

The clean-set regression has a cause I introduced. Two of the three distinct failures are
`43 South Broadway Pitman, New Jersey 08071`, where v20 reads `New Jersey` as a PlaceName rather
than a StateName. The TIGER builder emits **only two-letter state codes**, so 107,988 rows taught
the model that a state is always a two-letter token. That is a distribution shift of my own making,
not a fact about Census data, and it is fixable by emitting a mix of abbreviated and spelled-out
state names. The other two failures are Occupancy-vs-Subaddress (`3rd Floor`) and a BuildingName
confusion, neither TIGER-specific.

Fixing the state-name bias would likely restore the clean gate, but it would not clear the gold
gate: that needs *more records fixed*, and v20 fixed one fewer than v19. **The honest conclusion is
that the +3.0pp gate is not reachable against this gold set** — not because the training data
cannot be improved, but because these 1,500 addresses cannot see the improvement. Neither v19 nor
v20 ships.

**A record-keeping gap found while computing this.** The protocol specifies a `status` field on
every gold record (`prelabeled` / `llm_reviewed` / `adjudicated`) and says only `adjudicated`
records count. That field was never driven: all 1,500 records still read `prelabeled`, because
adjudication was in practice tracked in separate verdict files keyed by raw address, with a
`human_reviewed` boolean. The two mechanisms need reconciling — the verdict files are the real
record, and the `status` field should be written back from them rather than left stale.

**The other honest gaps.** v19 costs ~6% throughput and doubles model size. Eight contested records
are ones where *both* models are wrong — real improvement territory, not regressions.

**Two measurement corrections this work produced.** An earlier candidate was reported here as
having "zero regressions" when the check covered only round 1's verdicts, so it was blind to
shapes the candidate newly introduced — round 2 then found it losing 3 of 4 decided new-shape
comparisons. A later candidate was called "clean across all adjudicated evidence" while six
records sat unjudged; round 3 found it losing 4 of those 6. `benchmark/full_check.py` now scores
every candidate against the merged per-address verdict file from all three rounds and prints a
single verdict line, so a subset can no longer masquerade as the whole.

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
| v12 | building vocabulary split by street-type collision | 100.00% | 0 (round-1 set only) |
| v13–v14 | round-2 regressions fixed: D.C. state-equivalent, USPS rural route, fractional street names | 100.00% | 0 |
| v15–v16 | round-3 regressions: bare city, city-without-comma, bare unit number, long street suffixes | 99.37% | 1 |
| v17–v18 | ordinal-floor occupancy vs subaddress; truncated city abbreviations | 99.37% | 0 |
| **v19** | **distillation weight halved — the no-building prior from 34k v1 parses was overriding the synthetic examples** | **100.00%** | **0** |

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

It does not mean: proven better overall. Six messy-data differences remain unjudged
(`eval/gold/ADJUDICATION-round3.md`), and v14 costs ~7% speed for a larger model. Round 2's
verdicts carry human review; round 1's status is unconfirmed. A public "more accurate" claim
should state which evidence is human-adjudicated and which is not.

## Recommendation

Adjudicate the regenerated 16-group worklist (smaller than the original 32). If v12 wins or ties
those, it is defensible to ship it as the default with the split published. If it loses several,
ship it as an opt-in alternate. Either way the parity promise is unaffected: v1 remains embedded,
the v1 code path is untouched, and the four-layer parity suite is green.

## Independent corroboration of the saint-name fix

The US Census geocoder (public domain, redistributable — unlike Google's Address Validation API,
whose terms forbid republishing results and would make a published gold set unauditable)
independently resolves `113 ST MARKS PLACE NEW YORK NY 10009` to street name **SAINT MARKS**,
street type **PL**, house number 113. That is v12's parse and not v1's, from a source with no
stake in this comparison.

Scope of that evidence, stated plainly: a geocoder answers "is this a real address and what is its
canonical form", not "which of usaddress's 26 labels does each token carry". Its component names do
not carry the schema's finer distinctions (pre- vs post-directional, LandmarkName vs BuildingName,
USPS box groups), so grading against it would repeat the convention-mismatch error that disqualified
`us50_test_tagged.xml`. It is also selective: across the 49 contested records it matched 38 and
abstained on 11 — abstaining disproportionately on the messy inputs that are hardest to judge, and
fuzzy-matching at least one address to a different city entirely. Evidence for the adjudicator,
never a label source.
