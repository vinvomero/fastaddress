# Model v2 — Findings Report (Round 1: shelved)

Per the pre-registered protocol (eval/PROTOCOL.md), v2 candidates ship only by clearing both
gates. Neither training recipe cleared the clean gate; the v2 selection path remains disabled
(the `model-v2` cargo feature is off). This report has the same prominence a ship would have.

## Results

| Recipe | Corpus | Clean exact match | Clean gate (≥ 99.0%) |
|---|---|---|---|
| original (v1) | upstream's | **100.00%** (159 rows) | baseline |
| v2-r1: c1=0.1, c2=0.01 | 91,429 seqs (labeled.xml + OA Linn 50k + county distant 40k) | 95.60% (CI −8.18..−1.26 vs v1) | **FAIL** |
| v2-r2: r1 + labeled.xml oversampled 20x | 118,309 seqs effective | 95.60%, same 7 misses | **FAIL** |

Gold-set gate: not evaluable this round — 1,500 candidates exist, zero adjudicated (human
adjudication pending per protocol). Even a clean-gate pass could not have shipped yet.

## What the failures are

All 7 clean misses are rare postal patterns: state postal routes ("519 PR 462"), HC/rural boxes
("HC R 32 Box # e3"), business-route highways ("U.S. 17 Business"), no-zip trailing states
("610 EAST MAIN MARION KANSAS"), and type-less occupancy numbers. Memorization was ruled out:
only 11/159 clean rows appear in v1's training labeled.xml, so v1 genuinely generalizes to these
patterns and the current v2 recipes genuinely don't.

**Root cause:** distant-supervision dilution. ~86k structurally simple county pairs (number +
street + city + state + zip) dominate the corpus ~60:1 over the upstream set that carries rare
patterns. 20x oversampling of the upstream set did not restore them — the patterns are
individually near-singletons even oversampled.

## What survives regardless

The eval infrastructure this round produced is permanent: the pre-registered two-gate protocol,
the 1,500-candidate gold set awaiting adjudication, the clean-set convention audit (us50
exclusion), the runtime model loader, the reproducible corpus builder with enforced
train/eval separation (68 overlaps auto-excluded), and a 15-minute retrain loop.

## Recommended next recipes (not yet tried, in order)

1. **Pattern-targeted synthesis:** the failing classes are enumerable (PR/FM/CR routes, HC/RR
   boxes, business highways, zip-less tails). Generate a few thousand labeled examples per class
   from templates — direct treatment, not rebalancing.
2. **Distant-cap reduction** (5k/source) so county pairs season rather than dominate.
3. **Two-stage training** if crfsuite supports warm starts poorly: train on upstream-only, then
   continue on the blend.

Human adjudication of the gold set is the other prerequisite for any future ship decision —
without it, the accuracy half of the story has no gate at all.
