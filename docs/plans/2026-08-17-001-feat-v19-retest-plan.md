---
title: "feat: Retest v19 — the only candidate that isn't self-damaged"
type: feat
status: active
date: 2026-08-17
origin: gold-2c archaeology (PROTOCOL2, 2026-08-17)
---

# feat: Retest v19

## Summary

Gold-2c showed every candidate from v28 onward is worse than the unmodified original on
independent human-labeled free text, and that v19 — from before the error-class campaign — is
the only model that beats it (+2 of 126; 42/47 on suffix-present against the original's 38).
This plan tests v19 properly against every surface, resolves the gate problem that discovery
creates, and takes the shortest honest path to shipping a v2.

**The goal is a shippable v2. The constraint is that it has to be genuinely better, measured by
something that isn't made of the same material as the training data.**

## The gate problem, stated before any number is generated

v19 will almost certainly fail gate 2 of the current gauntlet — the +3.0pp gold-1 margin —
because that margin was manufactured by the error-class campaign that v19 predates. Gold-2c now
shows that campaign traded real accuracy for gold-1 wins. So a v19 failure on gate 2 is
evidence about the gate, not about v19.

This is the moment where a project cheats: discover an inconvenient gate, quietly relax it,
ship. We do not get to do that. What we may do is pre-register a **new** gate structure for a
**new** line of work, commit it before scoring, and disclose exactly what was already known when
it was written. Both are recorded here.

**Already known when this plan was written** (disclosed, not blind): v19 scores +2 net on
gold-2c with a CI including zero, 42/47 suffix-present, 18/27 recipient. Nothing else about v19
on any modern surface is known. Gold-2b remains unscored against v19 and holds its final
attempt.

## Requirements

- **R-A**: v19's complete, honest profile on every existing surface. Measure before deciding.
- **R-B**: A gate structure for this line, pre-registered before scoring, that gates on
  surfaces which do not share a generative process with training data. Gold-1 margin becomes
  reported-not-gating, with the contamination evidence cited as the reason.
- **R-C**: If v19 clears the new bar, gold-2b's final attempt may be spent on it. If it does
  not, no candidate ships and the finding is published — same rule as always.
- **R-D**: A v19-derived candidate line is permitted (v19's recipe plus fixes that are
  demonstrably neutral-or-better on gold-2c), but nothing from the v2x–v5x line may be revived.
- **R-E**: The default model stays bit-identical to usaddress regardless of outcome.

## Key Technical Decisions

1. **Gold-2c is the qualifying surface; gold-2b is the exam.** Gold-2c has absolute human
   labels on disjoint sources and is reusable, so it can gate candidate selection. It cannot
   make fine rankings between near-identical models (it failed that calibration), so the bar is
   set coarse: a candidate must beat the original by a margin its CI supports, on
   suffix-present specifically.
2. **Gold-1 margin: reported, not gating, for this line.** Justification is on the record and
   measurable: the classes that produce that margin were mined from gold-1's own failures, and
   models optimised for it regress on independent data. Continuing to gate on it would select
   for the exact failure we found. The clean set stays gating — it is upstream's own held-out
   data and nobody studied it.
3. **No new synthetic error classes.** That mechanism is what caused the damage. Any v19-derived
   work uses corpus composition and regularisation only, and every change is checked on
   gold-2c's suffix-present class before anything else.
4. **One shot at the exam.** Gold-2b's remaining attempt is spent once, on the best qualifying
   candidate, and never on a model whose evidence rests on a contaminated surface.

## Implementation Units

### V19-U1. Full profile of v19

**Goal:** every number v19 produces on every surface, in one report.
**Requirements:** R-A. **Dependencies:** none.
**Files:** none new — run existing harnesses.
**Approach:** clean gate + adjudicated records (`full_check`), gold-1 margin (reported),
both national scans, the 20-county split, real-text dev, hard-class dev, gold-2c, gold-2 dev.
Record all of them including the failures.
**Verification:** a single table; no cherry-picking, no surface omitted.

### V19-U2. Pre-register the gate structure for this line

**Goal:** PROTOCOL2 entry fixing what gates and what is merely reported, committed before U3.
**Requirements:** R-B. **Dependencies:** U1 (the profile informs the write-up, and the plan
already discloses the one number known in advance).
**Files:** `eval/gold2/PROTOCOL2.md`.
**Approach:** GATING — clean set 159/159; national scans' two ship rules; gold-2c overall net
positive AND suffix-present at least at parity with the original; gold-2b (the exam, one
attempt). REPORTED ONLY — gold-1 margin, hard-class dev, gold-2 dev, real-text dev, with the
contamination rationale written out. Disclose that v19's gold-2c number was known when this was
written.
**Verification:** committed before any candidate is scored under it.

### V19-U3. v19-derived candidates, if needed

**Goal:** a candidate that clears the U2 bar, if v19 itself does not.
**Requirements:** R-D. **Dependencies:** U1, U2.
**Approach:** start from v19's exact recipe (base + synth 3 + distill 1 + augment 4,
oversample 15, distant-cap 3000, c1 0.1). Permitted moves: c1/c2 sweep, distant-cap, oversample
ratio, and adding the **aligned real-text corpus only if** it improves gold-2c suffix-present —
which the current evidence says it will not, so it is a test, not an assumption. Forbidden:
error-class synthetics, national vocabulary frames, the extended ladder.
**Verification:** gold-2c suffix-present is checked first on every cell; a cell that regresses
it is dropped immediately regardless of other numbers.

### V19-U4. Spend the exam, or don't

**Goal:** gold-2b attempt 2 of 2 on the best qualifying candidate, or a published no-ship.
**Requirements:** R-C, R-E. **Dependencies:** U3.
**Approach:** round-10 review doc over the strict cohort; human adjudication; the four cohort
analyses already fixed by the owner's rulings. On pass: ship v2 opt-in, flip the feature,
update the accuracy record, disclose every attempt count. On fail: publish, and the honest
answer becomes that this project could not build a model better than DataMade's on real text —
which is itself a finding worth the repo it ships in.

## Scope Boundaries

**In scope:** v19 and its direct derivatives; the gate restructure; one exam attempt.
**Out of scope:** reviving any v2x–v5x candidate; new error-class synthetics; changing the
default model; new evaluation-set construction beyond what exists.
**Non-negotiable:** gates are committed before results; failures publish with the same
prominence as passes; the default model stays bit-identical.

## Risks & Mitigations

- **The gate restructure looks like moving goalposts.** Mitigated by writing the rationale and
  the contamination evidence into the protocol *before* scoring, disclosing the one number
  known in advance, and keeping the exam blind. If it still reads as convenient, the honest
  alternative is to ship nothing — which stays on the table throughout.
- **v19 fails the clean set or the scans.** Then it is not shippable and U3 is the only path;
  if U3 finds nothing, no ship.
- **v19's +2 is noise.** It is: the CI includes zero. Gold-2b is the arbiter, which is why the
  exam exists and why one attempt was protected.
- **Time pressure produces a rushed spend.** The exam attempt is one-shot and irreversible.
  It gets spent when a candidate qualifies, not when the clock says so.
