# Gold-2 Evaluation Protocol (PROTOCOL2)

Pre-registered before any candidate is scored against gold-2. These gates do not move after
results exist. Companion to `eval/PROTOCOL.md` (gold-1), which remains in force for its sets.

## What gold-2 is

A state-stratified, free-text national gold set, target ~30 records per state, drawn from
county-assessor / tax-roll **owner mailing address** fields — true free text as assessors wrote
it. Composed or component-assembled text is ineligible (gold-1 rule, unchanged). Sources per
state are recorded in `eval/gold2/SOURCE_MAP.md`; states without reachable free-text sources are
documented as gaps, never silently backfilled.

Known constraints from source discovery (2026-08-15, pre-registration): four jurisdictions are
hard gaps for legal or commercial reasons (CA, ID, KY, WY — CA by Gov. Code §7928.205), so the
effective ceiling is 46 states + DC. Statewide GIS aggregates (NC, WI, MN, MT, ME) require a
per-county composed-text spot-check before sampling; counties whose "full mailing address" is
assembled from components during standardization are ineligible.

## Gates (all fixed now)

1. **Margin gate.** Candidate-vs-v1 net margin positive with a 95% bootstrap CI excluding zero
   on the full set. Clean-set and gold-1 regression gates unchanged and simultaneous.
2. **Division gate, with minimum-n.** No census division net-negative, applied only where the
   division has ≥10 divergent records; sub-threshold divisions are reported, not gating.
3. **Coverage floor for "national" language.** All 9 census divisions represented AND ≥40 states.
   Below the floor, the pre-drafted enumerated-coverage phrasing applies: "better across N
   states" with the state list published. The floor was fixed before source discovery completed
   and does not move because discovery makes it look hard.
4. **Two language tiers, pre-drafted.**
   - CI-gate pass: "measurably better than usaddress on a stratified national free-text sample
     (+X pp, 95% CI [a, b]); scoring attempt N of 2 disclosed."
   - Stronger headline requires, additionally: net margin ≥ +1.5 pp on the full set. (Effect-size
     threshold fixed now.)
   - Limitation note that ships with any claim: per-state n≈30 cannot detect concentrated
     sub-state failure classes.
5. **Adjudication-volume tripwire.** If candidate-vs-v1 disagreements exceed 150, the gate
   switches to exhaustive human adjudication of a pre-committed random sample of 150 (seeded,
   sample drawn before any verdicts), with a sampling-adjusted margin CI. The human-only standard
   (only human-reviewed verdicts enter gate arithmetic) is unchanged either way.
6. **Spend budget.** Gold-2 may be scored against candidates at most **twice**. Any public claim
   discloses the attempt count. After the second failure, gold-2 is spent: further claim-tier
   runs require a gold-2b built from sources not used by gold-2.

## Labeling method

Same as gold-1: machine prelabel → LLM-assisted review → human adjudication, blinded A/B with
evidence attached, only human-reviewed verdicts in gate arithmetic, verdicts stored with the
approved label sequence (`judged_labels`) so third readings are impossible by construction.
Adjudication scope: disagreement records only.

## Separation guarantees

No gold-2 record may appear in any training corpus (normalized-identity dedupe, enforced by
builders). Gold-2 sources are disjoint from training-data sources by state-source accounting in
the SOURCE_MAP; Cook County IL and Allegheny PA (training sources) are excluded from gold-2
sampling entirely.

## Status log (append-only)

- 2026-08-15: PROTOCOL2 committed. Source map complete: 11 states verified free-text, 8
  docs-verified, 28 candidates, 4 hard gaps. No candidate has been scored against gold-2.
  Scoring attempts used: 0 of 2.
- 2026-08-16: Gold-2 fetched: 1,394 records, 34/jurisdiction, 40 states + DC, 9/9 divisions —
  **coverage floor MET**. Spot-checks passed on all six statewide aggregates with recorded
  evidence; gaps: CA/ID/KY/WY (legal), AR/DE/HI/MS/NH/UT (no reachable free-text source, reasons
  in FETCH_MANIFEST.md). Dedupe verified zero overlaps. Scoring attempts used: 0 of 2.
- 2026-08-16: **Scoring attempt 1 of 2: FAIL.** Candidate v36 vs v1, 62 disagreements
  human-adjudicated in full (no tripwire): 30 candidate / 27 incumbent / 5 neither.
  Net +0.215 pp, 95% CI [-0.861, +1.291] — includes zero (Gate 1 FAIL). Mountain division
  binding net-negative, -6 on 10 divergents (Gate 2 FAIL). One scoring attempt remains;
  after it, gold-2b from unused sources is required. The composed-tier dominance
  (70.5%/17.3% on the binding split) did not transfer to free text — recorded as the
  central finding for the next generation.
- 2026-08-16: **Spend rule for scoring attempt 2 of 2, frozen before any v37-generation candidate
  exists or is scored.** Attempt 2 fires only for a candidate that (a) beats v1 on the held-out
  real-text dev set (`eval/realtext_dev.jsonl`, stratified, never trained on) with net positive
  divergent-record margin and a 95% bootstrap CI excluding zero, AND (b) is simultaneously green
  on every existing surface: clean 159/159, all human-adjudicated gold-1 verdicts, both national
  scans, all spent splits. No candidate meeting less than this bar may be scored against gold-2.
  After attempt 2, pass or fail, gold-2 is spent and gold-2b (sources disjoint per
  GOLD2B_SOURCES.md) is the only remaining claim path.
- 2026-08-15: Dev holdout carved (`eval/realtext_dev.jsonl`, 2,000 rows, 30 states, seed
  20260818, physically removed from the training corpus before any v37-generation model
  existed). **Anchor result: v36 scores +0.900 pp, 95% CI [+0.300, +1.500] on the dev
  holdout — it PASSES the tier that gold-2 failed.** Cause: selection bias — the holdout
  contains only rows whose interiors aligned exactly against TIGER (55% of raw), while
  gold-2 also contains the unalignable classes (dropped suffixes, misspellings,
  non-TIGER phrases) where v36 lost. The dev tier is therefore easier than gold-2, and
  the frozen spend rule above is a floor, not a predictor. **Additional guard, recorded
  before any v37-generation candidate exists: attempt 2 will not be spent on a candidate
  whose dev-tier net margin does not materially exceed the v36 anchor (+0.900 pp point
  estimate).** This only tightens the frozen rule; nothing is loosened.
- 2026-08-16: **Spend decision: scoring attempt 2 of 2 will be spent on candidate v43.**
  Eligibility under the frozen rule, verified before this entry: real-text dev holdout
  +2.400 pp, 95% CI [+1.750, +3.100] (CI floor above the v36 anchor's +0.900 point
  estimate — tightened guard met); full gauntlet ALL GREEN (clean 159/159; all
  human-adjudicated gold-1 verdicts matched, 115/0; both national scans pass; spent
  20-county split pass). v43 recipe: v36's + realtext corpus at weight 1 + four
  counterweight frames added across v41-v43, each committed before its test
  (git 79b76a8, 644e04e, e3889b5). Cumulative candidate count this generation: 5
  trained (v37, v39, v41, v42, v43), 2 untrainable (v38, v40, memory).
  **Outcome paths, scripted now:** PASS -> ship flip per the prior plan's U8 (artifact
  promotion, model-v2 feature default-on in the same commit, README/provenance/findings
  updated, attempt counts disclosed: binding 2, gold-2 2). FAIL -> published with the
  same prominence, gold-2 is spent, gold-2b (GOLD2B_SOURCES.md) becomes the only claim
  path. Round-8 adjudication is blinded under a fresh key; only human verdicts enter
  gate arithmetic.
- 2026-08-16: **Scoring attempt 2 of 2: FAIL. Gold-2 is spent.** Candidate v43 vs v1,
  64 disagreements human-adjudicated in full (no tripwire): 35 candidate / 24 incumbent /
  5 neither. Net +11 records = +0.789 pp, 95% CI [-0.287, +1.865] — includes zero
  (Gate 1 FAIL). Gate 2 PASS: no binding division net-negative; the Mountain division
  problem from attempt 1 is resolved. Verdicts with approved label sequences in
  verdicts_r8.json. Honest progress note recorded with the fail: the margin moved from
  +3 (attempt 1, v36) to +11 (attempt 2, v43) and the division gate flipped to pass;
  at 64 divergents this set cannot certify an effect below roughly +1.1 pp, and +0.789
  is under that resolution. No claim-tier language may cite gold-2. Further claim-tier
  runs require gold-2b built from GOLD2B_SOURCES.md, subject to the same pre-registered
  discipline and a fresh two-attempt budget.
- 2026-08-16: **Gold-2b pre-registration, committed before any gold-2b record is fetched.**
  All PROTOCOL2 gates carry over unchanged to gold-2b (margin CI gate; division gate with
  min-10; coverage floor 9 divisions + ≥40 states for "national" language, enumerated-coverage
  phrasing below it; two language tiers with the +1.5 pp effect threshold; 150-record
  adjudication tripwire; human-only verdict arithmetic; judged_labels storage), with these
  gold-2b-specific terms fixed now: (1) **size floor 2,900 records** — the gold-2 postmortem
  showed 1,394 records resolve only ~±1.1 pp and two real effects fell under it; below the
  size floor gold-2b may not be scored at all; (2) **source disjointness per the amended
  GOLD2B_SOURCES.md** — dataset-level disjoint from gold-2's fetched datasets AND from every
  training-consumed dataset (Cook IL, Allegheny PA, the 30 realtext datasets); (3) **dedupe**
  by normalized identity against gold-1, gold-2, clean, the realtext training corpus, and
  eval/realtext_dev.jsonl; (4) **spend budget: 2 scoring attempts**, attempt counts disclosed
  in any claim, spend rule for each attempt: candidate green on every existing surface
  (gauntlet ALL GREEN) — the realtext dev-holdout bar and v36-anchor guard carry over;
  (5) same per-state ~n≈30-per-jurisdiction stratified sampling, composed-text spot-check
  requirement for statewide aggregates, gaps documented never backfilled.
- 2026-08-16 (correction, before any fetch): term (5) above is internally inconsistent with
  the 2,900 size floor (30 × ~44 jurisdictions < 2,900). Corrected: sampling is stratified
  **evenly per jurisdiction at whatever per-jurisdiction n meets the size floor** (~65-70
  per jurisdiction at 44 reachable jurisdictions). All other terms unchanged.
- 2026-08-16: **Gold-2b fetched: 3,066 records, 73/jurisdiction × 42 states, 9/9 divisions —
  both floors MET** (survives WY removal at 2,993/41). Independent post-build verification:
  zero overlap with gold-1, gold-2, clean, realtext training corpus, and realtext dev holdout;
  zero internal duplicates. Six former gold-2 gap states converted (AR, DE, HI, MS, UT, WY);
  remaining gaps documented in SOURCE_MAP_2B.md (CA/ID/KY legal; CT, DC, KS, ME, NH, VT
  no-disjoint-source). **Pending human source review before any use** — four flagged judgment
  calls at the top of SOURCE_MAP_2B.md, chiefly the WI/WV/MN statewide aggregates (rule (a)
  vs strategy #1 tension: same datasets gold-2 sampled, different counties, zero record
  overlap; dropping them would break both floors at 2,847/39). No candidate has been scored
  against gold-2b. Scoring attempts used: 0 of 2.
- 2026-08-16: **Human rulings on the four flagged judgment calls, recorded before any scoring
  and before any candidate exists for gold-2b.** The reviewer resolved every ambiguity AGAINST
  post-hoc loosening:
  1. **WI/WV/MN statewide aggregates: EXCLUDED from the primary score.** The rule-vs-strategy
     contradiction is not resolved in favor of inclusion after seeing the data; record-level
     dedupe does not cure the pre-registration problem. Retained only as a clearly labeled
     sensitivity analysis (include-vs-exclude both reported).
  2. **Wyoming: INCLUDED, with explicit amendment disclosure** ("WY was pre-registered as an
     availability gap; an eligible source became available before evaluation and was added
     before scoring") **and a score-without-WY robustness check.**
  3. **Same-lineage sources (FL Hernando, GA Atlanta, MA Boston, MT Lake, NC Guilford,
     NJ Newark): EXCLUDED from the strict headline evaluation.** Upstream rolls feed excluded
     compilations; formatting/convention dependence survives record-level dedupe, so
     "completely disjoint" is not defensible for these six. Included only in a separately
     named dataset-disjoint sensitivity analysis.
  4. **Provenance-flagged publishers (AL, LA, TX, MS, WA; the reviewer wrote "SC" where the
     flagged list has MS — interpreted as the flagged class): INCLUDED conditional on
     documented pass-through fidelity** (fields originate from the stated assessor roll; no
     intermediary normalization/reconstruction of the mailing line; samples remain raw free
     text). Any source failing the check is dropped, not argued for. TX (unofficial AGOL
     republication) gets the most aggressive inspection; if fidelity cannot be established,
     TX is dropped rather than speculated about.
  **Resulting analysis structure, fixed now:** PRIMARY = strict-disjoint cohort (33 states
  before fidelity checks; enumerated-coverage phrasing applies since it sits below the
  40-state floor — the pre-drafted below-floor language rule, unchanged). SENSITIVITY-A =
  dataset-disjoint (adds the six same-lineage states). SENSITIVITY-B = adds WI/WV/MN.
  ROBUSTNESS = primary without WY. **Size floor repair, before any scoring:** the strict
  cohort is topped up from its own already-approved sources to ≥2,900 records (~91/state,
  robust to a TX drop) — more data from approved sources, nothing reweighted, nothing
  removed. Scoring attempts used: 0 of 2.
- 2026-08-16: **Candidate artifact pinning (transparency repair, pre-launch review).** The
  model binaries behind the scored rounds are now committed: round 7's candidate is
  `model/candidates/v36.crfsuite` (sha256/16 `ec5815de46b9602f`, matching
  training/MANIFEST-v36.json) and round 8's is `model/candidates/v43.crfsuite`
  (sha256/16 `c5cbb26b5fe8586c`, matching training/MANIFEST-v43.json). The blind-key files
  themselves are unmodified round artifacts; this entry is the hash linkage.
- 2026-08-16: **Fidelity checks executed; gold-2b final structure locked.** Verdicts
  (evidence in eval/gold2b/FIDELITY_CHECKS.md): AL PASS, LA PASS, TX PASS (10/10 parcels
  verbatim against BCAD's official records at matching vintage), MS PASS, **WA FAIL —
  dropped**: the Milton layer mixed counties, and 49 of 50 non-Pierce parcels were King
  County — excluded training lineage. The fidelity rule caught real contamination.
  Strict cohort topped up 73→91 per state from approved sources, no shortfalls.
  **Final: strict primary 32 states × 91 = 2,912 (size floor MET); sensitivity states
  9 × 73 = 657; grand total 3,569 across 41 states; 9/9 divisions in both cohorts.**
  Cohort membership machine-readable in eval/gold2b/COHORTS.json. Independently verified:
  zero internal duplicates, zero overlap with all exclusion sets. Gold-2b is locked
  pending nothing — it waits for a candidate. Scoring attempts used: 0 of 2.
