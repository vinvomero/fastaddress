# Gold-2c Per-State Source Map — Disjoint Free-Text Owner-Mailing Sources (DEV SURFACE)

Date: 2026-08-17. Built under the gold-2c pre-registration in `eval/gold2/PROTOCOL2.md`
(2026-08-17 entry).

**What this set is.** Gold-2c is a **dev tier**, not an exam. It exists because both earlier
instruments failed to predict gold-2b (the hard-class tier reported +5.333 pp for a candidate
that scored −0.275 pp on the exam). It may be iterated against freely; **it may never be cited
in a public claim**, and no claim-tier language may reference it. Gold-2b's one remaining
attempt is still the only claim path.

**Disjointness bar (same rule as gold-2b, applied to a larger spent registry).** Every dataset
below was checked against all three exclusion lists before any row was fetched:

| List | Contents | Where it lives |
|---|---|---|
| (a) gold-2 | the 41 datasets gold-2 fetched (+ the NE Blair layer) | `eval/gold2/FETCH_MANIFEST.md` |
| (b) gold-2b | the 42 datasets across BOTH cohorts (strict + sensitivity), including the dropped WA layer | `eval/gold2b/FETCH_MANIFEST_2B.md`, `SOURCE_MAP_2B.md` |
| (c) training | Cook County IL, Allegheny County PA, and the 30 sources in `training/REALTEXT_MANIFEST.json` per_source (the 30 are the gold-2 datasets, same fetch cache; `training/corpus/realtext2.jsonl` is derived from the same cache with `no_fetch: true`, so it adds no dataset) | `training/REALTEXT_MANIFEST.json`, `training/REALTEXT2_MANIFEST.json` |

The check is **executed, not asserted in prose**: `benchmark/fetch_gold2c.py` carries the spent
registry (endpoint-host fragments, dataset names, and per-state spent jurisdiction names) and
`assert_disjoint()` hard-fails before any network call if a configured source collides with it.
`--check` runs it standalone. "Different county, same dataset" does **not** restore eligibility;
a different publisher/portal in the same state does, and every same-lineage case is flagged
below rather than resolved silently.

**Free-text rule (unchanged from gold-1/gold-2/gold-2b):** the owner/taxpayer MAILING address
as the assessor wrote it, from stored line field(s). Component-assembled sources are ineligible
(examples rejected this round are listed at the bottom). Every source here is a single county
or city roll — **no statewide or multi-county aggregate is used**, so the PROTOCOL2
composed-text spot-check for aggregates does not bind; a composed-text sample was still taken
and recorded per source in `FETCH_MANIFEST_2C.md`.

**Enrichment.** This set deliberately over-samples the classes that decided gold-2b (suffix
present vs. omitted, recipient/c-o/trustee prefixes, box forms, spelled-out types and
directionals, unit forms including inverted ones). That is legitimate *only* because this is a
dev surface, exactly as the pre-registration says. Rows are **selected, never synthesized or
edited**; achieved counts and the pool supply behind them are in `FETCH_MANIFEST_2C.md`.

## Per-state sources (25 states, 600 records)

| State | Dataset (publisher) | Checked against | Disjointness proof |
|---|---|---|---|
| AL | Baldwin County Parcels, Revenue Commission roll (hosted by KCS GIS, vendor ISV) | (a)(b)(c) | gold-2/training used Jefferson County; gold-2b used Montgomery County. Different county, different host. **Provenance flag:** vendor-hosted publication, same class as gold-2b's AL/LA/TX flags; content is the county roll (`P O BOX 221`, `ROW BUREAU 1409 COLISEUM BLVD` recipient lines = pass-through). |
| AZ | Navajo County Parcels TGI (Navajo County AGOL org) | (a)(b)(c) | gold-2/training used Pima (Tucson); gold-2b used Yavapai (Prescott Valley). Different county/publisher. Mixed-case stored lines (`2291 W Plum Blossom Ln`), zip9-no-hyphen tails kept as written. |
| CO | Boulder County Parcels Owner (county-hosted, maps.bouldercounty.org) | (a)(b)(c) | gold-2/training used San Miguel; gold-2b used Larimer. Different county, county's own server. CareOf line + MailAddr1/2 + city/state/zip. |
| FL | Volusia County Parcel Ownership (county-hosted, maps5.vcgov.org) | (a)(b)(c) | gold-2/training used the FDOR statewide NAL; gold-2b used Hernando County. Different county/publisher. **Lineage flag:** Volusia's roll also feeds the FDOR NAL — record-level dedupe removed 46 identity collisions against the realtext training corpus and 1 against the dev holdout, which is the flag doing visible work. |
| IA | Cerro Gordo County Parcel Points (county GIS AGOL org) | (a)(b)(c) | gold-2/training used Linn; gold-2b used Scott. Different county/publisher. Carries an explicit attention line (`C/O TRUSTEES OF THE …`) — a target class. |
| IL | Whiteside County Tax Parcels (county GIS AGOL org) | (a)(b)(c) | gold-2/training used Winnebago; gold-2b used Lake; training also consumed Cook. Different county/publisher. `%ROBERT L ROSENGREN MNGR 9803 POLO RD` = pass-through free text. |
| IN | St. Joseph County parcels via City of South Bend GIS (city-hosted) | (a)(b)(c) | gold-2/training used Marion (Indy); gold-2b used Vanderburgh. Different county. **Publisher flag:** city-published copy of the county assessor roll. Mixed case with stored abbreviations (`1414 Kessler Pl.`). |
| LA | Livingston Parish Assessor Parcels (parish assessor AGOL org) | (a)(b)(c) | gold-2 used East Baton Rouge; gold-2b used St. Tammany (via Slidell). Different parish/publisher. Leading-space and spelled-out variants (`  739 DARIN DRIVE  `) preserved. |
| MD | Washington County Parcels property view (county GIS AGOL org) | (a)(b)(c) | gold-2 used Baltimore City CAMA; gold-2b used Gaithersburg. Different county/publisher. `C/O GERRY M REID 15213 NATIONAL PIKE` = recipient prefix as stored. |
| ME | City of Biddeford Mailing List Parcels (city-hosted, gis.biddefordmaine.org) | (a)(b)(c) | gold-2/training used the statewide Organized Towns ADB; **ME was a documented gold-2b gap.** **JUDGMENT CALL, flagged not resolved:** Biddeford is an organized town whose assessing may also flow into the state parcel program, so this is a different dataset/publisher rather than a provably independent lineage. Included because a dev surface may carry a flagged source; if the same source is ever wanted for a claim surface it needs a human ruling first. |
| MI | Bloomfield Township (Oakland County) Tax Parcels | (a)(b)(c) | gold-2/training used Detroit (Wayne); gold-2b used Ottawa. Different county/publisher. Mixed case with inline unit (`195 W 9 Mile # 110`) and suffix-omitted rows (`193 Dourdan`). |
| MS | DeSoto County Parcels (parcel publication AGOL org) | (a)(b)(c) | gold-2 recorded MS as a gap; gold-2b used Harrison County. Different county. **Provenance flag:** the publishing account is a private/consultant AGOL org, not the county assessor; content is the assessor roll (second-owner name line + street line + city/state/zip). |
| MT | Ravalli County Parcels (county planning AGOL org) | (a)(b)(c) | gold-2/training used the statewide Cadastral Framework; gold-2b used Lake County. Different county/publisher. **Lineage flag:** upstream is the same MT DOR ORION database behind the statewide framework — identical to the flag gold-2b carried for MT. |
| NC | Onslow County Parcels (county-hosted, gismaps.onslowcountync.gov) | (a)(b)(c) | gold-2/training used NC OneMap statewide; gold-2b used Guilford. Different county/publisher. **Lineage flag:** county CAMA also feeds OneMap. |
| ND | Grand Forks Parcel Owner Info Active (city GIS AGOL org) | (a)(b)(c) | gold-2/training used Cass County; gold-2b used Burleigh. Different county/publisher. Recipient lines stored in the label block (`LIFE ESTATE DARYL NIKLE 1517 6TH AVE N`). |
| NJ | Sussex County Tax Parcel Features (county AGOL org) | (a)(b)(c) | gold-2/training used the statewide MOD-IV composite; gold-2b used Newark. Different county/publisher. **Lineage flag:** municipal MOD-IV records also sit inside the statewide composite (same flag gold-2b carried for Newark); 8 identity collisions against the realtext training corpus were removed. |
| NM | City of Alamogordo / Otero County parcels ETJ (city AGOL org) | (a)(b)(c) | gold-2 used Santa Fe County; gold-2b used Dona Ana. Different county/publisher. Single stored blob with an embedded newline before the tail (whitespace normalized, text unedited). |
| NY | Oswego County Active Tax Parcels (county AGOL org) | (a)(b)(c) | gold-2 used the Buffalo roll; gold-2b used the NYS statewide tax-parcel layer; the data.ny.gov roll was recorded components-only. Different dataset from all three. **Lineage flag:** county RPS records also appear in the NYS statewide layer. Rich route/abbreviation variety (`810 Co Rt 5`, `301 County Route 5`, `8858 Warming Spgs`). |
| OH | Stark County Parcels, County Auditor (county-hosted, scgisa.starkcountyohio.gov) | (a)(b)(c) | gold-2/training used Cuyahoga; gold-2b used Franklin. Different county, auditor's own server. Free-text tells: `316 HAMILTON AVE NE AVE NE` (duplicated suffix), `218 CLEVELAND AVE POB 24218`, `839 E MARKET ST SUITE 106`. |
| PA | Crawford County Tax Parcels Open Data (county GIS AGOL org) | (a)(b)(c) | gold-2 used Philadelphia OPA; gold-2b used York; training consumed Allegheny. Different county/publisher from all three. `RD.`/`ROAD`/`STREET` side by side = pass-through. |
| SC | Georgetown County Parcel Assessment Table (county-hosted portal) | (a)(b)(c) | gold-2/training used York County; gold-2b used Kershaw. Different county/publisher. Billing address line + city/state/zip; `225 HODGE DRIVE` vs `93 HODGE DR` adjacent. |
| TN | Washington County Parcels (county GIS AGOL org) | (a)(b)(c) | gold-2/training used Metro Nashville/Davidson; gold-2b used Rutherford. Different county/publisher. Spelled-out types at high frequency (`4 RESTON COURT`, `216 EMERALD CHASE CIRCLE`). |
| TX | Denton County Parcels, Denton CAD attributes (county GIS AGOL org) | (a)(b)(c) | gold-2/training used Williamson (Georgetown); gold-2b used Bexar (BCAD AGOL copy). Different county/publisher; county's own GIS org, so no third-party-copy flag this time. |
| VA | Bedford County Real Estate Ownership master table (county-hosted) | (a)(b)(c) | gold-2/training used City of Richmond; gold-2b used City of Newport News. Different jurisdiction/publisher. |
| WI | City of Milwaukee MPROP parcels (city-hosted, milwaukeemaps.milwaukee.gov) | (a)(b)(c) | gold-2 AND gold-2b both used the WI statewide V12 aggregate. **Lineage flag:** MPROP is the city assessor's own master property file — a distinct dataset with its own conventions (`N85W18188 LAWRENCE AVE` grid addresses) — but Milwaukee County submits parcel data to the statewide aggregate, so lineage independence is not provable. Zero dedupe removals against any list. |

## Judgment calls flagged for human review (not resolved here)

1. **ME Biddeford** — converts a state that gold-2b documented as a hard gap. The gap reason
   was "all town assessing flows through the statewide Organized Towns ADB". This is a
   city-published assessing extract: a different dataset and publisher, but the same
   underlying assessing office. Fine for a dev surface; needs a ruling before it could ever
   support a claim surface.
2. **Same-lineage sources** (FL Volusia → FDOR NAL; NJ Sussex → MOD-IV composite;
   NC Onslow → OneMap; NY Oswego → NYS statewide; MT Ravalli → DOR ORION; WI Milwaukee →
   statewide V12; IN South Bend → county roll). Eligible under the amended
   different-publisher/different-dataset rule that gold-2b operated under, and record-level
   dedupe removed every exact collision, but the lineage is shared. Gold-2b's owner ruled that
   this class belongs in a *sensitivity* cohort rather than a strict one; that ruling is about
   claim surfaces, so it is recorded here rather than applied.
3. **Provenance-weak publishers** (AL Baldwin via a vendor ISV host; MS DeSoto via a
   private/consultant AGOL org). Attributes are assessor-roll fields; the publishing account is
   not the assessor. Gold-2b's answer to this class was a pass-through fidelity check before
   use; no fidelity check was run here because gold-2c cannot carry a claim. If either source
   is ever promoted, it needs that check first.
4. **Recipient/name lines are included where the assessor stores them inside the mailing
   block** (IA attention line, ND/MS second-name lines, MD/CO care-of lines). This follows the
   gold-2b precedent (MN `own_add_l1..l4`, NE `Attn_Contact`, UT `care_of`, LA `CARE_OF`). It
   is a deliberate choice, not an accident of field selection, and it is what makes the
   `recipient` class measurable at all.

## States not covered, and why

| State(s) | Status |
|---|---|
| CA, ID, KY | **Legal/fee barrier, carried over unchanged** (Gov. Code §7928.205; Idaho Code 74-120; fee-based PVA rolls). Not attempted. |
| NE | **No disjoint source found.** The reachable lead (Lincoln/Lancaster County assessor tax parcels, `gis.lincoln.ne.gov`) is the same county gold-2b sampled through the LPSNRD view; gold-2 already spent Sarpy and Washington (Blair). Left uncovered rather than argued around. |
| CT, VT, DC, NH, KS, MA, MN, WA, GA, and the remaining states | **Not attempted this round.** Gold-2c has no coverage floor — it is a dev surface sized for class signal, not for national coverage — and 25 states already exceed what the enrichment needs. Discovery did surface unused disjoint-looking leads for several of them (WA Thurston County; GA Dougherty County; MN Ramsey County / City of Minneapolis; CT Hartford CAMA — the last one carrying the same statewide-CAMA lineage problem that made CT a gold-2b gap). They are recorded here as headroom, not as coverage. |

## Sources inspected and REJECTED (eligibility rule doing visible work)

- **Jefferson County CO (Jeffco) parcels** — mailing address stored as components
  (`MAILSTRNBR` / `MAILSTRDIR` / `MAILSTRNAM` / `MAILSTRTYP` / `MAILSTRUNT`), no stored line.
  Component-assembled → ineligible under the free-text rule.
- **"Mississippi Parcels and Property Data" (Esri professional-services demo layer)** —
  component fields (`mail_addno`, `mail_addstr`, `mail_addsttyp`) plus a normalized `mailadd`;
  statewide aggregate with an unclear publisher. Rejected on both eligibility and provenance.
- **Wake County NC parcels** — exposes billing *class* codes, not a mailing address line.
- **Third-party pipeline-corridor parcel compilations (TX)** — multi-county consultant
  compilations of CAD data with no stated vintage; rejected on provenance rather than argued.
- **Statewide MA (MassGIS L3) and similar statewide aggregates** — already spent by gold-2 or
  training and excluded by the assertion, which is the point of the registry.

Two row-level exclusions are also enforced in the builder rather than left to the reader:
**non-US rows** (Canadian province + postal-code forms; 1 removed — gold-2b's human review found
15 such records that neither parser labels, so they add noise a dev surface does not need) and
**redaction/placeholder artifacts** (`##########` name lines in the ND source; 2 removed after a
post-assembly sample review, ND refetched). Both are storage junk, not assessor free text.
