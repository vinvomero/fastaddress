# Gold-2b Per-State Source Map — Disjoint Free-Text Owner Mailing Sources

Date: 2026-08-16. Built under `eval/gold2/GOLD2B_SOURCES.md` (amended rules) and the
gold-2b pre-registration + correction in `eval/gold2/PROTOCOL2.md`.

**Disjointness bar (amended):** every dataset here was checked against BOTH exclusion
lists — (a) the 41 datasets gold-2 fetched from (`eval/gold2/FETCH_MANIFEST.md`) and
(b) every training-consumed dataset (Cook County IL, Allegheny PA, and the 30 datasets in
`training/REALTEXT_MANIFEST.json` per_source). "Different county, same dataset" does NOT
restore eligibility; a different portal/publisher (different dataset) in the same state does.
The WI/WV/MN statewide aggregates are the documented exception (GOLD2B_SOURCES strategy #1)
— see the review flags section.

**Free-text rule (unchanged from gold-1/gold-2):** owner/taxpayer MAILING address line as
the assessor wrote it; component-assembled text ineligible. Statewide/multi-county
aggregates spot-checked for composed text BEFORE sampling, evidence in
`C:/cargo-target/us-address-parser/gold2b_cache/spotchecks/` and quoted in
`FETCH_MANIFEST_2B.md`.

## Per-state sources

| State | Dataset (publisher) | Excluded-list check | Disjointness rationale |
|---|---|---|---|
| AK | Kenai Peninsula Borough Parcels, redacted-names view (KPB) | gold-2/training used Mat-Su Borough | Different borough, different publisher/dataset. |
| AL | Montgomery County Parcel Boundary (assessor roll, via ALEA-hosted service) | gold-2/training used Jefferson County | Different county/publisher. County identity verified by MailCity/PropertyCity=MONTGOMERY. Provenance flag: layer lives inside a state-agency web-map service, but attributes are the county assessor roll. |
| AR | Hope-area Parcel Ownership from assessor (hopegis; Pike/Hempstead-area roll) | gold-2: gap (statewide CAMP situs-only); training: none | New state vs gold-2. County assessor roll with MailingAd1/2 + city/st/zip stored fields. |
| AZ | Prescott Valley Parcels, Yavapai assessor attributes (Town of Prescott Valley) | gold-2/training used Pima (Tucson) | Different county/publisher. Own_Addr stored line ("1015 FAIR ST STE 310"), zip9-no-hyphen quirks kept as written. |
| CO | Larimer County Tax Parcels (county GIS, maps1.larimer.org) | gold-2/training used San Miguel County | Different county/publisher; SOURCE_MAP's original strong CO lead, never fetched before. |
| CT | — GAP | gold-2/training used the CT statewide CAMA dataset (data.ct.gov) | No disjoint source found: reachable CT parcel layers are either subsets/copies of the statewide CAMA dataset (same dataset-level lineage) or lack owner mailing. |
| DC | — GAP | gold-2 used the ITS Public Extract | Every public DC owner-mailing dataset (Ownerply etc.) is a view of the same OTR ITSPE dataset; dataset-level disjointness is unattainable for DC. |
| DE | Kent County Parcels (county GIS) | gold-2: gap (NCC endpoint broken); training: none | New state vs gold-2; county-published; MAILINGADDRESS + OWNERCITY/STATE/ZIP; "HICKMAN RD"/"HICKMAN ROAD" side-by-side = pass-through. |
| FL | Hernando County Property Appraiser Parcels | gold-2/training used FDOR statewide NAL | Different dataset/publisher (county PA vs state DOR compilation). REVIEW FLAG: Hernando's roll also flows into the FDOR NAL that training sampled — dataset-level disjoint per the amended rule, record-level dedupe enforced. |
| GA | City of Atlanta Tax Parcels 2025 (DCP) | gold-2 used Fulton County | Different publisher/dataset. REVIEW FLAG: Atlanta parcels derive largely from Fulton/DeKalb county CAMA; dataset-level disjoint per rule, record-level dedupe enforced. |
| HI | Maui County Certified Parcels 2020 (county GIS) | gold-2: gap; training: none | New state vs gold-2. County-published with MailAddr/MailAddr2 + city/state/zip + care-of. |
| IA | Scott County Cadastral Parcels (county GIS) | gold-2/training used Linn County | Different county/publisher. |
| ID | — GAP (legal) | — | Idaho Code 74-120, carried over. |
| IL | Lake County Tax Parcels (county open data) | training used Cook + Winnebago (also gold-2) | Different county/publisher (DuPage/Kane were the doc's examples; Lake County converted first). |
| IN | Vanderburgh County Assessor Parcel Data | gold-2/training used Marion County (Indy) | Different county/publisher (county assessor open-data portal). |
| KS | — GAP | gold-2/training used City of Maize (Sedgwick Co.) | No disjoint source converted: Sedgwick County's own open-data parcels are geometry-only (no owner fields); Johnson/Shawnee/Riley/Wyandotte/Saline/Reno portals expose no owner-mailing layers; remaining AGO hits were tiny consultant subsets. |
| KY | — GAP (legal/fee) | — | Fee-based PVA rolls, carried over. |
| LA | Slidell parcels w/ St. Tammany assessor owner mailing | gold-2 used East Baton Rouge Parish | Different parish/dataset. Provenance flag: consultant-published planning layer carrying parish assessor mailing fields (MAIL_ADDRE + city/state/zip + CARE_OF). |
| MA | Boston Property Assessment FY26 (city Assessing) | gold-2/training used MassGIS statewide | Different publisher/dataset (city assessing DB vs MassGIS compilation). REVIEW FLAG: Boston's data also feeds MassGIS statewide; dataset-level disjoint per rule, dedupe enforced. |
| MD | City of Gaithersburg Parcels | gold-2 used Baltimore City CAMA | Different city/publisher. Small dataset (2,965 rows) but line fields verified. |
| ME | — GAP | gold-2/training used the Organized Towns ADB (statewide) | Maine assesses by town through the state parcel program; no reachable town-published owner-mailing dataset outside that program found this session. |
| MI | Ottawa County Parcel Assessment Data (county GIS) | gold-2/training used Detroit | Different county/publisher. |
| MN | Statewide opt-in aggregate (MnGeo) | fetched by gold-2; NOT consumed by training (single-blob tail) | GOLD2B_SOURCES #1 exception — see review flags. Fresh spot-check passed. |
| MO | St. Charles County Tax Information (county open data) | gold-2/training used City of Independence (Jackson Co.) | Different county/publisher. Single free-text mail-to line incl. tail as written. |
| MS | Harrison County parcels via Gulfport-Biloxi Airport public GIS | gold-2: gap; training: none | New state vs gold-2. County assessor roll (OWNER, MAIL_1/2 + city/st/zip) republished by the airport authority for noise mitigation; n~100k = Harrison County. Free-text tells: "ROAD 429"/"RD" variety, "PASS CHRISTIA" truncation. Provenance flag: airport-authority republication, vintage not stated on the layer. MARIS statewide remained unreachable/empty (2023 service returns no layer metadata); Canton city layer rejected (line-only, no tail). |
| MT | Lake County Parcels monthly extract (county-published) | gold-2/training used the statewide Cadastral Framework | Different dataset/publisher. REVIEW FLAG: upstream is the same DOR ORION DB behind the statewide framework; dataset-level disjoint per rule, dedupe enforced. |
| NC | Guilford County Parcels (county GIS) | gold-2/training used NC OneMap statewide | Different publisher/dataset (county CAMA direct vs OneMap compilation). Same lineage caveat as FL/MA (county feeds OneMap); dedupe enforced. |
| ND | Burleigh County Tax Parcels (county GIS) | gold-2/training used Cass County | Different county/publisher. |
| NE | Lancaster County Parcels (LPSNRD view) | gold-2/training used Sarpy County | Different county; the GOLD2B_SOURCES "NE Lancaster" lead. NRD-published view of county assessor data. |
| NH | — GAP | gold-2: gap | Town-based assessing; no machine-fetchable town/city dataset with owner mailing found (GRANIT mosaic carries no owner attributes; city portals expose none). |
| NJ | Newark Parcels with Ownership (city GIS) | gold-2/training used the statewide MOD-IV composite | Different publisher/dataset (city layer). REVIEW FLAG: Newark's MOD-IV records are also inside the statewide composite; dataset-level disjoint per rule, dedupe enforced. |
| NM | Dona Ana County Parcels (Las Cruces DAC_Parcel) | gold-2/training used Santa Fe County | Different county/publisher. CAREOFNAME + MAILADDR1/2 + city/state/zip. |
| NV | Washoe County Parcels, assessor nightly open data | gold-2 used Carson City | Different county; the GOLD2B_SOURCES "NV Washoe" lead, county-published. |
| NY | NYS Tax Parcels Public (GIS Program Office) | gold-2 used Buffalo roll; data.ny.gov roll (7vem-aaz7) recorded components-only/ineligible | Different dataset from both. RPS MAIL_ADDR is a stored line + separate PO_BOX field. Statewide aggregate: composed-text spot-check PASSED (highway-spelling variety, Rd/Road side-by-side, malformed zip9s). |
| OH | Franklin County Parcels (Auditor) | gold-2/training used Cuyahoga | Different county/publisher; SOURCE_MAP's original strong OH lead. |
| OK | Oklahoma County Tax Parcels Public (assessor) | gold-2/training used Canadian County | Different county/publisher (county verified via tax-district names, e.g. "Luther #3"). |
| OR | Lane County Taxlots (LCOG public) | gold-2/training used Deschutes | Different county/publisher. |
| PA | York County Parcels (YCPC open data) | gold-2 used Philadelphia OPA; training used Allegheny | Different county/publisher from both. |
| RI | City of Cranston Parcels (CAMA extract) | gold-2 used Providence 2022 roll | Different city/publisher. OwnerAddress line + city/state/zip ("46 CASTLETON DR" vs "32 COOLSPRING DRIVE" abbreviation variance = pass-through). |
| SC | Kershaw County Parcels (Fairfield/Kershaw/Richland map) | gold-2/training used York County | Different county. taxMailing line + city/state/zip fields. |
| SD | City of Sioux Falls Parcels (Minnehaha/Lincoln) | gold-2/training used Pennington (Rapid City) | Different counties/publisher; also distinct from the never-fetched Minnehaha-county-hub lead. |
| TN | Rutherford County Parcel Data | gold-2/training used Metro Nashville/Davidson | Different county/publisher (county verified via Murfreesboro/La Vergne sample cities). |
| TX | Bexar County Parcels (BCAD attributes, AGOL copy) | gold-2/training used Williamson (Georgetown) | Different county. Provenance flag: third-party AGOL copy of BCAD data; MAIL_LINE1/2 stored lines used, composed MAIL_ADDR concat field NOT used. |
| UT | Millcreek Parcels (Salt Lake County assessor attributes) | gold-2: gap (UGRC LIR lacks owner mailing) | New state vs gold-2. City-published copy of SL County assessor attributes: own_addr line + own_citystate + zip + care_of. |
| VA | City of Newport News Parcels (city GIS, maps.nnva.gov) | gold-2/training used City of Richmond | Different city/publisher. PSTLADDRESS1/2 + city/state/zip ("97 28TH ST, UNIT B" comma style = pass-through). Loudoun/Henrico/VB were probed first and rejected (no mailing, tiny subsets, or biased delinquency lists). |
| VT | — GAP | gold-2/training used VCGI statewide | All VT parcel data flows through the VCGI statewide program (the training dataset); no town-published alternative found. |
| WA | Pierce County parcels via City of Milton planning layer | gold-2/training used King County | ~~Different county (Pierce assessor taxpayer fields), city-published extract.~~ **DROPPED 2026-08-16: pass-through fidelity check FAILED — the Milton layer mixes counties and 50/73 sampled records are King County (excluded lineage) parcels, not Pierce; see `FIDELITY_CHECKS.md`. WA records removed from candidates.jsonl; no replacement this session.** |
| WI | Statewide Parcels V12 aggregate (PSTLADRESS) | fetched by gold-2; NOT consumed by training (single-blob tail) | GOLD2B_SOURCES #1 exception — see review flags. Fresh spot-check passed. |
| WV | WVU GIS Tech Center statewide parcels | fetched by gold-2; NOT consumed by training (single-blob tail) | GOLD2B_SOURCES #1 exception — see review flags. Fresh spot-check passed. |
| WY | Sheridan County Parcels (owner mailing) | pre-registered hard gap | REVIEW FLAG (biggest judgment call): WY's gold-2 gap was availability ("no bulk open source"), not a statute like CA/ID. An open county service with free-text owner mailing now exists. Fetched so the option exists; including WY amends the pre-registered gap list only if Vin approves. Dropping WY costs one jurisdiction (see manifest totals). |
| CA | — GAP (legal) | — | Gov. Code §7928.205, carried over. |

## Review flags (judgment calls for Vin)

1. **WI/WV/MN statewide aggregates.** GOLD2B_SOURCES rule (a) literally excludes every
   dataset gold-2 fetched from — which includes these three — while its strategy #1
   names the same three aggregates the PRIMARY gold-2b leads ("still virgin for
   evaluation" because training could not use single-blob tails), and the task brief
   repeats that instruction. Followed strategy #1: used them, re-spot-checked all
   three before sampling, enforced record-level dedupe against gold-2 (and everything
   else). The tension between rule (a) and strategy #1 is documented here rather than
   silently resolved. Counties sampled this run are random under seed 20260819 and
   may overlap gold-2's county draw; no record-level overlap survives dedupe.
2. **WY inclusion** (see WY row) — pre-registered gap list vs. newly-available source.
3. **Same-lineage different-dataset sources** (FL Hernando vs FDOR NAL; MA Boston vs
   MassGIS; NJ Newark vs MOD-IV composite; MT Lake County vs DOR ORION statewide;
   NC Guilford vs OneMap; GA Atlanta vs Fulton CAMA): eligible under the amended
   rule's "different portal (different publisher/dataset) in the same state remains
   eligible", but the underlying rolls feed the excluded compilations. Record-level
   dedupe removed every exact identity collision (counts in FETCH_MANIFEST_2B.md).
   If Vin wants a stricter lineage bar, these six states need replacement sources.
4. **Provenance-weak publishers** (AL Montgomery via ALEA service; LA Slidell via
   consultant; TX Bexar AGOL copy; SC Kershaw via regional map; WA via Milton city):
   attributes are assessor-roll fields but the publishing account is not the assessor
   itself. Flagged for review; content verified free-text in every case.

## Gaps summary

Legal, carried over: CA (Gov. Code §7928.205), ID (Code 74-120), KY (fee-based PVA).
Pre-registered gap, now available, flagged: WY (fetched, pending review).
No disjoint source found this run: CT, DC, KS, ME, NH, VT (reasons above; the gold-2 and
training datasets for those states remain excluded, which is exactly what makes them hard
the second time).

**Final coverage: 42 states x 73 records = 3,066 (41 states x 73 = 2,993 if WY is dropped
at review — still above both floors). All 9 census divisions covered. DC not covered
(dataset-level disjointness unattainable, see DC row); the PROTOCOL2 coverage floor
counts states, so this does not affect the floor.**

**Update 2026-08-16 (post human ruling + fidelity checks + top-up):** WA dropped
(fidelity FAIL, see `FIDELITY_CHECKS.md`); the 32 surviving strict states topped up to
91 records each per the ruling's size-floor repair. Current file: 41 states, 3,569
records — strict cohort 32 x 91 = 2,912 (floor MET), sensitivity states 9 x 73 = 657
untouched. Cohorts in `COHORTS.json`; top-up details appended to `FETCH_MANIFEST_2B.md`.
Both cohorts still cover 9/9 census divisions.

## Sample-review fixes (recorded for auditability)

A post-assembly review of 2 random records per state caught tail-duplication or zip
artifacts in five sources; each config was corrected and the state refetched (details in
`benchmark/fetch_gold2b.py` config comments and FETCH_MANIFEST_2B fetch logs):
- IL Lake County: lines 2/3 carry the tail; separate city/st/zip fields were duplicates
  (initial "line_2 NOT NULL" correction was itself wrong - tail lives in line_3 - and was
  re-corrected; final n uses the full 278k-row population).
- OH Franklin: PSTLADDRES already embeds the tail; PSTLCITYSTZIP dropped.
- IA Scott: MailAddr2/3 carry the tail; MailZip dropped (tail filter on MailAddr3).
- HI Maui: MailAddr2 is the tail line; MailCity/State/Zip dropped.
- NJ Newark: numeric ZIPCODE artifacts (7112, 7107.1731) normalized to 07112 / 07107-1731
  (undoing a storage artifact, not editing assessor text).
