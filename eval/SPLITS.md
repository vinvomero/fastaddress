# Evaluation-split ledger

Append-only. Every geography or dataset ever used for training, scanning, or validation is
recorded here with its role and what spent it. A binding draw is legal only if its counties
appear nowhere below; the gauntlet refuses overlapping draws mechanically. Entries are never
edited or removed — corrections append.

## Free-text sets

| Asset | Contents | First used | Status |
|---|---|---|---|
| Clean set | 159 records, upstream usaddress held-out XMLs | 2026-08-13 | regression gate; never iterated against |
| Gold-1 | 1,500 records: Cook County IL mail (900, 878 IL), NYC (225), us-addrs cases (375, 51 states thin) | 2026-08-13 | verdicts fixed (5 human rounds); steered v19–v23; regression gate |
| Gold-2 | state-stratified free-text, ~30/state (U6, being built) | — | claim tier; budget: max 2 scorings, then gold-2b |

## Composed (TIGER) county splits

| Split | Counties (FIPS) | First used | Role | Spent by |
|---|---|---|---|---|
| 18-county training/scan corpus (the "16-state scan") | 17031, 48201, 49035, 22071, 13121, 12086, 06037, 36061, 04013, 53033, 35001, 42101, 08031, 37119, 30111, 46103, 20173, 29095 | 2026-08-14 | training data (tiger.jsonl experiment) + dev-tier scan | steered v24–v28 |
| 32-state holdout | 39049, 26081, 51059, 25027, 47037, 18097, 27053, 55025, 41051, 40143, 01073, 05119, 09110, 10003, 15003, 19153, 16001, 21111, 23005, 24005, 28049, 31055, 33011, 34003, 38017, 32031, 44007, 45045, 50007, 54039, 56021, 02020 | 2026-08-15 | geographic holdout | steered v29–v31 |
| 20-county final split | 48029, 06073, 12057, 36029, 17097, 53063, 04019, 08041, 37183, 29189, 22033, 49049, 13067, 42091, 39035, 26163, 47157, 27123, 45079, 23031 | 2026-08-15 | binding validation (v31) | spent 2026-08-15: FAIL (AZ 5:41, GA 4:33); failures feed U1 taxonomy |

## Training-data counties (non-TIGER sources)

| Source | Geography | Role |
|---|---|---|
| Cook County IL parcel/mail rolls | 17031 | distant supervision + gold-1 |
| Allegheny County PA parcel rolls | 42003 | distant supervision |
| NYC open data | 36061 (+boroughs) | benchmark + gold-1 |

## Rules (pre-registered; see plan U5/R-F and PROTOCOL.md)

1. A **binding split** draws only counties absent from every table above; the draw is appended
   here (with date, spec, and the ≥20-divergents threshold) **before** the run.
2. One binding attempt per candidate **generation** — a committed corpus/recipe changeset with a
   pre-registered failure diagnosis. Grid cells within one corpus share one attempt.
3. Binding draws are stratified to include at least one U1-taxonomy hard-class geography.
4. The ship-time findings report states the cumulative binding-attempt count across all
   generations.
5. TIGER vintage is part of the spec (currently 2024); a vintage change makes counties
   non-comparable and is recorded as a new ledger era.

## Binding attempts

| # | Date | Candidate generation | Split spec | Result |
|---|---|---|---|---|
| 1 | 2026-08-15 | v29–v31 lineage (pre-ledger; counted retroactively) | 20-county final split above | FAIL (per-state 3:1: AZ, GA) |
