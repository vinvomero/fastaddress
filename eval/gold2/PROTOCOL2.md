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
