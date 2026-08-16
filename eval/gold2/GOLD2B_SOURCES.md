# Gold-2b insurance source list (RT-U4; amended post-realtext)

Drafted 2026-08-16, while gold-2 attempt 2 was still unspent. Amended 2026-08-16 after gold-2
was spent AND after the real-text training corpus consumed 30 of the gold-2-era source
datasets — the disjointness bar is higher now than when first drafted.

Rule (amended): gold-2b sources must be **disjoint at the dataset level from BOTH** (a)
every dataset gold-2 fetched from (FETCH_MANIFEST.md) and (b) every dataset any training
corpus has consumed — Cook County IL, Allegheny PA, and the 30 state datasets used by
`training/build_realtext_corpus.py` (REALTEXT_MANIFEST.json's per_source list). "Different
county, same dataset" is dataset-level overlap and is **no longer eligible** when that
dataset fed training: an exam drawn from the training distribution would repeat the
dev-holdout selection bias at claim tier. Different portal (different publisher/dataset) in
the same state remains eligible.

## Disjointness strategy (amended)

1. **Statewide aggregates the training corpus could NOT use.** The realtext builder excluded
   single-blob-tail sources (WI, WV, MN) because alignment needs separate tail fields — but
   human adjudication does not. Those spot-check-passed aggregates are still virgin for
   evaluation and are now the primary gold-2b leads.
2. **Second-choice county portals** (distinct publishers) in any state: IL DuPage/Kane,
   NV Washoe, NE Lancaster, and SOURCE_MAP.md's moderate/weak candidate column. A different
   county portal is a different dataset even in a trained state.
3. **Unconverted candidates.** SOURCE_MAP candidates never fetched for gold-2 and never used
   by training remain virgin.
4. **Hard gaps stay hard.** CA/ID/KY/WY legal gaps apply to gold-2b equally; its ceiling is
   the same 46 + DC, and the coverage floor language rules carry over unchanged.

## Size requirement (new, from the gold-2 postmortem)

Gold-2's 1,394 records produced 64 divergents — a resolution of roughly ±1.1 pp, which two
real effects (+0.215, +0.789) both fell under. Gold-2b targets **≥2,900 records** so a
~+0.8 pp true effect is certifiable (CI half-width ≈ 42/sqrt(N) pp at the observed ~4.6%
divergence rate). The 150-record adjudication tripwire carries over unchanged and caps the
human burden regardless of set size.

## Pre-registration requirement

Before gold-2b is scored against anything: fetch under these rules, then append gates to
PROTOCOL2 (same gates, fresh set) — the same commit-before-score discipline as every evaluation
asset in this project.
