---
title: "feat: The gold-2b campaign — teach the classes alignment threw away"
type: feat
status: active
date: 2026-08-16
origin: gold-2 attempt 2 failure analysis + REALTEXT_MANIFEST drop accounting
---

# feat: The gold-2b campaign

## Summary

Gold-2b is built, locked, and unscored: 2,912 records, 32 states, two attempts for its
lifetime. v43 is the best candidate ever produced here and still failed gold-2 by an interval
that includes zero. This campaign is the attempt to close that gap before spending attempt 1.

The diagnosis is specific, not vague. **The real-text corpus that made v43 good is built by
exact TIGER alignment, and exact alignment structurally excludes the classes v36 and v43 lost
on.** 50,995 fetched rows were dropped as `interior_unmatched` — dropped suffixes
("3906 N LAKE RIDGE" with St omitted), misspellings, non-TIGER phrases — plus 3,471 recipient
and care-of lines dropped as `no_line_start`. Those are the same failure classes the gold-2
adjudications kept surfacing. We trained on the easy 55% and were examined on all of it.

The fix is to extend the alignment ladder to label the hard rows **without** relaxing into
heuristics, then retrain, then spend.

## Problem Frame

Every gold-2 loss class we adjudicated is a class the corpus cannot contain by construction:

| Loss class seen in adjudication | Why the corpus lacks it |
|---|---|
| Dropped street suffix | Interior doesn't match any TIGER record exactly |
| Misspelled street name ("TALLY" for "TALLEY") | Same |
| Recipient / trustee / c-o lines | Row doesn't start with a number or box token |
| PO Box + small locality | Partly present, thin |
| Landmark-style rows with no number | No address-number anchor |

Meanwhile the dev holdout is carved from aligned rows only, so it is *also* blind to these
classes — which is exactly why v36 scored +0.900 there while sitting at parity on gold-2. The
dev tier and the training corpus share the same blind spot. Fixing one without the other buys
nothing.

## Requirements

- **R-A**: Extended alignment ladder producing ≥25k additional labeled rows drawn from the
  already-fetched cache, each new rung evidence-based, separately reported, individually
  disableable. No fuzzy matching without a uniqueness guard.
- **R-B**: A hard-class dev holdout carved from the new rungs, disjoint from everything,
  scored separately from the existing dev set so we can see whether the hard classes are
  actually learned rather than averaged away.
- **R-C**: No new fetching. Every new row comes from the 30 datasets the corpus already
  consumed, which gold-2b was explicitly built to exclude. Contamination risk stays zero by
  construction, and this is asserted in the builder.
- **R-D**: Candidates evaluated on the full gauntlet plus both dev tiers; gold-2b attempt 1
  fires only under the PROTOCOL2 spend rule already frozen (gauntlet ALL GREEN, dev-tier CI
  excluding zero, materially above the v36 anchor).
- **R-E**: All existing discipline: pre-registration, published misses, spent-surface rules.

## Key Technical Decisions

1. **New rungs are alignment, not guessing.** Each one still resolves the label from an
   authoritative record; it only relaxes *how the row is matched to that record*, never what
   the labels are:
   - **Rung 2a, omitted suffix.** Row's interior matches a TIGER record's name components
     exactly, with the record's suffix absent from the row. Label the tokens as the record
     splits them, with no post-type. Requires the name to resolve to exactly one record in
     that geography.
   - **Rung 2b, single-token near-match.** All interior tokens match a TIGER record except
     one, which is within Levenshtein 1 (tokens ≥5 chars: ≤2) of the corresponding record
     token. Requires a unique candidate record; ambiguous matches drop.
   - **Rung 2c, recipient prefix.** Row fails `no_line_start` because it opens with a name,
     and the source's own owner-name field matches that prefix (modulo case and punctuation).
     Label the prefix `Recipient`, align the remainder normally.
   - **Rung 2d, no-number rows.** Interior matches a record but no address number leads the
     row. Label without an AddressNumber rather than dropping.
2. **Every rung reports its own yield, sample rows, and rejection count** in the manifest.
   A rung that yields poorly or looks noisy on inspection gets disabled rather than tuned
   into producing more.
3. **The hard-class dev holdout is the new steering surface.** ~1,500 rows drawn only from
   the new rungs, carved before training. Both dev sets are reported for every candidate;
   the campaign's goal is stated as "improve hard-class dev without regressing anything,"
   which is a falsifiable target.
4. **The corpus grows; nothing leaves.** v43's recipe plus the new rows, at a weight chosen
   by small grid. The retained frames and national corpus stay — they carry adjudicated
   conventions that four rounds of whack-a-mole proved fragile.

## Implementation Units

### G2B-U2. Extended alignment ladder

**Goal:** `training/corpus/realtext2.jsonl`, ≥25k rows from the cached hard-class drops.
**Requirements:** R-A, R-C.
**Files:** `training/extend_realtext_corpus.py` (new), `training/REALTEXT2_MANIFEST.json`.
**Approach:** Re-read the cached raw rows, re-run the drop classification, then apply rungs
2a-2d to the `interior_unmatched` and `no_line_start` pools. Same dedupe as before, now also
against `realtext.jsonl` and both dev holdouts. Tokenize round-trip enforced.
**Test scenarios:** per-rung yield reported; zero eval overlaps (gold-1, gold-2, gold-2b,
clean, realtext, realtext_dev); 100% tokenize round-trip; ≥20 sample rows per rung dumped for
inspection; uniqueness guard proven by a deliberate ambiguous case.
**Verification:** manifest + a spot review of each rung's samples before training uses them.

### G2B-U3. Hard-class dev tier

**Goal:** `eval/realtext_hard_dev.jsonl` (~1,500 rows) + scorer + gauntlet wiring.
**Requirements:** R-B. **Dependencies:** U2.
**Files:** `tools/carve_hard_dev.py`, `benchmark/realtext_hard_dev.py`, `benchmark/gauntlet.py`.
**Approach:** Stratified carve by rung and state, physically removed from the training corpus,
scored candidate-vs-v1 with bootstrap CI exactly like the existing tier.
**Verification:** disjointness asserted; v43 scored on it as the new anchor (expect weak —
that is the point).

### G2B-U4. Candidate generation

**Goal:** a candidate that beats v43 on hard-class dev with CI excluding zero, holds the
existing dev tier, and is green on every composed surface.
**Requirements:** R-D. **Dependencies:** U2, U3.
**Files:** `training/train.py` (`--realtext2`), `model/candidates/`.
**Approach:** Small grid over realtext2 weight × c1 (mf=0 held, sequential — the 720k-row
cells OOM'd last time). Diagnose regressions against the dev tiers only. Counterweight frames
get added the same way they did in v41-v43: cite the ruling, commit before the test.
**Verification:** gauntlet + both dev tiers per survivor.

### G2B-U5. Spend attempt 1

**Goal:** score gold-2b (attempt 1 of 2) if and only if the frozen rule is met.
**Requirements:** R-D, R-E. **Dependencies:** U4.
**Approach:** Round-9 blinded review doc over the strict cohort; human adjudication; gates
computed from human verdicts only; primary + both sensitivity cohorts + without-WY robustness
reported together, per the owner's rulings.
**Verification:** PROTOCOL2 status entry either way, published with equal prominence.

## Scope Boundaries

**In scope:** the hard classes, and the surfaces that measure them.
**Deferred:** constrained decoding; NAD unit enrichment; any default-model change (the
compat default stays bit-identical, unconditionally); new source fetching.
**Outside this product's identity:** any accuracy claim not backed by a passed gate.

## Risks & Mitigations

- **Rung 2b introduces mislabels.** Uniqueness guard plus per-rung sample review before use;
  if a rung looks noisy, it is disabled rather than tuned.
- **Hard-class rows swamp the retained conventions** (the v42 failure mode). Weight chosen by
  grid, full adjudicated-verdict check every candidate, disjoint city lists in any new frame.
- **We improve hard-class dev and still fail gold-2b.** Possible and disclosed in advance:
  the dev set is drawn from rows we could label, and gold-2b contains rows nobody could. One
  attempt remains after that, and it stays unspent until something new justifies it.
- **Yield falls short of 25k.** Report the shortfall and train on what exists; do not relax
  matching to hit a number.

## Amendment 1 (2026-08-16, after U2's first build, before any retraining)

U2 built the four specified rungs and returned 4,970 rows against a 25,000 target, with the
shortfall measured rather than tuned around. Three rulings, recorded before the rebuild runs:

**Rung 2e is added: canonicalized lexical variants.** 17,264 of the 50,995 unmatched rows
(34%) match a TIGER record *exactly*, position for position, once spelled-out suffixes and
directionals are canonicalized to TIGER's abbreviations ("180 WEST VALLEY AVENUE" against
TIGER's "W Valley Ave"). This relaxes nothing about matching: same arity, same slots, labels
from the same record, only the surface spelling of a token differs. It is strictly safer than
rung 2b, which is already accepted. It is also a real-text class the exact-match corpus
systematically lacks, since assessors write "AVENUE" and TIGER stores "Ave". Approved.

**Rung 2a's uniqueness rule is replaced by label agreement.** As written, the rule drops a row
when several TIGER records match its name — but all 2,708 such ties are between records that
assign *identical label sequences* ("Whispering Birch Cir" and "Whispering Birch Ln" both
reduce to StreetName StreetName). The rule exists to prevent mislabeling, and where every
candidate agrees on the labels there is no mislabeling to prevent. Requiring label agreement
rather than record uniqueness is the rule the original intent implies. Approved.

**Rung 2c keeps its rows on substitute evidence, documented.** The plan asked the recipient
prefix to be confirmed against the source's own owner-name field. That field was never
fetched, and R-C forbids fetching it now, so the requirement cannot be met as written. The
substitute: the text sits in an owner-*mailing* field (whose semantics are "who to mail to"),
it is name-like by explicit test (no digits, no unit or box token, not a street name in that
geography), and the remainder of the row aligns authoritatively. A leading name-like phrase in
a mailing field is a recipient; the competing reading (BuildingName) is rare there and was
absent from all 25 samples, which carried C/O, %, TRS, LIFE ESTATE, and TRUSTEES markers.
Accepted with the evidence substitution stated in the builder's docstring and the manifest,
and with 2c rows tagged by origin so they can be ablated if a candidate regresses on the
adjudicated Recipient records.

Also recorded: 2a's first build had a systematic mislabel (rows whose own suffix was present
matching records carrying an extra suffix, e.g. "820 WASHINGTON STREET" against "Washington
Street Pl"), caught in sample review and fixed with a suffix-word guard at a cost of 869 rows.
This is why per-rung samples are reviewed before training uses them.
