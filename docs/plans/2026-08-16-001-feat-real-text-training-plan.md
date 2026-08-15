---
title: "feat: Real-text training — close the composed-to-real transfer gap"
type: feat
status: active
date: 2026-08-16
origin: C:/Users/vvome/docs/brainstorms/2026-08-09-us-address-parser-requirements.md
---

# feat: Real-text training — close the composed-to-real transfer gap

## Summary

Seventeen candidates learned from composed and synthetic text and are examined on real text; the
result is composed-tier dominance and free-text parity (gold-2 attempt 1: 30/27/5, CI includes
zero). This plan attacks the single root cause: build a **real-text training corpus** by aligning
fetched owner-mail lines against authoritative address records, add a **real-text dev tier** so
iteration optimizes what the exam measures, train the next generation on it, and pre-commit the
spend rule for the final gold-2 attempt. Everything else — launch, default model, existing gates,
ledger discipline — stays exactly as is.

---

## Problem Frame

Training distribution ≠ evaluation distribution. The one time real-text classes were taught from
adjudicated real examples (gold-1's classes), transfer happened (+4.73pp, held). Synthetic frames
taught composed champions (70.5% on the binding split) that sit at parity on real mail text. The
v36 gold-2 losses are real-text habits no generator produced: dropped suffixes ("3906 N Lake
Ridge" with St omitted), recipient/trustee lines, "PO Box + North Bridgton" localities,
"Old Hickory" city names. Millions of real lines are reachable through the 41 working gold-2
source configs; they lack labels. Labels are recoverable by alignment: the sources carry
city/state/zip as separate fields (tail labels come free), and the street-line interior can be
matched against TIGER's pre-split street records for that geography — exact matches only,
unmatched rows dropped and the yield reported. The same conservative-alignment trick that made
the TIGER corpus trustworthy, now applied to real text.

---

## Requirements

- **R-A**: A real-text labeled corpus ≥50k rows from ≥25 states, built by alignment, zero
  heuristic interior splits, dedupe enforced against gold-1, gold-2, and clean.
- **R-B**: A real-text dev tier (held-out, stratified, never trained on) wired into the gauntlet;
  iteration happens against it, never against gold-2.
- **R-C**: Pre-committed spend rule, written into PROTOCOL2 before any candidate is scored:
  gold-2 attempt 2 fires only for a candidate that beats v1 on the real-text dev holdout with a
  95% CI excluding zero AND is green on every existing surface (clean, gold-1 verdicts, scans,
  spent splits).
- **R-D**: Gold-2b source list drafted in parallel as insurance (documentation only).
- **R-E**: All prior discipline intact: ledger, disclosure language, publish-either-way.

---

## Key Technical Decisions

1. **Alignment labeling, not heuristics.** Tail labels (city/state/zip) come from the source's
   own separate fields. Interior: strip unit/box patterns by adjudicated conventions (PO Box,
   Apt/Ste/#), then require the remaining street phrase to exactly match (modulo case and
   punctuation) a TIGER street record for the row's geography; the record's component split
   labels the real tokens as written. No match → row dropped, yield reported per source. The
   9.11%-wrong heuristic era does not return.
2. **The corpus is real text as fetched** — abbreviations, misspellings, c/o lines survive; only
   labels are added. Noise transforms are NOT applied (reality needs no noise).
3. **Dev tier is the new iteration surface.** A stratified holdout (~2,000 aligned rows across
   all states, disjoint by normalized identity from everything) scores candidate-vs-v1 net with
   bootstrap CI. Gold-2 is touched exactly once more, ever, under R-C.
4. **Recipe: real corpus joins, nothing leaves.** v37+ = v36's recipe + realtext corpus at
   weight found by small grid; retained frames and national corpus stay (they carry adjudicated
   conventions and composed coverage that must not regress).

---

## Implementation Units

### U1. Real-text alignment corpus builder

**Goal:** `training/corpus/realtext.jsonl` — ≥50k aligned real lines from ≥25 states, with
per-source yield stats.
**Requirements:** R-A.
**Dependencies:** none.
**Files:** `training/build_realtext_corpus.py` (new), `training/REALTEXT_MANIFEST.json`
(generated), reuses `benchmark/fetch_gold2.py` source configs for bulk sampling.
**Approach:** Sample 3–15k fresh rows per source (offset/window sampling, checkpointed,
outside-OneDrive cache). Alignment ladder per row: (1) tail from source fields; (2) box/unit
extraction by adjudicated conventions; (3) interior exact-match against TIGER FEATNAMES for the
source county/state (cached national sweep already on disk); (4) drop on no-match. Dedupe:
normalized identity vs gold-1, gold-2, clean, and within corpus. Tokens must round-trip
`usaddress.tokenize`.
**Test scenarios:** build-time assertions — zero eval overlaps; zero invalid labels; tokenize
round-trip 100%; yield per source reported and total ≥50k; spot exemplars present (a dropped-
suffix row, a PO Box row, a c/o row labeled Recipient per gold-1 convention if source provides
it, else documented as absent).
**Verification:** manifest shows rows, states, yield rates; validator green.

### U2. Real-text dev tier + spend rule pre-registration

**Goal:** Held-out real-text scorer in the gauntlet; R-C spend rule frozen in PROTOCOL2.
**Requirements:** R-B, R-C.
**Dependencies:** U1.
**Files:** `benchmark/realtext_dev.py` (new), `benchmark/gauntlet.py` (add tier),
`eval/gold2/PROTOCOL2.md` (append spend rule), `eval/realtext_dev.jsonl` (held out, committed).
**Approach:** Stratified ~2,000-row holdout drawn from U1 output before training ever sees it;
scorer reports candidate-vs-v1 net on divergent records with bootstrap CI and per-division
breakdown. Spend rule appended to PROTOCOL2 status log before any v37 scoring.
**Test scenarios:** holdout disjoint from training corpus (asserted); scorer reproduces v36-vs-v1
parity finding directionally on the holdout (sanity anchor); gauntlet refuses candidates missing
the new tier.
**Verification:** gauntlet output includes REALTEXT tier; PROTOCOL2 diff committed before v37.

### U3. Generation v37+: train, iterate on dev tier

**Goal:** A candidate green on all existing surfaces AND beating v1 on the real-text dev holdout
with CI excluding zero.
**Requirements:** R-B.
**Dependencies:** U1, U2.
**Files:** `training/train.py` (`--realtext` flag), `model/candidates/`, manifests.
**Approach:** Small grid over realtext weight × c1 (winning mf=0 held); fast gates per cell;
full gauntlet incl. real-text tier for survivors. Diagnose-and-fix loops run against the dev
holdout only.
**Test scenarios:** Test expectation: none — selection governed by the gauntlet.
**Verification:** one candidate meets R-C's bar; cumulative candidate count reported.

### U4. Gold-2b insurance source list

**Goal:** Documented source list for a future gold-2b (unused counties within fetched states +
untried second-choice counties in gap states).
**Requirements:** R-D. **Dependencies:** none (parallel).
**Files:** `eval/gold2/GOLD2B_SOURCES.md` (new).
**Test scenarios:** Test expectation: none — documentation.
**Verification:** list exists with disjointness note vs gold-2 sources.

### U5. Spend decision, gold-2 attempt 2, ship flip

**Goal:** If and only if R-C's bar is met: score gold-2 (attempt 2 of 2), and on pass execute the
prior plan's ship flip (artifact promotion, feature default-on, docs, adoption section, attempt
counts disclosed). On fail: publish, gold-2 spent, gold-2b becomes the path.
**Requirements:** R-C, R-E. **Dependencies:** U3 (+U4 as fallback).
**Files:** `benchmark/score_gold2.py` (reuse), `eval/gold2/PROTOCOL2.md` (status log), ship-flip
files per prior plan U8.
**Test scenarios:** Test expectation: none — evaluation and release mechanics under frozen gates.
**Verification:** PROTOCOL2 log entry either way; both outcome paths pre-scripted before the run.

---

## Scope Boundaries

**In scope:** the transfer gap, and only it.
### Deferred to Follow-Up Work
- Default-flip 2.0 decision; NAD unit enrichment; constrained decoding (unchanged from prior plans).
### Outside this product's identity (origin)
- Accuracy claims not backed by the gated, auditable evaluation.

---

## Risks & Mitigations

- **Alignment yield too low** (<50k): widen sources (more counties per state via the same
  configs) before loosening matching — looseness is how the heuristic era started.
- **Real corpus regresses composed greens**: cumulative gauntlet catches it; recipe keeps the
  composed corpus in the mix.
- **Dev-holdout overfitting across iterations**: holdout is large (2,000) relative to iteration
  count and the final exam (gold-2) remains untouched until R-C's bar is met; attempt count
  discloses everything.
- **Tonight-scale timeline**: bulk sampling and training run in background; human-dependent steps
  (none until a Round-8-style confirmation if gold-2 attempt 2 fires) are the only serialization.
