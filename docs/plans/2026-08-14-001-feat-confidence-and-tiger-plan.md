---

> Historical note (2026-08-16): the confidence error-prediction figures cited in this
> plan (AUC 0.833 et al.) were later found unreproducible from committed artifacts and
> were withdrawn; current regenerable numbers come from `benchmark/confidence_error_auc.py`.
title: "feat: Confidence scores in v1.0 + Census TIGER training corpus"
type: feat
status: completed
date: 2026-08-14
origin: 2026-08-09 requirements brainstorm (pre-repo, kept locally)
---

# feat: Confidence scores in v1.0 + Census TIGER training corpus

## Summary

Two changes of scope, both driven by the same decision: put the *quality* of the launch ahead of
the *date* of it. Confidence scores move from v1.1 into the initial release, and the Census
TIGER/Line training corpus moves from a v1.2 item to the front of the model queue. Along the way
the pre-registered gold gate was computed for the first time, and the candidate model missed it.

## Problem Frame

Confidence scores (upstream #337) were ranked as the highest demand-per-effort item in the tracker
and then scheduled *after* launch — which put the single most differentiating feature behind the
one moment it would have been noticed. Nothing about it needs retraining or touches parity: the
weights are already loaded and only the forward-backward pass was missing.

The TIGER item had a worse inconsistency. It had been described in the roadmap as the highest-value
improvement available to the project and simultaneously ranked third, because the ranking optimised
for time-to-launch while the description judged quality. Once the model became launch-critical, the
training data behind it did too.

## What was built

**Confidence scores.** Scaled forward-backward in the vendored `crates/crf` fork (upstream crfs
declares the `MARGINALS` flag and its context fields but never ported CRFsuite's alpha/beta
scores, so they were inert), surfaced through `crates/core` and the PyO3 binding as
`parse_with_confidence` / `tag_with_confidence` / `tag_native_with_confidence`. Opt-in throughout:
the plain `tag()` path allocates nothing extra and is unchanged. Multi-token components report the
**minimum** of their tokens' marginals, so a component is never claimed to be more confident than
its weakest token.

**TIGER/Line corpus** (`training/build_tiger_corpus.py`). FEATNAMES joined to ADDRFEAT on TLID for
house-number ranges and ZIP, then FACES to PLACE for the city — all pure attribute joins, no
geometry. 107,988 sequences across 18 counties chosen for addressing style.

## Verification

| Check | Result |
|---|---|
| Marginals vs `pycrfsuite.Tagger.marginal()` | max abs diff **1.665e-15**, 34,028 positions, 0 Viterbi disagreements |
| Independent second proof | brute-force over all 2^6 label sequences on the toy model, agrees to <1e-12 |
| Four-layer oracle parity, after the change | **0 divergences**, 20,738 addresses |
| Plain `tag()` throughput | no measurable change (noisy machine; interleaved best-of-18) |
| Confidence path cost when requested | ~1.6x |
| Does confidence predict errors | AUC **0.833**; 0 of 47 known-wrong parses above 0.99 |

## What this work found

**The candidate model misses its own pre-registered gate.** Computing the full-set gold margin for
the first time gives **+2.60pp** against a required +3.0pp — and a hard ceiling of +2.80pp even if
every outstanding record is adjudicated favourably. It is not a paperwork problem: clearing the bar
requires fixing more records (45 of 1,500) than the candidate fixes (39). Published in
`benchmark/results/model-v2-findings.md` per the protocol's rule that a miss is reported as
prominently as a ship.

**The margin needs no full-set adjudication.** Records where both models emit the same parse
contribute exactly zero to a margin, so it is decided entirely by the differing records. Valid only
if *every* differing record is judged, so `benchmark/full_set_margin.py` re-derives that set on
each run and names any record lacking a verdict rather than trusting a stored list.

**A "v2" verdict approves a specific parse, not "anything but v1".** The prior check scored a win
whenever a candidate merely differed from the incumbent, so a new model could differ in a way
nobody judged and be credited for it — the same structural blindness behind two earlier false "no
regressions" claims. `--judged-parse` now requires the candidate to reproduce the parse the
reviewer actually saw; a third reading counts as unknown.

**Three label-mapping traps, each caught by checking rather than assuming.** `StreetNamePostModifier`
appears in upstream's labeled.xml but is absent from the model's 26-label set — mapping to it would
have trained a label the decoder cannot emit and pushed the count to 27, silently disabling the
`viterbi_unrolled::<26>` fast path. `PREQUALABR` is a pre-modifier only when a pre-type follows it.
And rows whose tokens `usaddress.tokenize` would not reproduce (a bare `-`) crash upstream's own
feature extractor.

## Scope Boundaries

- No change to compat-mode behaviour or the pinned v1 model. Parity is still the product.
- No accuracy claim is made anywhere on the strength of a model that missed the gate.
- NAD was evaluated, not built: reachable and public domain (r23), but it answers the same
  street-split question TIGER already answers. Its distinct value is unit fields and real house
  numbers, which is a later lever.

## Outstanding

Only 6 of the 46 decisive gold records carry the human review the protocol requires, so the gate is
currently unclearable by any model. `tools/make_confirmation_doc.py` generates the blinded
worklist; it should be regenerated against the final candidate so each address is judged once.
