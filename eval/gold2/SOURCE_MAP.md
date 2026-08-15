# Gold-2 Per-State Source Map — Free-Text Owner Mailing Addresses

Date: 2026-08-15. Built as the first action of plan unit U6 (docs/plans/2026-08-15-001-feat-ship-model-v2-plan.md).

**Eligibility rule (from gold-1 methodology / PROTOCOL2):** the address line must be free text as
assessors/humans wrote it — a single line like `123 N MAIN ST APT 4` (city/state/zip may be separate
fields or a second free-text line). Component-assembled text (separate house-number/street-name/suffix
fields) is INELIGIBLE. Owner/taxpayer MAILING address strongly preferred over situs.

**Verification tiers used below:**
- `yes (verified)` — a 1-row API fetch or field-schema probe was performed in this session and the
  free-text line field was seen directly.
- `yes (docs)` — an authoritative schema document names the free-text field; no live fetch this session.
- `unknown` — a plausible source was found but the mailing-address field (or its format, or bulk
  machine-fetchability) was NOT confirmed. Strength noted per row.
- `components-only` — reachable dataset exists but address is split into parse components (ineligible).
- `gap` — no reachable machine-fetchable free-text source found; reason given.

| State | Dataset | Portal type | URL / endpoint | Address fields | Free-text? | Notes |
|---|---|---|---|---|---|---|
| AL | Jefferson County AL Open Data — parcels | arcgis | https://data-jeffco-al.opendata.arcgis.com/ | mailing addr fields unconfirmed | unknown (moderate) | Vendor stats say 99.8% of 409k parcels carry mailing address; county hub field names not probed. Most AL assessors paywalled (Flagship/Delta). |
| AK | Mat-Su Borough Cadastral Parcels; Anchorage assessment | arcgis | https://data1-msb.opendata.arcgis.com/datasets/MSB::cadastral-parcels/about | unconfirmed | unknown (weak) | MSB open data has ~40 layers incl. parcels; owner-mailing presence unverified. Anchorage bulk is commercial. Risk of gap. |
| AZ | Maricopa County Assessor Data Downloads (CSV) | csv | https://www.mcassessor.maricopa.gov/page/data_sales/ | owner mailing address (per site) | unknown (strong) | Free CSV downloads; site states mailing address included. Field format not probed. ~1.7M parcels. |
| AR | Arkansas GIS Office statewide parcels (CAMP) | csv/shp | https://gis.arkansas.gov/download/ (GeoStor CADAS_PARCEL_*_CAMP) | attrs unconfirmed | unknown (moderate) | Statewide centroid/polygon files; "Landowner-Parcels" search app implies owner attrs; mailing-address presence unverified. |
| CA | — (owner mailing legally restricted) | — | see notes | — | **gap** | Cal. Gov. Code §7928.205 restricts owner mailing addresses from public endpoints statewide (confirmed in LA County docs). Situs-only datasets exist but are components/composed. Hard gap for owner-mailing free text. |
| CO | Larimer County Assessor Public Data Center (Account table); Denver open data alt. | csv | https://www.larimer.gov/assessor/publicdata | ownership + mailing (per site) | unknown (strong) | Free downloadable account table with ownership info; exact field names not probed. |
| CT | CT Parcel and CAMA Data 2024 (statewide) | socrata | https://data.ct.gov/resource/pqrn-qghw.json | `mailing_address` (line) + `mailing_city/state/zip` | **yes (verified)** | 1-row fetch confirmed single free-text line ("24 OAK FARMS RD"). Statewide — covers CT towns. |
| DC | Integrated Tax System Public Extract (ITSPE) | arcgis | https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Property_and_Land_WebMercator/MapServer/53 (also CSV on opendata.dc.gov) | `ADDRESS1`, `ADDRESS2`, `CITYSTZIP` (+`CAREOFNAME`) | **yes (verified)** | Layer probe confirmed 40-char tax-billing address lines. |
| DE | New Castle County GIS hub | arcgis | https://apps-nccde.hub.arcgis.com/ | unconfirmed | unknown (weak) | Bulk owner-mailing data appears commercial (ReportAll/Regrid); county hub parcel attrs not confirmed. Risk of gap. |
| FL | DOR NAL tax-roll files, all 67 counties | csv (zip) | https://floridarevenue.com/property/Pages/DataPortal_RequestAssessmentRollGISData.aspx | `OWN_ADDR1`, `OWN_ADDR2`, `OWN_CITY`, `OWN_STATE`, `OWN_ZIPCD` | **yes (docs)** | Users Guide documents the fields; statewide, free bulk download, annually certified. Excellent source (matches gold-1 style). |
| GA | Fulton County Tax Parcels | arcgis | https://gismaps.fultoncountyga.gov/arcgispub2/rest/services/PropertyMapViewer/PropertyMapViewer/MapServer/11 | `OwnerAddr1`, `OwnerAddr2` (255-char lines) | **yes (verified)** | Field probe confirmed line-oriented owner mailing address. Situs is components (AddrNumber/AddrStreet…) — use OwnerAddr*. |
| HI | Honolulu "Parcels - Tax" open data | arcgis | https://honolulu-cchnl.opendata.arcgis.com/datasets/cchnl::parcels-tax/about | unconfirmed | unknown (weak) | GIS layer likely geometry+TMK only; owner data lives in qPublic (not bulk). Risk of gap. |
| ID | — (owner mailing legally excluded) | — | https://adacounty.id.gov/assessor/assessor-data-analytics/ada-county-assessor-data/ | — | **gap** | Idaho Code 74-120: owner names and mailing addresses excluded from Ada County public files (mailing-list prohibition). No reachable free-text source found. |
| IL | Cook County Assessor — Parcel Addresses | socrata | https://datacatalog.cookcountyil.gov/resource/3723-97qp.json | `mail_address_full` (line) + `mail_address_city_name/state/zipcode_1` | **yes (verified)** | 1-row fetch confirmed ("1450 N DAYTON ST"). Millions of rows, multi-year. |
| IN | Indy/Marion County — Parcels w/ Owner Information & Assessed Values | arcgis | https://data.indy.gov/datasets/IndyGIS::parcels-w-owner-information-assessed-values | owner info incl. address (fields unprobed) | unknown (strong) | Nightly-updated from county assessor; field names/format not probed. |
| IA | Polk County Assessor (search only); no bulk confirmed | — | https://www.assess.co.polk.ia.us/ | — | unknown (weak) | No confirmed machine-fetchable bulk with owner mailing. Check Linn/Johnson county hubs as alternates. Risk of gap. |
| KS | Sedgwick County GIS data downloads | shp/gdb | http://gis.sedgwick.gov/gisdata/default2.asp | ownership attrs unconfirmed | unknown (moderate) | Free shapefile downloads incl. parcel ownership boundaries; mailing-address attribute presence unverified. |
| KY | — (PVA data fee-based) | — | see notes | — | **gap** | Statewide PVA rolls sold per standardized fee schedule; LOJIC parcel layer is restricted to participants and its public metadata shows no owner-address fields. |
| LA | East Baton Rouge Parish Tax Roll | socrata | https://data.brla.gov/resource/myfc-nh6n.json | `taxpayer_addr_1` (line), `taxpayer_addr_2` (city/state/zip line) | **yes (verified)** | 1-row fetch confirmed ("9824 EVERGLADES AVE" / "BATON ROUGE, LA 70814"). |
| ME | Maine Parcels Organized Towns ADB (ownership table) | arcgis | https://maine.hub.arcgis.com/datasets/54cdfff41b214264997d291b76d69886 (+ ADB table) | ownership/mailing "where provided" | unknown (moderate) | Statewide FGDB; ownership table coverage is patchy by town and update cadence irregular. Adequate for ~30 samples if fields check out. |
| MD | Baltimore City Real Property Information | arcgis | https://data.baltimorecity.gov/maps/real-property-information-2 | unconfirmed | unknown (moderate) | Statewide SDAT open dataset (ed4q-f8tm) confirmed to have NO owner-mailing fields (metadata checked) — premise address only, components. Baltimore city layer has a data dictionary not yet read. |
| MA | MassGIS Standardized Assessors' Parcels (statewide) | gdb/shp download | https://www.mass.gov/info-details/massgis-data-property-tax-parcels | `OWN_ADDR` + `OWN_CITY/OWN_STATE/OWN_ZIP` | **yes (docs)** | Assess table documented to carry owner address as a line field; per-town downloads statewide. Not live-probed this session. |
| MI | Detroit Parcels (Current) | arcgis | https://services2.arcgis.com/qvkbeam7Wirps6zC/arcgis/rest/services/Parcels_Current/FeatureServer/0 | `taxpayer_street` ("Full street address on record") + `taxpayer_city/state/zip` | **yes (verified)** | Field probe confirmed full-street-line semantics. ~390k parcels. |
| MN | Parcels, Compiled from Opt-In Open Data Counties (statewide, quarterly) | arcgis/gpkg | https://gisdata.mn.gov/dataset (parcel tag); https://gis.data.mn.gov | GAC standard owner address lines (`OWN_ADD_L1..L3`-style) | **yes (docs)** | GAC parcel attribute standard defines line-oriented owner address; opt-in counties incl. metro. Field spot-check still advised. |
| MS | MARIS county cadastral downloads | shp | https://maris.mississippi.edu/HTML/DATA/County.html | 40+ attrs; owner addr unconfirmed | unknown (moderate) | Statewide county shapefiles; owner-address presence/redaction unverified. |
| MO | St. Louis City parcel database (open data, full DB download) | csv/mdb | https://www.stlouis-mo.gov/data/datasets/dataset.cfm?id=82 | owner address in parcel table (unprobed) | unknown (strong) | Full assessor DB is a free download incl. ownership; field format not probed this session. |
| MT | Montana Cadastral Framework (statewide, monthly per county) | gdb/shp | https://www.msl.mt.gov/geoinfo/msdi/cadastral/ | owner mailing address from DOR ORION (line fields) | **yes (docs)** | State docs: parcels carry owner names and owner addresses. CAMA data dictionary published. |
| NE | Douglas County (Omaha) Assessor "Property Ownership" download | csv/txt | https://www.douglasco.gov/assessor/data-downloads/ | `Mailing_Address_Line_1`, `Mailing_Address_Line_2`, `Mailing_City_Name/State/Zip_Code` | **yes (docs)** | Download page documents exact line fields. Free full-county file. |
| NV | Washoe County Assessor GSA_QuickInfo.zip (nightly) | csv (zip) | https://www.washoecounty.gov/assessor/online_data/DataDownloads.php | ownership + mailing address (layout key in zip) | unknown (strong) | Free nightly full-county extract with layout workbook; exact fields not read this session. Clark County bulk requires signed request — skip. |
| NH | NH GRANIT Parcel Mosaic | arcgis | https://www.nhgeodata.unh.edu/ (NH Parcel Mosaic) | attrs unconfirmed | unknown (weak) | Statewide mosaic downloadable, but owner-mailing attributes uncertain (town-based assessing). Risk of gap. |
| NJ | MOD-IV Tax List database + Parcels composite (statewide) | arcgis/gdb | https://njogis-newjersey.opendata.arcgis.com/ (Parcels and MOD-IV Composite; MOD-IV Tax List Search Plus DB) | owner mailing street/city-state (MOD-IV) | **yes (docs)** | Owner NAME redacted on public service (Daniel's Law) but mailing-address fields present; full MOD-IV table downloadable. Name not needed for gold set. |
| NM | Bernalillo County GIS Open Data parcels | arcgis | https://bernalillo-county-gis-open-data-2-ipgr.hub.arcgis.com/ ; https://www.bernco.gov/planning/gis-overview/download-gis-data/ | Owner Name + Mailing Address (per field list) | unknown (strong) | Vendor field list shows a single Mailing Address field; county hub not probed directly. |
| NY | Buffalo Current Assessment Roll | socrata | https://data.buffalony.gov/resource/4t8s-9yih.json | `mail3` (street line), `mail4` (city, state), `mail_zipcode` | **yes (verified)** | 1-row fetch confirmed line-oriented mailing address ("136 MAYER AVE"). NOTE: NYS statewide roll (data.ny.gov 7vem-aaz7) is COMPONENTS-ONLY (mailing_address_number/street/suff) — ineligible, do not use. |
| NC | NC OneMap Parcels (statewide standardized) | arcgis | https://services.nconemap.gov/secure/rest/services/NC1Map_Parcels/FeatureServer/1 | `MAILADD` ("Full Mailing Address", 200 chars) + `MCITY/MSTATE/MZIP` | **yes (verified schema)** | Service schema confirms free-text full mailing address. Aggregated from county CAMA; spot-check per-county for composed-looking uniformity before sampling. |
| ND | Cass County (Fargo) Hub GIS downloads | arcgis | https://cass-county-hub-casscountynd.hub.arcgis.com/ | attrs unconfirmed | unknown (moderate) | Hub offers GIS data downloads; owner-mailing attribute presence unverified. |
| OH | Franklin County Auditor FTP (full parcel extract) | csv/ftp | https://franklincountyauditor.com/ftp | mailing address (fields unprobed) | unknown (strong) | Free full-county extracts; parcel records documented to include mailing address. Cuyahoga/Hamilton similar as backups. |
| OK | Oklahoma County Assessor data | csv | https://www.okassessor.com/ (data downloads) | owner name + mailing address (per site) | unknown (moderate) | Records documented to include owner mailing address; whether bulk download is free vs fee unconfirmed. |
| OR | Deschutes County assessor roll export | csv | https://www.deschutes.org/assessor (roll download; DIAL) | owner name on title + mailing address (per description) | unknown (strong) | County publishes full roll with 100+ fields incl. owner mailing; exact endpoint/fields to confirm. Multnomah is search-only. |
| PA | Philadelphia OPA Properties | carto sql api | https://phl.carto.com/api/v2/sql?q=SELECT ... FROM opa_properties_public | `mailing_street` (line) + `mailing_address_1/2`, `mailing_city_state`, `mailing_zip` | **yes (verified)** | Live SQL fetch confirmed free-text line ("4715 OAKMONT ST"). Allegheny County (WPRDC CKAN, resource 65855e14-…) as backup. |
| RI | Providence Property Tax Roll (annual) | socrata | https://data.providenceri.gov/resource/c3q4-f95q.json (2022 roll) | `street_1` (line) + `city_1`, `state`, `zip_postal_1` (+ `free_line_2/3`) | **yes (verified)** | 1-row fetch confirmed line-oriented owner mailing address. Newer roll years exist on same portal. |
| SC | Charleston County GIS parcels (self-hosted REST) | arcgis | https://charleston-county-gis-chascogis.hub.arcgis.com/pages/open-data | `OWNER1`, `MAIL_CITY`, `MAIL_ST_NAME`, … | unknown (moderate) — **components risk** | `MAIL_ST_NAME` naming suggests split mailing components; must probe before accepting. Greenville bulk is commercial. SC solicitation-restriction terms apply. |
| SD | Minnehaha County Open Data parcels | arcgis | https://mcgis-minnehahacounty.opendata.arcgis.com/datasets/MinnehahaCounty::parcels/about | Owner Name + Mailing Address (per field list) | unknown (strong) | ~76k parcels, 99.5% with mailing address per vendor stats; county CSV download available; field format unprobed. |
| TN | TN Comptroller Property Assessment Data (86 counties) | csv/arcgis | https://www.comptroller.tn.gov/quick-links/tn-property-assessment-data.html | IMPACT incl. owner mailing address | unknown (strong) | State system covers 86/95 counties; bulk/GIS parcel download offered; whether the download carries owner-mailing lines unconfirmed. Memphis/Shelby REST endpoints are token-gated (checked). |
| TX | HCAD (Harris County) PDATA real_acct extract | csv (zip) | https://hcad.org/pdata/pdata-property-downloads.html | `mail_addr_1`, `mail_addr_2`, `mail_city`, `mail_state`, `mail_zip` | **yes (docs)** | Record layout published; free bulk download; ~1.5M accounts. TAD/DCAD similar as backups. |
| UT | Salt Lake County Parcels LIR | arcgis | https://opendata.gis.utah.gov/datasets/utah-salt-lake-county-parcels-lir | unconfirmed | unknown (weak) | Basic statewide parcels documented WITHOUT owner address; LIR variants may add it but unconfirmed. Risk of gap. |
| VT | VCGI statewide parcels + Grand List join | arcgis | https://vcgi.vermont.gov/data-and-programs/parcel-program | grand-list owner mailing address (line fields) | **yes (docs)** | Grand List contains owner name + mailing address; joined statewide parcel FeatureServer publicly queryable across all 247 municipalities. |
| VA | Richmond GeoHub parcel map / Fairfax county data | arcgis | https://richmond-geo-hub-cor.hub.arcgis.com/datasets/richmond-parcel-map | unconfirmed | unknown (moderate) | Norfolk's Socrata assessment dataset VERIFIED to lack owner mailing (1-row fetch). Richmond/Fairfax candidates unprobed. |
| WA | King County Assessments Data Download — Real Property Account extract | csv (zip) | https://info.kingcounty.gov/assessor/datadownload/default.aspx | `AddrLine` + `CityState` + `ZipCode` (taxpayer mailing) | unknown (strong) | Free full-county extract; AddrLine layout well documented historically, but the FAQ page could not be fetched this session — confirm before pre-registering. |
| WV | WVU GIS Tech Center — statewide surface parcels (Tax Maps) | shp | https://wvgis.wvu.edu/data/dataset.php?ID=371 | IAS owner info; mailing addr unconfirmed | unknown (moderate) | Statewide download for all 55 counties, owner attrs from Integrated Assessment System; mailing-address field unverified. |
| WI | WI Statewide Parcel Map V12 (annual) | gdb/shp | https://www.sco.wisc.edu/parcels/data/ | `PSTLADRESS` ("Full Mailing Address" of owner/tax bill, single field) | **yes (verified schema)** | Schema doc explicitly defines PSTLADRESS as the owner's full mailing address; 3.56M records statewide. Top-tier source. |
| WY | — | — | see notes | — | **gap** | Statewide parcel viewer only (no bulk attrs); county bulk data commercial (Laramie/Natrona). No reachable free-text source found. |

## Summary

**Counts (51 jurisdictions = 50 states + DC):**

- **Verified free-text sources (live fetch or schema probe this session): 11** — CT, DC, GA, IL, LA, MI, NY (Buffalo), NC, PA, RI, WI
- **Docs-verified free-text (authoritative schema named the field; no live probe): 8** — FL, MA, MN, MT, NE, NJ, TX, VT
- **Unverified candidates: 28** — strong: AZ, CO, IN, MO, NV, NM, OH, OR, SD, TN, WA (11); moderate: AL, AR, KS, MD, ME, MS, ND, OK, SC, VA, WV (11); weak: AK, DE, HI, IA, NH, UT (6)
- **Hard gaps: 4** — CA (Gov. Code §7928.205 restriction), ID (Code 74-120 restriction), KY (fee-based PVA rolls), WY (no bulk open source)
- **Components-only findings recorded (ineligible, do not use):** NY statewide roll (data.ny.gov 7vem-aaz7), MD SDAT statewide (ed4q-f8tm — premise address components, no owner mailing), Norfolk VA (no mailing at all), Cambridge MA & Providence use line fields (fine); SC Charleston flagged as components risk.

**Census-division read (9 divisions):**

| Division | Status |
|---|---|
| New England | STRONG — CT, RI verified; MA, VT docs |
| Middle Atlantic | STRONG — NY, PA verified; NJ docs |
| East North Central | STRONG — IL, MI, WI verified; OH, IN strong candidates |
| West North Central | OK — NE, MN docs; MO, SD strong candidates; IA/KS/ND weak-moderate |
| South Atlantic | STRONG — DC, GA, NC verified; FL docs |
| East South Central | **WEAKEST** — zero verified; TN strong candidate, AL/MS moderate, KY gap |
| West South Central | STRONG — LA verified; TX docs; AR/OK moderate |
| Mountain | THIN — MT docs only; AZ/CO/NV/NM candidates; ID/WY gaps; UT weak |
| Pacific | **SECOND WEAKEST** — zero verified; WA/OR strong candidates; CA gap; AK/HI weak |

All 9 divisions have at least one docs-level-or-better source EXCEPT East South Central and Pacific,
which currently rest on strong-but-unverified candidates (TN Comptroller; WA King County / OR Deschutes).
Verifying those two rescues the division floor.

**Is the pre-registered coverage floor (all 9 divisions + ≥40 states) reachable?**

- 19 states are verified-or-docs today. Reaching 40 requires converting ~21 of the 28 candidates.
- Realistic conversion estimate: strong candidates ~9–11 of 11; moderate ~6–8 of 12; weak ~1–2 of 6
  → projected total **~35–40 states**. The floor is **plausible but not comfortable**: hitting 40
  likely requires (a) converting nearly all strong candidates, (b) finding second-choice counties in
  several moderate/weak states (every state has 3+ counties untried here — this map records one
  candidate per state, not an exhaustive search), and (c) accepting that CA/ID/KY/WY are permanent
  gaps (46 states is the effective ceiling without legal-workaround sources).
- The 9-division floor is easier: it needs only TN-or-AL-or-MS plus WA-or-OR-or-AK-or-HI to convert.
- **Recommendation for PROTOCOL2:** draft the enumerated-coverage fallback language ("better across
  N states") now, per the plan's pre-commitment rule; verify TN + WA + the 11 strong candidates
  before pre-registering the gate, since the 40-state claim hinges on them.

**Caveats recorded for the sampler (U6):**
- Statewide GIS aggregates (NC MAILADD, WI PSTLADRESS, MN, MT, ME) are aggregated from county rolls;
  most counties pass through assessor-entered text, but a county could compose the line from
  components during standardization. Before sampling a county from these, eyeball ~50 rows for
  composed-text tells (perfect uniformity, no APT/PO BOX/c-o variants).
- "Verified" here means field semantics, not license review. License/terms capture is still owed per
  source at fetch time (fetch_gold2.py should record terms URL alongside fetch date).
- Socrata/Carto endpoints above are directly `$select`-able and are the cheapest to sample; ArcGIS
  REST layers support `outFields`/`resultRecordCount` paging; CSV/zip sources need one bulk pull each.
