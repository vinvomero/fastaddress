# Gold-2b Pass-Through Fidelity Checks — Five Provenance-Flagged Sources

Date: 2026-08-16. Executed under the human ruling recorded in the final status-log entry of
`eval/gold2/PROTOCOL2.md` (item 4): the provenance-flagged publishers (AL, LA, TX, MS, WA)
are included **conditional on documented pass-through fidelity** — (a) the mailing-address
fields genuinely originate from the stated county assessor roll; (b) the intermediary did
not normalize or reconstruct the mailing line; (c) sampled records remain raw free text.
Any source failing the check is dropped, not argued for. TX (unofficial AGOL republication)
got the most aggressive inspection.

## Method

1. **Candidate-to-parcel mapping.** Each flagged state's 73 in-set records were re-matched
   to source rows by re-querying the intermediary layer at the same manifest fetch windows
   and rebuilding the raw string with `benchmark/fetch_gold2b.py`'s `build_raw`; matching by
   normalized identity recovered parcel IDs for **73/73 records in all five states**
   (evidence: `C:/cargo-target/us-address-parser/gold2b_cache/probes/fidelity_<ST>_map.json`).
2. **Seeded samples** (seed 20260819): 10 parcels for TX, 6 each for AL/LA/MS/WA
   (`probes/fidelity_<ST>_sample.json`).
3. **Official cross-check** of every sampled parcel against the assessor's own public
   lookup, by parcel ID (TX/AL/MS/WA) or owner name + roll year (LA). Verbatim both-sides
   evidence in `probes/fidelity_<ST>_verify.json`. Scripts:
   `gold2b_cache/fidelity.py`, `gold2b_cache/fidelity_verify.py` (60s timeouts, 2 attempts).
4. **Pass-through vs normalization tells** examined on both the sampled parcels and
   dataset-wide field statistics (abbreviation variety, truncations, typos, malformed
   zips, care-of lines vs uniform USPS-standardized reconstruction).

Where the intermediary snapshot is older than the current roll, mismatches from ownership
changes were resolved by querying the official roll **at the snapshot's own vintage year**
(possible for TX and LA, whose official lookups expose historical years).

## Verdicts

| State | Source (intermediary) | Official reference used | Verdict |
|---|---|---|---|
| TX | Bexar County Parcels, BCAD attributes (third-party AGOL copy) | BCAD property search (`bexar.trueautomation.com/clientdb`, linked from bcad.org), incl. per-year pages | **PASS** |
| AL | Montgomery County Parcel Boundary via ALEA-hosted service | Montgomery County Revenue Commissioner GIS backend (`al03montrevenue.kcsgis.com` MapServer/29, behind isv.kcsgis.com/al.montgomery_revenue) | **PASS** |
| LA | Slidell planning layer w/ St. Tammany assessor owner mailing (consultant-published) | STPAO property search, legacy roll archive 2001-2021 (`propertysearch.stassessor.org/assessor22.php`, linked from stpao.org) | **PASS** |
| MS | Harrison County parcels via Gulfport-Biloxi Airport GIS | Harrison County property lookup (Delta Computer Systems `cgi-lrm5`, MS24), by PPIN | **PASS** |
| WA | Pierce County parcels via City of Milton planning layer | Pierce County official Tax_Parcels service (PCWA org) + King County GIS / eReal Property | **FAIL — dropped** |

## TX — Bexar (most aggressive: 10 parcels) — PASS

The AGOL copy carries BCAD PACS export fields (`Prop_ID`, `MAIL_LINE1/2`, `MAIL_CITY/STAT/ZIP`,
`TAX_YEAR=2022`); `Prop_ID` resolves directly in BCAD's own search.

- **10/10 sampled parcels verified against the official BCAD search.** 7/10 matched the
  current (2026) roll verbatim on owner + mailing street line, e.g. Prop_ID 690230
  official "21523 TENORE / SAN ANTONIO, TX 78259-2118" vs copy "21523 TENORE / SAN ANTONIO
  TX 78259"; Prop_ID 314102 "24903 BIRDIE RDG" both sides.
- The 3 apparent mismatches were re-checked on the official **2022-year** pages (the copy's
  TAX_YEAR) and all 3 matched character-for-character at vintage:
  - 1009159: official 2022 "9739 CEREMONY CV" = copy "9739 CEREMONY CV" (BCAD itself later
    changed it to "9739 CEREMONY COVE" in the 2026 roll — the suffix change is upstream,
    not intermediary normalization);
  - 360201: official 2022 "GARCIA INOCENCIO / 6406 RIDGE PASS DR" = copy exactly
    (parcel later sold);
  - 690087: official 2022 "B GREEN 2 LLC / 6197 S RURAL RD STE 103 / TEMPE, AZ 85283" =
    copy exactly.
- **Pass-through tells, dataset-wide** (n=665,130): abbreviation variety survives —
  `MAIL_LINE2 LIKE '% COVE%'` = 1,279, `'% ROAD%'` = 1,313, `'% STREET%'` = 646, alongside
  the abbreviated CV/RD/ST forms — i.e. NOT uniformly USPS-standardized.
- **Documented caveats (omissions, not rewrites):** the copy's `MAIL_LINE1`
  (addressee/care-of overflow) is empty across the entire dataset (0 of 665,130 populated;
  official pages show e.g. "SILVIA LAINES" as a second addressee line for Prop_ID 473107,
  absent from the copy), and `MAIL_ZIP` is effectively ZIP5 (19 of 665,130 contain a
  hyphen) while the official display carries ZIP+4. Both are field-level omissions that
  reduce tail difficulty; neither alters the assessor-written street line, and no record in
  the set contains intermediary-composed text.

## AL — Montgomery via ALEA-hosted service (6 parcels) — PASS

The county's own official viewer (isv.kcsgis.com/al.montgomery_revenue, KCS backend layer
"Parcels", RecordYear 2026) exposes the **identical schema** to the ALEA-hosted copy
(RecordYear 2025) — same field names and the same fixed-width space padding — i.e. both are
extracts of the same county CAMA roll, one year apart.

- **5/5 vintage-comparable parcels matched character-for-character** on
  MailAddress1/City/State/Zip, including punctuation and malformed-zip quirks preserved on
  both sides: PID 2205210000009001 "P.O. BOX 22 / VERBENA AL 36109" (periods kept);
  PID 1106242025005000 "713 GENETTA CT / MONTGOMERY AL **36104-0000**" (the -0000 zip
  artifact appears identically in the official roll — proof the quirk is upstream);
  PID 1104201008006002 "3461 OLD SELMA RD / MONTGOMERY AL 36108-3707".
- The 6th (PID 2205210000018002) changed owner between 2025 and 2026 (NEWELL MELINDA →
  IBEY SHANNON D) with a new mailing address — vintage drift, not divergence.
- Free-text tells in the copy, dataset-wide (n=104,809): `MailAddress1 LIKE '%C/O%'` = 346;
  abbreviation variety `'% ROAD%'` = 3,059 alongside `'% RD%'` = 16,516. Within the 73
  in-set AL records: ROAD 5 vs RD 21, and "P.O. BOX" (2) vs "PO BOX" (5) side by side.

## LA — Slidell / St. Tammany via consultant layer (6 owners) — PASS

The layer's assessor attributes are a ~2006-vintage St. Tammany roll extract (ADD_DATE
epoch 2006-03-25). STPAO's official legacy search exposes certified rolls 2001-2021, so
every sample could be checked **at vintage**.

- **6/6 matched the official STPAO roll verbatim** (owner string incl. "ETUX" convention +
  mailing line + city/zip):
  - "PENNINGTON, LARRY ETUX | 103 S HOLIDAY DR SLIDELL, LA 70461" (asmt 123-016-8904);
  - "BUSH, THOMAS ROBERT ETUX | 556 DRIFTWOOD CIRCLE" — unabbreviated CIRCLE on both sides;
  - "HEBERT, HARRY JOSEPH JR ETUX | 677 DALE DR"; "AUTRY, JOHN L ETUX | 1011 BELVEDERE DR";
  - "KUHLMANN, MERWYN LEE ETUX | 250 TEDDY AVE" — official rolls 2004-2013 say "TEDDY AVE",
    2014+ say "TEDDY AV": the copy carries the at-vintage form, and the abbreviation drift
    is the assessor's own;
  - "EDWARDS, JAMES PRINTESS | 919 MAINE ST" — official 2003-2013 "MAINE ST", 2014+
    "MAINE AVE": same at-vintage agreement;
  - "MARTINEZ, JOHN F | 512 POPLAR DR" with layer CARE_OF "CORWIN, MICHELLE S ETAL" —
    and the official 2006 roll shows "512 POPLAR DR" and "512 POPLAR **DRIVE**"
    side-by-side on two parcels of the same owner: the abbreviation variety originates in
    the assessor roll itself.
- Truncation tell preserved: "SLIDELL CITY OF | PO BOX" (box number missing) in the layer.

## MS — Harrison via airport-authority GIS (6 parcels + 1 quirk case) — PASS

PPIN/parcel IDs from the airport layer resolve directly in Harrison County's official
Delta lookup (MS24; tax year 2025, records updated 8/15/2026); the layer is an older
snapshot of the same roll.

- **4/6 matched verbatim** on mailing line + city/state/zip: PPIN 74231 "ROBARE MELINDA
  VIAL | 2820 WILLIAMS BLVD | KENNER LA 70062" (identical both sides); PPIN 13987 "TUBRE
  ROBERT G | 2940 CYPRESS CREEK DR | D'IBERVILLE MS 39540"; PPIN 12733 mailing "2178
  HARMANSON VUE | BILOXI MS 39531" identical (owner later became "-TRUSTEE-"); PPIN 118785
  mailing line "879 BRENTWOOD DR" identical across an ownership change.
- 2/6 (PPIN 14950, 61335) show post-snapshot sales: owner and mailing both replaced in the
  current roll — vintage drift on the same parcel IDs, consistent with an older copy of
  the same roll, not with reconstruction.
- **Quirk-preservation case:** PPIN 100588, official detail mailing "23589 **TALLY** SHAW
  RD / PERKINSTON MS 39573" while the official situs line is "23589 **TALLEY** SHAW RD" —
  the layer's MAIL_1 carries the same idiosyncratic "TALLY" spelling. A normalizing
  intermediary would not reproduce the assessor's mailing-side misspelling.
- Free-text tells: "ROAD 429"/"RD" variety, "PASS CHRISTIA" truncation, deed-acre
  "(600.00 AC)" strings (recorded at build), "P O BOX" spacing variants.

## WA — Pierce via City of Milton planning layer — FAIL (records dropped)

The check **disproved criterion (a)** for the majority of the state's records: the Milton
planning layer mixes parcels from TWO counties, and most sampled records originate from the
**King County** assessor roll — not the stated Pierce County roll. King County is an
excluded lineage (used by both gold-2 and the training corpus).

- Of the 73 in-set WA records, only **23 parcels exist in Pierce County's official
  Tax_Parcels service**; 50 do not (`probes/fidelity_WA_county_split.json`).
- **49 of those 50 resolve in King County's official GIS parcel layer** (PIN match;
  situs cities Federal Way / unincorporated King County;
  `probes/fidelity_WA_kc_membership.json`); parcel 3751601801 also resolves in King
  County's eReal Property ("375160-1801"). The remaining 1 (0420161010) was found in
  neither county's current layer.
- Corroborating format tell: the King-side records carry King County's taxpayer-name
  conventions — "+" name separators with fixed-width truncation (e.g. "ALFILER CESAR
  A+JENNA F+JUA", "BOONSRIPAISAL SIAM+ WITTHAN") — 20/50 on the King side vs **0/23** on
  the Pierce side (Pierce uses "&").
- The 23 Pierce-side parcels did verify verbatim against Pierce's official service (e.g.
  parcel 9006700200 "2404 MILTON WAY UNIT F / MILTON, WA / 98354" identical), but the
  source as fetched cannot support the stated provenance for 50/73 records, and 50 of them
  carry excluded-county lineage. Per the ruling ("Any source failing the check is dropped,
  not argued for"), **WA's 73 records are removed from `candidates.jsonl`**, WA is excluded
  from the strict cohort and from the size-floor top-up, and no replacement source is
  sought this session.

## Consequences applied

- WA dropped (73 records removed); strict cohort = 32 states.
- AL, LA, TX, MS retained and eligible for the strict-cohort top-up.
- Cohort membership and totals recorded in `eval/gold2b/COHORTS.json`; top-up fetch
  details appended to `eval/gold2b/FETCH_MANIFEST_2B.md`.
