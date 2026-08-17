#!/usr/bin/env python3
"""Gold-2c sampler: build a DEV surface of free-text owner-mailing records from
sources disjoint from gold-2, gold-2b (both cohorts) and every training-consumed
dataset.

Status of this set, per the 2026-08-17 pre-registration in eval/gold2/PROTOCOL2.md:
gold-2c is a **dev tier**. It may be iterated against freely and may NEVER be cited
in a public claim. It exists because both previous instruments (the real-text dev
holdout and the hard-class tier) failed to predict gold-2b; gold-2c's job is to stop
gold-2b's last attempt being spent on a guess.

Rules enforced here (in code, not just in prose):
- FREE TEXT ONLY: the mailing address must come from stored line field(s) as the
  assessor wrote them. Component-assembled sources (separate house-number /
  street-name / street-type columns with no stored line) are ineligible and are
  recorded as such in SOURCE_MAP_2C.md rather than configured here.
- DATASET-LEVEL DISJOINTNESS: `assert_disjoint()` runs before any fetch and hard-fails
  if a configured endpoint host, service path or dataset name collides with the spent
  registry below (gold-2's 41 fetched datasets, gold-2b's 42 datasets across both
  cohorts, Cook County IL, Allegheny County PA and the 30 training realtext sources).
  "Different county, same dataset" does not restore eligibility; a different
  publisher/portal in the same state does (and same-lineage cases are flagged in
  SOURCE_MAP_2C.md, never resolved silently).
- ENRICHMENT (legitimate here, and only because this is a dev surface): the assemble
  step deliberately over-samples the classes that decided gold-2b -- suffix present vs.
  omitted, recipient/c-o/trustee prefixes, box forms, spelled-out types/directionals,
  unit forms including inverted ones. Rows are SELECTED, never synthesized or edited.
- DEDUPE by normalized identity (uppercase alphanumeric join) against gold-1, gold-2,
  gold-2b, clean, both training realtext corpora, the realtext dev holdout and the
  hard-class dev holdout, plus within gold-2c itself. Per-list removal counts tracked.
- Every kept row must round-trip usaddress.tokenize (tokens rejoin to the same
  normalized identity), so no row can break a scorer downstream.

Checkpoints: C:/cargo-target/us-address-parser/gold2c_cache/checkpoints/<STATE>.json
(outside OneDrive; delete a file to refetch that state). Fetching is resumable.

Usage:
  python benchmark/fetch_gold2c.py --list
  python benchmark/fetch_gold2c.py --check           # disjointness assertion only
  python benchmark/fetch_gold2c.py --preview OH      # composed-text eligibility look
  python benchmark/fetch_gold2c.py --fetch OH [--want N]
  python benchmark/fetch_gold2c.py --fetch-all
  python benchmark/fetch_gold2c.py --assemble [--target 600]
"""

import argparse
import datetime as dt
import json
import random
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GOLD2C_DIR = ROOT / "eval" / "gold2c"
CACHE = Path("C:/cargo-target/us-address-parser/gold2c_cache")
CKPT_DIR = CACHE / "checkpoints"
EVID_DIR = CACHE / "evidence"
CANDIDATES_OUT = GOLD2C_DIR / "candidates.jsonl"
MANIFEST_OUT = GOLD2C_DIR / "FETCH_MANIFEST_2C.md"

EXCLUSION_FILES = {
    "gold-1": ROOT / "eval" / "gold" / "candidates.jsonl",
    "gold-2": ROOT / "eval" / "gold2" / "candidates.jsonl",
    "gold-2b": ROOT / "eval" / "gold2b" / "candidates.jsonl",
    "clean": ROOT / "eval" / "clean" / "clean.jsonl",
    "realtext-train": ROOT / "training" / "corpus" / "realtext.jsonl",
    "realtext2-train": ROOT / "training" / "corpus" / "realtext2.jsonl",
    "realtext-dev": ROOT / "eval" / "realtext_dev.jsonl",
    "realtext-hard-dev": ROOT / "eval" / "realtext_hard_dev.jsonl",
}

TARGET_TOTAL = 600
PER_STATE_POOL = 400          # rows kept per source before enrichment selection
PER_STATE_CAP = 45            # max rows any one source may contribute to the set
CHUNKS = 6
SEED = 20260820               # fresh seed; gold-2 used 20260815, gold-2b 20260819
TIMEOUT = 60                  # hard 60s per request
RETRIES = 2                   # at most 2 attempts, then the failure is recorded
UA = "fastaddress-gold2c-sampler/1.0 (research dev set; contact: repo maintainer)"

FETCH_DATE = dt.date.today().isoformat()

# ---------------------------------------------------------------------------
# SPENT REGISTRY -- everything gold-2c must be disjoint from.
# (state, dataset label, endpoint/host fragment). Sources: eval/gold2/FETCH_MANIFEST.md,
# eval/gold2b/FETCH_MANIFEST_2B.md + SOURCE_MAP_2B.md, training/REALTEXT_MANIFEST.json
# per_source, plus Cook County IL and Allegheny County PA (training-consumed).
# ---------------------------------------------------------------------------

SPENT = {
    "gold-2": [
        ("AK", "Matanuska-Susitna Borough AK Cadastral Parcels", "maps.matsugov.us"),
        ("AL", "Jefferson County AL Parcels (Basemap)", "jccgis.jccal.org"),
        ("AZ", "Pima County AZ Parcels - Regional", "mapdata.tucsonaz.gov"),
        ("CO", "San Miguel County CO Tax Parcels (Public)", "aXqye4IXyXsdIpPb"),
        ("CT", "CT Parcel and CAMA Data (statewide)", "data.ct.gov"),
        ("DC", "DC Integrated Tax System Public Extract (ITSPE)", "maps2.dcgis.dc.gov"),
        ("FL", "FDOR Florida Statewide Cadastral (NAL owner fields)", "Gh9awoU677aKree0"),
        ("GA", "Fulton County GA Tax Parcels", "gismaps.fultoncountyga.gov"),
        ("IA", "Linn County IA Real Estate Parcels", "i14SLLmXo7Hn9vNc"),
        ("IL", "Winnebago County IL Parcel Ownership", "s8vOzt2hgxqrWawQ"),
        ("IN", "Indy/Marion County Parcels w/ Owner Information", "gis.indy.gov"),
        ("KS", "City of Maize KS Parcels (Sedgwick County)", "PRyeAMTgQS8gkd0F"),
        ("LA", "East Baton Rouge Parish Tax Roll", "data.brla.gov"),
        ("MA", "MassGIS Standardized Assessors' Parcels (statewide)", "hGdibHYSPO59RG1h"),
        ("MD", "Baltimore City MD Real Property CAMA", "UWYHeuuJISiGmgXx"),
        ("ME", "Maine Parcels Organized Towns ADB", "RbMX0mRVOFNTdLzd"),
        ("MI", "Detroit Parcels (Current)", "qvkbeam7Wirps6zC"),
        ("MN", "MN Parcels, Compiled from Opt-In Open Data Counties", "gisdata.mn.gov"),
        ("MO", "City of Independence MO (Jackson County) Parcels", "sbDzK061dd6DNPHv"),
        ("MT", "Montana Cadastral Framework (DOR ORION owner mailing)", "qnjIrwR8z5Izc0ij"),
        ("NC", "NC OneMap Parcels (statewide standardized)", "nconemap.gov"),
        ("ND", "Cass County ND Tax Parcels (Open Data)", "casscountynd.gov"),
        ("NE", "Sarpy County NE Tax Parcels", "geodata.sarpy.gov"),
        ("NE", "Washington County NE Ownership Parcels (Blair)", "ksv1wRvySwOGRs8x"),
        ("NJ", "NJ Parcels and MOD-IV Composite (statewide)", "XVOqAjTOJ5P6ngMu"),
        ("NM", "Santa Fe County NM Land Parcels", "p0Gk2nDbPs7KEqSZ"),
        ("NV", "Carson City NV Assessor Data (AssrData)", "portal.carsoncity.gov"),
        ("NY", "Buffalo NY Current Assessment Roll", "data.buffalony.gov"),
        ("OH", "Cuyahoga County OH Parcels (MyPLACE)", "gis.cuyahogacounty.us"),
        ("OK", "Canadian County OK Parcel Data (Public)", "0NjdXxmJp53hZWPd"),
        ("OR", "Deschutes County OR Taxlots - GIS_MAILING", "znO8Hz1SuVVohYhZ"),
        ("PA", "Philadelphia OPA Properties", "phl.carto.com"),
        ("RI", "Providence RI 2022 Property Tax Roll", "data.providenceri.gov"),
        ("SC", "York County SC Parcels", "2AGLxyiJoNiVHKwq"),
        ("SD", "Rapid City/Pennington County SD Tax Parcels", "gis.rcgov.org"),
        ("TN", "Metro Nashville/Davidson County TN Parcels", "HdTo6HJqh92wn4D8"),
        ("TX", "Williamson County TX Parcels (Georgetown open data)", "gis.georgetowntexas.gov"),
        ("VA", "City of Richmond VA Parcels (GeoHub)", "k3vhq11XkBNeeOfM"),
        ("VT", "VCGI VT Statewide Standardized Parcels", "BkFxaEFNwHqX3tAw"),
        ("WA", "King County WA Parcels with Ownership Information", "Ej0PsM5Aw677QF1W"),
        ("WI", "Wisconsin Statewide Parcels V12 (PSTLADRESS)", "n6uYoouQZW75n5WI"),
        ("WV", "WV Statewide Parcels (WVU GIS Tech Center)", "wvgis.wvu.edu"),
    ],
    "gold-2b": [
        ("AK", "Kenai Peninsula Borough AK Parcels", "ba4DH9pIcqkXJVfl"),
        ("AL", "Montgomery County AL Parcel Boundary", "xNUwUjOJqYE54USz"),
        ("AR", "Hope AR area Parcel Ownership from assessor", "RVMSajYQji1bjmZ4"),
        ("AZ", "Prescott Valley AZ Parcels (Yavapai assessor)", "NxZdAmj8rBzdRpTr"),
        ("CO", "Larimer County CO Tax Parcels", "maps1.larimer.org"),
        ("DE", "Kent County DE Parcels", "gis.kentcountyde.gov"),
        ("FL", "Hernando County FL Property Appraiser Parcels", "x5zvhhxfUuRDntRe"),
        ("GA", "City of Atlanta GA Tax Parcels 2025", "gis.atlantaga.gov"),
        ("HI", "Maui County HI Certified Parcels 2020", "fsrDo0QMPlK9CkZD"),
        ("IA", "Scott County IA Cadastral Parcels", "ovln19YRWV44nBqV"),
        ("IL", "Lake County IL Tax Parcels", "HESxeTbDliKKvec2"),
        ("IN", "Vanderburgh County IN Assessor Parcel Data", "evansvillegis.com"),
        ("LA", "Slidell LA parcels w/ St. Tammany assessor owner mailing", "LJwIycC0yIuqCBxq"),
        ("MA", "Boston MA Property Assessment FY26", "gisportal.boston.gov"),
        ("MD", "City of Gaithersburg MD Parcels", "cbDaIA5xFnHBUlC1"),
        ("MI", "Ottawa County MI Parcel Assessment Data", "gis.miottawa.org"),
        ("MN", "MN Parcels, Compiled from Opt-In Open Data Counties", "gisdata.mn.gov"),
        ("MO", "St. Charles County MO Tax Information", "sccmo.org"),
        ("MS", "Harrison County MS Parcels (Gulfport-Biloxi Airport GIS)", "XwK5zAS8O0b6s3Tp"),
        ("MT", "Lake County MT Parcels (county monthly extract)", "qQ6tqy9VSUry3ySt"),
        ("NC", "Guilford County NC Parcels", "guilfordcountync.gov"),
        ("ND", "Burleigh County ND Tax Parcels", "8r0lsT7QHelkANsD"),
        ("NE", "Lancaster County NE Parcels (LPSNRD view)", "iTf0MCf7KYGMrPY1"),
        ("NJ", "Newark NJ Parcels with Ownership", "WAUuvHqqP3le2PMh"),
        ("NM", "Dona Ana County NM Parcels (Las Cruces DAC_Parcel)", "ejcbAsQEUUGWEyzb"),
        ("NV", "Washoe County NV Parcels (assessor nightly open data)", "iCGWaR7ZHc5saRIl"),
        ("NY", "NYS Tax Parcels Public (GIS Program Office)", "EbVsqZ18sv1kVJ3k"),
        ("OH", "Franklin County OH Parcels (Auditor)", "gis.franklincountyohio.gov"),
        ("OK", "Oklahoma County OK Tax Parcels Public", "euhkr1dAJeQBIjV0"),
        ("OR", "Lane County OR Taxlots (LCOG public)", "NbWCmkRTtvyr63CT"),
        ("PA", "York County PA Parcels (YCPC open data)", "arcweb1.ycpc.org"),
        ("RI", "City of Cranston RI Parcels", "arcgisserver.cranstonri.org"),
        ("SC", "Kershaw County SC Parcels", "RvqSyw3diI7dTKo5"),
        ("SD", "City of Sioux Falls SD Parcels", "gis.siouxfalls.gov"),
        ("TN", "Rutherford County TN Parcel Data", "A5C0MR9xfkxVRwat"),
        ("TX", "Bexar County TX Parcels (BCAD attributes, AGOL copy)", "82iS1Pc7dgs3LFZv"),
        ("UT", "Millcreek UT Parcels (Salt Lake County assessor attributes)", "XRrSFvEwSsReIxuA"),
        ("VA", "City of Newport News VA Parcels", "maps.nnva.gov"),
        ("WA", "Pierce County WA Parcels via Milton Planning (dropped, still spent)",
         "RLW8Rymck77KYbSO"),
        ("WI", "Wisconsin Statewide Parcels V12 (PSTLADRESS)", "n6uYoouQZW75n5WI"),
        ("WV", "WV Statewide Parcels (WVU GIS Tech Center)", "wvgis.wvu.edu"),
        ("WY", "Sheridan County WY Parcels", "V4b98G4pSkzvUam9"),
    ],
    "training": [
        # The 30 realtext sources are the gold-2 datasets above (same fetch cache);
        # these two are the additional training-consumed rolls.
        ("IL", "Cook County IL assessor/parcel data (training-consumed)", "cookcountyil"),
        ("PA", "Allegheny County PA property assessment (training-consumed)", "alleghenycounty"),
    ],
}

SPENT_HOSTS = {h.lower() for lst in SPENT.values() for _, _, h in lst}
SPENT_DATASETS = {d.lower() for lst in SPENT.values() for _, d, _ in lst}
# County/jurisdiction names already spent, per state: a config naming the same
# jurisdiction in the same state must justify itself in SOURCE_MAP_2C.md.
SPENT_JURISDICTIONS = {
    "AK": ["matanuska", "mat-su", "kenai"], "AL": ["jefferson", "montgomery"],
    "AR": ["hope", "pike", "hempstead"], "AZ": ["pima", "tucson", "yavapai", "prescott"],
    "CO": ["san miguel", "larimer"], "CT": ["statewide cama"], "DC": ["itspe"],
    "DE": ["kent"], "FL": ["fdor", "statewide", "hernando"],
    "GA": ["fulton", "atlanta"], "HI": ["maui"], "IA": ["linn", "scott"],
    "IL": ["winnebago", "lake", "cook"], "IN": ["marion", "indy", "vanderburgh"],
    "KS": ["maize", "sedgwick"], "LA": ["east baton rouge", "st. tammany", "slidell"],
    "MA": ["massgis", "boston"], "MD": ["baltimore", "gaithersburg"],
    "ME": ["organized towns"], "MI": ["detroit", "ottawa"], "MN": ["opt-in", "mngeo"],
    "MO": ["independence", "st. charles"], "MS": ["harrison"],
    "MT": ["cadastral framework", "lake"], "NC": ["onemap", "guilford"],
    "ND": ["cass", "burleigh"], "NE": ["sarpy", "washington", "lancaster"],
    "NJ": ["mod-iv", "newark"], "NM": ["santa fe", "dona ana"],
    "NV": ["carson city", "washoe"], "NY": ["buffalo", "nys tax parcels"],
    "OH": ["cuyahoga", "franklin"], "OK": ["canadian", "oklahoma county"],
    "OR": ["deschutes", "lane"], "PA": ["philadelphia", "york", "allegheny"],
    "RI": ["providence", "cranston"], "SC": ["york", "kershaw"],
    "SD": ["pennington", "rapid city", "sioux falls"], "TN": ["davidson", "nashville", "rutherford"],
    "TX": ["williamson", "georgetown", "bexar"], "UT": ["millcreek", "salt lake"],
    "VA": ["richmond", "newport news"], "VT": ["vcgi"], "WA": ["king", "pierce", "milton"],
    "WI": ["statewide parcels"], "WV": ["statewide"], "WY": ["sheridan"],
}

# ---------------------------------------------------------------------------
# Per-source config. `checked` records which exclusion lists the source was
# verified against; `lineage_flag` records an unresolved judgment call that
# SOURCE_MAP_2C.md must surface rather than decide silently.
# ---------------------------------------------------------------------------

CONFIG = {
    "OH": {
        "type": "arcgis",
        "endpoint": "https://scgisa.starkcountyohio.gov/arcgis/rest/services/Auditor/StarkCountyParcels/FeatureServer/0",
        "dataset": "Stark County OH Parcels (County Auditor, mailing label fields)",
        "publisher": "Stark County OH Auditor (scgisa.starkcountyohio.gov, county-hosted)",
        "addr_fields": ["MAILING_ADDRESS1", "MAILING_ADDRESS2", "MAILING_ADDRESS3"],
        "city": None, "st": None, "zip": None,
        "where": "MAILING_ADDRESS1 IS NOT NULL AND MAILING_ADDRESS3 IS NOT NULL",
        "checked": ["gold-2", "gold-2b", "training"],
    },
    "CO": {
        "type": "arcgis",
        "endpoint": "https://maps.bouldercounty.org/arcgis/rest/services/PARCELS/PARCELS_OWNER/FeatureServer/0",
        "dataset": "Boulder County CO Parcels Owner (county assessor)",
        "publisher": "Boulder County CO (maps.bouldercounty.org, county-hosted)",
        "addr_fields": ["CareOf", "MailAddr1", "MailAddr2"],
        "city": "MailCity", "st": "MailState", "zip": "MailZip",
        "where": "MailAddr1 IS NOT NULL AND MailAddr1 <> ''",
        "checked": ["gold-2", "gold-2b", "training"],
    },
    "FL": {
        "type": "arcgis",
        "endpoint": "https://maps5.vcgov.org/arcgis/rest/services/Open_Data/Open_Data_3/FeatureServer/34",
        "dataset": "Volusia County FL Parcel Ownership (Property Appraiser open data)",
        "publisher": "Volusia County FL (maps5.vcgov.org, county-hosted)",
        "addr_fields": ["CAREOF", "MAILADDR1", "MAILADDR2", "MAILADDR3"],
        "city": "MAILCITY", "st": "MAILSTATE", "zip": "MAILZIP",
        "where": "MAILADDR1 IS NOT NULL AND MAILADDR1 <> ''",
        "checked": ["gold-2", "gold-2b", "training"],
        "lineage_flag": "county roll also feeds the FDOR statewide NAL that training "
                        "sampled (same class of flag gold-2b carried for FL Hernando)",
    },
    "IA": {
        "type": "arcgis",
        "endpoint": "https://services7.arcgis.com/qyyoWTywHfayX67L/arcgis/rest/services/Parcel_Points/FeatureServer/0",
        "dataset": "Cerro Gordo County IA Parcel Points (assessor mailing lines)",
        "publisher": "Cerro Gordo County IA GIS (AGOL org qyyoWTywHfayX67L)",
        "addr_fields": ["Tyler_MailAttentionLine", "Tyler_MailLine1", "Tyler_MailLine2"],
        "city": "Tyler_MailCity", "st": "Tyler_MailState", "zip": "Tyler_MailPostalCode",
        "where": "Tyler_MailLine1 IS NOT NULL AND Tyler_MailLine1 <> ''",
        "checked": ["gold-2", "gold-2b", "training"],
    },
    "AZ": {
        "type": "arcgis",
        "endpoint": "https://services.arcgis.com/cghC2lEIpJ2TRrs5/arcgis/rest/services/ParcelsTGI/FeatureServer/0",
        "dataset": "Navajo County AZ Parcels TGI (assessor owner mailing)",
        "publisher": "Navajo County AZ (AGOL org cghC2lEIpJ2TRrs5)",
        "addr_fields": ["MailingAddressLine1", "MailingAddressLine2"],
        "city": "MailingCityStateZip", "st": None, "zip": None,
        "where": "MailingAddressLine2 IS NOT NULL AND MailingAddressLine2 <> ''",
        "checked": ["gold-2", "gold-2b", "training"],
    },
    "NY": {
        "type": "arcgis",
        "endpoint": "https://services3.arcgis.com/0dC3T96jvK0z64NH/arcgis/rest/services/parcelsActive_view/FeatureServer/0",
        "dataset": "Oswego County NY Active Tax Parcels (county real property)",
        "publisher": "Oswego County NY (AGOL org 0dC3T96jvK0z64NH)",
        "addr_fields": ["MAIL_ADDR"],
        "city": "MAIL_CITY", "st": "MAIL_STATE", "zip": "MAIL_ZIP",
        "where": "MAIL_ADDR IS NOT NULL AND MAIL_ADDR <> ''",
        "checked": ["gold-2", "gold-2b", "training"],
        "lineage_flag": "county RPS records also appear in the NYS statewide tax-parcel "
                        "layer gold-2b sampled; different publisher/dataset, dedupe enforced",
    },
    "TX": {
        "type": "arcgis",
        "endpoint": "https://services.arcgis.com/9dTWrhPzuDPnUVXr/arcgis/rest/services/County_Parcels/FeatureServer/0",
        "dataset": "Denton County TX Parcels (Denton CAD owner mailing lines)",
        "publisher": "Denton County TX GIS (AGOL org 9dTWrhPzuDPnUVXr)",
        "addr_fields": ["ADDR_LINE1", "ADDR_LINE2", "ADDR_LINE3"],
        "city": "CITY", "st": "STATE", "zip": "ZIP",
        "where": "ADDR_LINE2 IS NOT NULL AND ADDR_LINE2 <> ''",
        "checked": ["gold-2", "gold-2b", "training"],
    },
    "PA": {
        "type": "arcgis",
        "endpoint": "https://services1.arcgis.com/CcJI8wbz22fo71LO/arcgis/rest/services/CivQuest_Core/FeatureServer/1",
        "dataset": "Crawford County PA Tax Parcels Open Data (assessment mailing)",
        "publisher": "Crawford County PA GIS (AGOL org CcJI8wbz22fo71LO)",
        "addr_fields": ["MAD_MAIL_ADDR1", "MAD_MAIL_ADDR2"],
        "city": "MAD_MAIL_CITY", "st": "MAD_MAIL_STATE", "zip": "MAD_MAIL_ZIP",
        "where": "MAD_MAIL_ADDR1 IS NOT NULL AND MAD_MAIL_ADDR1 <> ''",
        "checked": ["gold-2", "gold-2b", "training"],
    },
    "WI": {
        "type": "arcgis",
        "endpoint": "https://milwaukeemaps.milwaukee.gov/arcgis/rest/services/property/parcels_mprop/MapServer/7",
        "dataset": "City of Milwaukee WI MPROP parcels (city assessor master property)",
        "publisher": "City of Milwaukee (milwaukeemaps.milwaukee.gov, city-hosted)",
        "addr_fields": ["OWNER_MAIL_ADDR"],
        "city": "OWNER_CITY_STATE", "st": None, "zip": "OWNER_ZIP",
        "where": "OWNER_MAIL_ADDR IS NOT NULL AND OWNER_MAIL_ADDR <> ''",
        "checked": ["gold-2", "gold-2b", "training"],
        "lineage_flag": "city assessor MPROP is a distinct dataset from the WI statewide "
                        "V12 parcel aggregate gold-2/gold-2b used, but Milwaukee County "
                        "submits to that aggregate; dedupe enforced",
    },
    "NJ": {
        "type": "arcgis",
        "endpoint": "https://services.arcgis.com/opPd2BqYeMe7vELn/arcgis/rest/services/TaxParcel_Features/FeatureServer/0",
        "dataset": "Sussex County NJ Tax Parcel Features (county tax mailing)",
        "publisher": "Sussex County NJ (AGOL org opPd2BqYeMe7vELn)",
        "addr_fields": ["PSTLADDRESS"],
        "city": "PSTLCITY", "st": None, "zip": "PSTLZIP5",
        "where": "PSTLADDRESS IS NOT NULL AND PSTLADDRESS <> ''",
        "checked": ["gold-2", "gold-2b", "training"],
        "lineage_flag": "municipal MOD-IV records also flow into the statewide composite "
                        "gold-2/training used; different publisher/dataset, dedupe enforced",
    },
    "TN": {
        "type": "arcgis",
        "endpoint": "https://services3.arcgis.com/nLnrKGwI08veJ5uu/arcgis/rest/services/Washington_County_Parcels_view/FeatureServer/0",
        "dataset": "Washington County TN Parcels (assessor mailing lines)",
        "publisher": "Washington County TN GIS (AGOL org nLnrKGwI08veJ5uu)",
        "addr_fields": ["MAILLINE1", "MAILLINE2", "MAILLINE3"],
        "city": None, "st": None, "zip": None,
        "where": "MAILLINE1 IS NOT NULL AND MAILLINE1 <> ''",
        "checked": ["gold-2", "gold-2b", "training"],
    },
    "IN": {
        "type": "arcgis",
        "endpoint": "https://gis.southbendin.gov/arcgis/rest/services/LandRecords/Parcels_County/MapServer/0",
        "dataset": "St. Joseph County IN Parcels via City of South Bend GIS (owner mailing)",
        "publisher": "City of South Bend IN (gis.southbendin.gov, city-hosted)",
        "addr_fields": ["MAILINGADD", "MAILINGA_1"],
        "city": "MAILINGCIT", "st": "MAILINGSTA", "zip": "MAILINGZIP",
        "where": "MAILINGADD IS NOT NULL AND MAILINGADD <> ''",
        "checked": ["gold-2", "gold-2b", "training"],
        "lineage_flag": "city-published copy of the St. Joseph County assessor roll "
                        "(publisher is the city, not the county assessor)",
    },
    "IL": {
        "type": "arcgis",
        "endpoint": "https://services.arcgis.com/l0M0OC6J9QAHCiGx/arcgis/rest/services/Tax_Parcels_Ver_2_Parcels_Only/FeatureServer/0",
        "dataset": "Whiteside County IL Tax Parcels (taxpayer mailing)",
        "publisher": "Whiteside County IL GIS (AGOL org l0M0OC6J9QAHCiGx)",
        "addr_fields": ["PSTLADDRESS", "PSTLADDRESS2"],
        "city": "PSTLCITY", "st": None, "zip": None,
        "where": "PSTLADDRESS IS NOT NULL AND PSTLADDRESS <> ''",
        "checked": ["gold-2", "gold-2b", "training"],
    },
    "NM": {
        "type": "arcgis",
        "endpoint": "https://services1.arcgis.com/tZhkGVr1gXGPSz0S/arcgis/rest/services/Parcels_ETJ/FeatureServer/0",
        "dataset": "Alamogordo NM / Otero County parcels ETJ (owner mailing blob)",
        "publisher": "City of Alamogordo NM (AGOL org tZhkGVr1gXGPSz0S)",
        "addr_fields": ["IN_CARE_OF", "OWNER_ADDR"],
        "city": None, "st": None, "zip": None,
        "where": "OWNER_ADDR IS NOT NULL AND OWNER_ADDR <> ''",
        "checked": ["gold-2", "gold-2b", "training"],
    },
    "MI": {
        "type": "arcgis",
        "endpoint": "https://services.arcgis.com/EZzgO87vB4k7XLB1/arcgis/rest/services/BloomfieldTaxParcels/FeatureServer/0",
        "dataset": "Bloomfield Township MI (Oakland County) Tax Parcels (owner mailing)",
        "publisher": "Bloomfield Township MI land records (AGOL org EZzgO87vB4k7XLB1)",
        "addr_fields": ["PSTLADDRESS"],
        "city": "PSTLCITY", "st": "PSTLSTATE", "zip": "PSTLZIP5",
        "where": "PSTLADDRESS IS NOT NULL AND PSTLADDRESS <> ''",
        "checked": ["gold-2", "gold-2b", "training"],
    },
    "ME": {
        "type": "arcgis",
        "endpoint": "https://gis.biddefordmaine.org/wa2/rest/services/TaxMaps/Mailing_List_Parcels/MapServer/0",
        "dataset": "City of Biddeford ME Mailing List Parcels (city assessing)",
        "publisher": "City of Biddeford ME (gis.biddefordmaine.org, city-hosted)",
        "addr_fields": ["MAD_MAIL_ADDR1", "MAD_MAIL_ADDR2"],
        "city": "MAD_MAIL_CITY", "st": "MAD_MAIL_STATE", "zip": "MAD_MAIL_ZIP",
        "where": "MAD_MAIL_ADDR1 IS NOT NULL AND MAD_MAIL_ADDR1 <> ''",
        "checked": ["gold-2", "gold-2b", "training"],
        "lineage_flag": "ME was a gold-2b documented gap (all town assessing flows through "
                        "the statewide Organized Towns ADB); this is a city-published "
                        "assessing extract, a different dataset/publisher - flagged, not "
                        "silently resolved",
    },
    "AL": {
        "type": "arcgis",
        "endpoint": "https://web6.kcsgis.com/kcsgis/rest/services/Baldwin/Baldwin_Public_ISV/MapServer/31",
        "dataset": "Baldwin County AL Parcels (Revenue Commission roll via KCS GIS ISV)",
        "publisher": "Baldwin County AL Revenue Commission, hosted by KCS GIS (vendor)",
        "addr_fields": ["MailAdd1", "MailAdd2", "MailAdd3"],
        "city": "MailCity", "st": "MailState", "zip": "MailZip1",
        "where": "MailAdd1 IS NOT NULL AND MailAdd1 <> ''",
        "checked": ["gold-2", "gold-2b", "training"],
        "lineage_flag": "vendor-hosted publication of the county roll (provenance-weak "
                        "publisher, same class as gold-2b's AL/LA/TX flags)",
    },
    "MD": {
        "type": "arcgis",
        "endpoint": "https://services2.arcgis.com/uxxyl33jRTSmjre5/arcgis/rest/services/Property_view/FeatureServer/42",
        "dataset": "Washington County MD Parcels property view (owner mailing lines)",
        "publisher": "Washington County MD GIS (AGOL org uxxyl33jRTSmjre5)",
        "addr_fields": ["OwnAdd1", "OwnAdd2"],
        "city": "OwnCity", "st": "OwnState", "zip": "OwnZip",
        "where": "OwnAdd1 IS NOT NULL AND OwnAdd1 <> ''",
        "checked": ["gold-2", "gold-2b", "training"],
    },
    "VA": {
        "type": "arcgis",
        "endpoint": "https://webgis.bedfordcountyva.gov/arcgis/rest/services/OpenData/OpenDataProperty/MapServer/9",
        "dataset": "Bedford County VA Real Estate Ownership master table (owner mailing)",
        "publisher": "Bedford County VA GIS (webgis.bedfordcountyva.gov, county-hosted)",
        "addr_fields": ["OwnerAddress1", "OwnerAddress2"],
        "city": "OwnerCity", "st": "OwnerState", "zip": "OwnerZip",
        "where": "OwnerAddress1 IS NOT NULL AND OwnerAddress1 <> ''",
        "checked": ["gold-2", "gold-2b", "training"],
    },
    "LA": {
        "type": "arcgis",
        "endpoint": "https://services8.arcgis.com/IUHRIaPhRaOrUMFb/arcgis/rest/services/Livingston_Parish_Assessor_Parcels/FeatureServer/0",
        "dataset": "Livingston Parish LA Assessor Parcels (owner mailing)",
        "publisher": "Livingston Parish LA Assessor (AGOL org IUHRIaPhRaOrUMFb)",
        "addr_fields": ["Owner_Addr"],
        "city": "Owner_City", "st": None, "zip": None,
        "where": "Owner_Addr IS NOT NULL AND Owner_Addr <> ''",
        "checked": ["gold-2", "gold-2b", "training"],
    },
    "MT": {
        "type": "arcgis",
        "endpoint": "https://services8.arcgis.com/M9lBa5KYtuKzdhNy/arcgis/rest/services/Parcels/FeatureServer/45",
        "dataset": "Ravalli County MT Parcels (county planning publication)",
        "publisher": "Ravalli County MT Planning (AGOL org M9lBa5KYtuKzdhNy)",
        "addr_fields": ["CareOfTaxp", "OwnerAddre"],
        "city": "CityStateZ", "st": None, "zip": None,
        "where": "OwnerAddre IS NOT NULL AND OwnerAddre <> ''",
        "checked": ["gold-2", "gold-2b", "training"],
        "lineage_flag": "upstream is MT DOR ORION, the same DB behind the statewide "
                        "Cadastral Framework gold-2/training used (same flag gold-2b "
                        "carried for MT Lake County)",
    },
    "ND": {
        "type": "arcgis",
        "endpoint": "https://services5.arcgis.com/tEvkdB384rqq9Ook/arcgis/rest/services/OpenDataLayers/FeatureServer/50",
        "dataset": "Grand Forks ND Parcel Owner Info Active (city/county open data)",
        "publisher": "City of Grand Forks ND GIS (AGOL org tEvkdB384rqq9Ook)",
        "addr_fields": ["OwnerAddress1", "OwnerAddress2"],
        "city": "OwnerCity", "st": "OwnerState", "zip": "OwnerZip",
        "where": "OwnerAddress2 IS NOT NULL AND OwnerAddress2 <> ''",
        "checked": ["gold-2", "gold-2b", "training"],
    },
    "MS": {
        "type": "arcgis",
        "endpoint": "https://services5.arcgis.com/nbwtrV1EDhKfIQhm/arcgis/rest/services/DESOTO_PARCELS/FeatureServer/0",
        "dataset": "DeSoto County MS Parcels (tax assessor mailing lines)",
        "publisher": "DeSoto County MS parcel publication (AGOL org nbwtrV1EDhKfIQhm)",
        "addr_fields": ["MAILADD1", "MAILADD2"],
        "city": "MCITY2", "st": "MSTATE2", "zip": "MZIP2",
        "where": "MAILADD2 IS NOT NULL AND MAILADD2 <> ''",
        "checked": ["gold-2", "gold-2b", "training"],
        "lineage_flag": "publisher account is a private/consultant AGOL org, not the "
                        "county assessor; content is the assessor roll (provenance flag)",
    },
    "SC": {
        "type": "arcgis",
        "endpoint": "https://gis1.georgetowncountysc.org/portal/rest/services/GCGIS_OpenData/FeatureServer/7",
        "dataset": "Georgetown County SC Parcel Assessment Table (billing/mailing address)",
        "publisher": "Georgetown County SC GIS (gis1.georgetowncountysc.org, county-hosted)",
        "addr_fields": ["BillingAddress", "BillingAddress2"],
        "city": "City", "st": "State", "zip": "ZipCode",
        "where": "BillingAddress IS NOT NULL AND BillingAddress <> ''",
        "checked": ["gold-2", "gold-2b", "training"],
    },
    "NC": {
        "type": "arcgis",
        "endpoint": "https://gismaps.onslowcountync.gov/server/rest/services/WEB_PUBLICATIONS/County_Map_Layers/MapServer/0",
        "dataset": "Onslow County NC Parcels (county tax mailing lines)",
        "publisher": "Onslow County NC GIS (gismaps.onslowcountync.gov, county-hosted)",
        "addr_fields": ["ADDRLINE1", "ADDRLINE2"],
        "city": "MAILCITY", "st": "MAILSTATE", "zip": "MAILZIP",
        "where": "ADDRLINE1 IS NOT NULL AND ADDRLINE1 <> ''",
        "checked": ["gold-2", "gold-2b", "training"],
        "lineage_flag": "county CAMA also feeds NC OneMap (used by gold-2/training); "
                        "different publisher/dataset, dedupe enforced",
    },
}

# ---------------------------------------------------------------------------
# Disjointness assertion -- runs before any network call.
# ---------------------------------------------------------------------------


def assert_disjoint(verbose=True):
    problems = []
    for state, cfg in sorted(CONFIG.items()):
        ep = cfg["endpoint"].lower()
        for host in SPENT_HOSTS:
            if host in ep:
                problems.append(f"{state}: endpoint matches spent host fragment '{host}'")
        if cfg["dataset"].lower() in SPENT_DATASETS:
            problems.append(f"{state}: dataset name collides with a spent dataset")
        for jur in SPENT_JURISDICTIONS.get(state, []):
            if jur in cfg["dataset"].lower():
                problems.append(
                    f"{state}: dataset names spent jurisdiction '{jur}' - same "
                    f"county/dataset as an exam or training source")
        missing = [n for n in ("gold-2", "gold-2b", "training") if n not in cfg["checked"]]
        if missing:
            problems.append(f"{state}: config not marked checked against {missing}")
    if problems:
        print("DISJOINTNESS ASSERTION FAILED:", file=sys.stderr)
        for p in problems:
            print("  - " + p, file=sys.stderr)
        raise SystemExit(3)
    if verbose:
        print(f"disjointness assertion PASSED for {len(CONFIG)} sources "
              f"({len(SPENT['gold-2'])} gold-2 + {len(SPENT['gold-2b'])} gold-2b + "
              f"{len(SPENT['training'])} training datasets in the spent registry)")


# ---------------------------------------------------------------------------
# HTTP (same machinery as fetch_gold2b.py: 60s timeout, at most 2 attempts)
# ---------------------------------------------------------------------------


def http_get(url, retries=RETRIES):
    last = None
    for _ in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2)
    raise RuntimeError(f"GET failed after {retries} tries: {url} ({last})")


def get_json(url):
    return json.loads(http_get(url).decode("utf-8", "replace"))


def arcgis_query(endpoint, params):
    params = dict(params)
    params["f"] = "json"
    d = get_json(endpoint + "/query?" + urllib.parse.urlencode(params))
    if "error" in d:
        raise RuntimeError(f"ArcGIS error: {str(d['error'])[:200]}")
    return d


# ---------------------------------------------------------------------------
# Text assembly / normalization
# ---------------------------------------------------------------------------


def norm_identity(raw: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", raw.upper())


def clean_part(v):
    if v is None:
        return ""
    s = str(v).replace("\r", " ").replace("\n", " ").strip()
    if s.lower() in ("null", "none", "nan"):
        return ""
    return re.sub(r"\s+", " ", s)


TAIL_LINE_RE = re.compile(r"[A-Za-z][A-Za-z .'\-]{1,30},?\s+[A-Za-z]{2}\.?[ ,]*"
                          r"(?:\d{5}(?:-?\d{4})?|\d{9})?\s*")


def build_parts(cfg, row):
    """Returns (street_part, full_raw). street_part = the addr_fields text only,
    used for class tagging; full_raw = what goes into the set."""
    addr = [clean_part(row.get(f)) for f in cfg["addr_fields"]]
    addr = [p for p in addr if p]
    # A stored line that is purely "CITY, ST ZIP" is the tail line: it belongs in the
    # record text but not in the street text used for class tagging.
    street_lines = [p for p in addr if not TAIL_LINE_RE.fullmatch(p.strip())]
    tail = []
    for key in ("city", "st", "zip"):
        if cfg.get(key):
            v = clean_part(row.get(cfg[key]))
            if v:
                tail.append(v)
    parts, seen_prev = [], None
    for p in addr + tail:
        if seen_prev is not None and p.strip().upper() == seen_prev:
            continue
        seen_prev = p.strip().upper()
        parts.append(p)
    raw = re.sub(r"\s+", " ", " ".join(parts)).strip()
    street = re.sub(r"\s+", " ", " ".join(street_lines or addr)).strip()
    first = addr[0] if addr else ""
    return street, raw, first


PLACEHOLDER_RE = re.compile(r"(^|\s)([#*]{3,}|[Xx]{6,}|\?{3,})(\s|$)|"
                            r"\b(UNKNOWN OWNER|NO ADDRESS|NOT AVAILABLE|SEE DEED)\b", re.I)


def plausible(street, raw):
    if len(street) < 3 or len(raw.split()) < 3:
        return False
    if not re.search(r"[A-Za-z]", street):
        return False
    # Redaction/placeholder artifacts are storage junk, not assessor free text.
    if PLACEHOLDER_RE.search(raw):
        return False
    return True


# ---------------------------------------------------------------------------
# Class tagging (enrichment targets from the gold-2c pre-registration)
# ---------------------------------------------------------------------------

SUFFIX_ABBR = {"ST", "RD", "AVE", "AV", "DR", "LN", "CT", "BLVD", "BLV", "WAY", "PL",
               "TER", "TERR", "TRL", "CIR", "HWY", "PKWY", "PKY", "PLZ", "SQ", "LOOP",
               "RUN", "PT", "XING", "CV", "BND", "RDG", "TRCE", "EXPY", "FWY", "BYP",
               "MNR", "HOLW", "CRK", "SPUR", "CRES", "GRV", "PATH", "PIKE", "TPKE",
               "SPGS", "SPG", "HTS", "VLG", "PLN", "PLNS", "FLS", "ISL", "LK", "MDW",
               "MDWS", "GLN", "GDN", "GDNS", "CYN", "HL", "HLS", "VW", "WLS", "XRD",
               "RTE", "RT", "CIRC", "CTR", "EST", "ESTS", "FRK", "FRD", "GTWY"}
SUFFIX_WORD = {"STREET", "ROAD", "AVENUE", "DRIVE", "LANE", "COURT", "BOULEVARD",
               "PLACE", "TERRACE", "TRAIL", "CIRCLE", "HIGHWAY", "PARKWAY", "PLAZA",
               "SQUARE", "CROSSING", "COVE", "RIDGE", "MANOR", "HOLLOW", "CREEK",
               "EXPRESSWAY", "FREEWAY", "BYPASS", "TURNPIKE", "CRESCENT", "GROVE"}
DIR_TOK = {"N", "S", "E", "W", "NE", "NW", "SE", "SW"}
DIR_WORD = {"NORTH", "SOUTH", "EAST", "WEST", "NORTHEAST", "NORTHWEST",
            "SOUTHEAST", "SOUTHWEST"}
UNIT_TOK = {"APT", "UNIT", "STE", "SUITE", "LOT", "TRLR", "BLDG", "RM", "ROOM", "SPC",
            "SPACE", "FL", "FLR", "FLOOR", "DEPT", "SLIP", "HNGR", "PIER", "OFC", "NO"}
BOX_RE = re.compile(r"(\bP\.?\s?O\.?\s?BOX\b|\bPOB\b|\bPOBOX\b|\bBOX\s+[\dA-Z]|"
                    r"\bR\.?\s?R\.?\s?\d|\bRTE?\.?\s+\d+\s+BOX|\bROUTE\s+\d+\s+BOX|"
                    r"\bH\.?\s?C\.?\s?\d|\bSTAR\s+ROUTE\b)", re.I)
RECIP_RE = re.compile(r"(\bC/O\b|\bC\.O\.|\bC\s+O\s+[A-Z]|\bC-O\b|\bATTN?\b|"
                      r"\bIN\s+CARE\s+OF\b|\bTRUSTEE|\bTRUST\b|\bET\s?AL\b|%|"
                      r"\bCUSTODIAN\b|\bESTATE\s+OF\b|\bPERS\s+REP\b|\bLIFE\s?EST)", re.I)
INVERTED_UNIT_RE = re.compile(r"(\b\d{1,3}(ST|ND|RD|TH)\s+(FLOOR|FL|FLR)\b|"
                              r"\b(FLOOR|FLR)\s+\d|\b(REAR|BASEMENT|"
                              r"PENTHOUSE|PH)\b|\b(NORTH|SOUTH|EAST|WEST)\s+(WING|TOWER)\b)",
                              re.I)
CITY_TAIL_RE = re.compile(r"[,\s]+[A-Za-z][A-Za-z .'\-]{1,28},?\s+[A-Za-z]{2}\.?\s*"
                          r"\d{5}(?:-?\d{4})?\s*$")
NON_US_RE = re.compile(r"\b(ON|BC|AB|QC|NS|NB|MB|SK|NL|PE|YT|NT|NU)\b\s*"
                       r"[A-Z]\d[A-Z]\s?\d[A-Z]\d|\b(CANADA|ONTARIO|BRITISH COLUMBIA|"
                       r"ALBERTA|QUEBEC)\b", re.I)


def street_core(street: str) -> str:
    """If a stored line embeds its own 'CITY ST ZIP' tail, walk that tail off the end
    so the last token is the street's own final token. Applied only when the text
    actually ends in a state+ZIP; never guesses otherwise."""
    s = street.strip().strip(",")
    if not re.search(r"\b[A-Za-z]{2}\.?[ ,]*\d{5}(?:-?\d{4})?\s*$", s):
        return s
    toks = s.split()
    if toks and re.fullmatch(r"\d{5}(?:-?\d{4})?|\d{9}", toks[-1].strip(",")):
        toks = toks[:-1]
    if toks and re.fullmatch(r"[A-Za-z]{2}\.?", toks[-1].strip(",")):
        toks = toks[:-1]
    dropped = 0
    while len(toks) > 2 and dropped < 3:
        t = toks[-1].strip(",.").upper()
        if not t or any(ch.isdigit() for ch in t):
            break
        if t in SUFFIX_ABBR or t in SUFFIX_WORD or t in UNIT_TOK or t in DIR_TOK:
            break
        toks = toks[:-1]
        dropped += 1
    return " ".join(toks).strip().strip(",")


def tag_classes(street, raw, first_field=""):
    """Overlapping heuristic tags used ONLY for enrichment selection and reporting.
    They carry no label authority."""
    tags = set()
    core = street_core(street)
    up = core.upper()
    toks = [t.strip(".,") for t in re.findall(r"[A-Za-z0-9#/&'.\-]+", up) if t.strip(".,")]
    is_box = bool(BOX_RE.search(up))
    if is_box:
        tags.add("box")
    # tokens making up the street body: drop a trailing unit designator run
    body = list(toks)
    for i, t in enumerate(body):
        if t in UNIT_TOK or t.startswith("#"):
            body = body[:i]
            break
    while body and (body[-1] in DIR_TOK or body[-1] in DIR_WORD or body[-1].isdigit()
                    or re.fullmatch(r"\d+(ST|ND|RD|TH)", body[-1])):
        body = body[:-1]
    last = body[-1] if body else ""
    if last in SUFFIX_ABBR or last in SUFFIX_WORD:
        tags.add("suffix_present")
    elif not is_box and toks and re.fullmatch(r"\d+[A-Za-z]?", toks[0]) and len(body) >= 2:
        tags.add("suffix_omitted")
    if last in SUFFIX_WORD or any(t in DIR_WORD for t in toks):
        tags.add("spelled_out")
    if RECIP_RE.search(raw.upper()):
        tags.add("recipient")
    else:
        ff = first_field.strip()
        if ff and not re.search(r"\d", ff) and len(ff.split()) >= 2:
            tags.add("recipient")   # stored mailing-label name line before the street
    if any(t in UNIT_TOK for t in toks) or "#" in up or re.search(r"\b\d+\s*-\s*[A-Z]\b", up):
        tags.add("unit")
    if INVERTED_UNIT_RE.search(up):
        tags.add("unit_inverted")
        tags.add("unit")
    return sorted(tags)


# ---------------------------------------------------------------------------
# usaddress round-trip
# ---------------------------------------------------------------------------

try:
    import usaddress
except ImportError:  # pragma: no cover
    usaddress = None


def tokenizes(raw):
    if usaddress is None:
        raise SystemExit("usaddress is required (pip install usaddress)")
    try:
        toks = usaddress.tokenize(raw)
    except Exception:  # noqa: BLE001
        return False
    if not toks:
        return False
    return norm_identity(" ".join(toks)) == norm_identity(raw)


# ---------------------------------------------------------------------------
# Exclusion sets
# ---------------------------------------------------------------------------


def load_exclusion_sets():
    out = {}
    for name, path in EXCLUSION_FILES.items():
        if not path.exists():
            print(f"FATAL: exclusion file missing: {path}", file=sys.stderr)
            raise SystemExit(2)
        s = set()
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                raw = rec.get("raw")
                if raw is None and rec.get("tokens"):
                    raw = " ".join(rec["tokens"])
                if raw:
                    s.add(norm_identity(raw))
        out[name] = s
    return out


# ---------------------------------------------------------------------------
# Fetch
# ---------------------------------------------------------------------------


def out_fields(cfg):
    fs = list(cfg["addr_fields"])
    for key in ("city", "st", "zip"):
        if cfg.get(key):
            fs.append(cfg[key])
    return list(dict.fromkeys(fs))


def fetch_rows(cfg, rng, want, log):
    where = cfg.get("where", "1=1")
    d = arcgis_query(cfg["endpoint"], {"where": where, "returnCountOnly": "true"})
    n = d.get("count", 0)
    chunk = max(20, want // CHUNKS + 5)
    if n <= chunk:
        offsets = [0]
    else:
        offsets = sorted(rng.sample(range(max(1, n - chunk)),
                                    min(CHUNKS, max(1, n // chunk))))
    log.append(f"arcgis n={n} offsets={offsets} chunk={chunk}")
    rows = []
    for off in offsets:
        d = arcgis_query(cfg["endpoint"], {
            "where": where, "outFields": ",".join(out_fields(cfg)),
            "returnGeometry": "false", "resultOffset": str(off),
            "resultRecordCount": str(chunk),
        })
        rows.extend(f["attributes"] for f in d.get("features", []))
        time.sleep(0.4)
    return rows, n


def identity_evidence(cfg, rows, limit=10):
    """Modal mailing city/state values -- the jurisdiction-identity check quoted in
    the manifest, plus the first composed lines as free-text evidence."""
    cities = Counter()
    for r in rows:
        got = False
        for key in ("city", "st"):
            if cfg.get(key):
                v = clean_part(r.get(cfg[key]))
                if v:
                    cities[v.upper()] += 1
                    got = True
        if not got:
            # No separate city/state column: read the tail off the composed line.
            _, raw, _f = build_parts(cfg, r)
            m = re.search(r"([A-Za-z][A-Za-z .'-]{2,25}),?\s+([A-Za-z]{2})\.?\s+\d{5}",
                          raw)
            if m:
                cities[f"{m.group(1).strip().upper()} {m.group(2).upper()}"] += 1
    lines = []
    for r in rows[:limit]:
        _, raw, _f = build_parts(cfg, r)
        if raw:
            lines.append(raw)
    return {"modal_city_state": cities.most_common(6), "sample_lines": lines}


def fetch_state(state, cfg, excl_sets, in_set, rng, want):
    log = []
    try:
        rows, total = fetch_rows(cfg, rng, want * 3, log)
    except Exception as e:  # noqa: BLE001
        return {"state": state, "status": "gap-unreachable", "note": str(e)[:300],
                "records": [], "fetch_log": log}
    evidence = identity_evidence(cfg, rows)
    rng.shuffle(rows)
    removed = {k: 0 for k in excl_sets}
    removed["within-gold2c"] = 0
    removed["tokenize-fail"] = 0
    removed["non-us"] = 0
    records = []
    for row in rows:
        street, raw, first = build_parts(cfg, row)
        if not raw or not plausible(street, raw):
            continue
        if NON_US_RE.search(raw):
            removed["non-us"] += 1
            continue
        nid = norm_identity(raw)
        hit = None
        for name, s in excl_sets.items():
            if nid in s:
                hit = name
                break
        if hit is None and nid in in_set:
            hit = "within-gold2c"
        if hit:
            removed[hit] += 1
            continue
        if not tokenizes(raw):
            removed["tokenize-fail"] += 1
            continue
        in_set.add(nid)
        records.append({
            "raw": raw, "state": state, "source": cfg["endpoint"],
            "dataset": cfg["dataset"], "fetched": FETCH_DATE,
            "_classes": tag_classes(street, raw, first),
        })
        if len(records) >= want:
            break
    status = "fetched" if len(records) >= 30 else ("thin" if records else "gap-unreachable")
    return {"state": state, "status": status, "note": f"dataset rows={total}",
            "rows_pulled": len(rows), "dedupe_removed": removed, "fetch_log": log,
            "evidence": evidence, "dataset": cfg["dataset"],
            "publisher": cfg.get("publisher", ""), "endpoint": cfg["endpoint"],
            "lineage_flag": cfg.get("lineage_flag", ""), "records": records}


def ckpt_path(state):
    return CKPT_DIR / f"{state}.json"


def save_ckpt(state, payload):
    CKPT_DIR.mkdir(parents=True, exist_ok=True)
    with open(ckpt_path(state), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)


# ---------------------------------------------------------------------------
# Enrichment selection + assembly
# ---------------------------------------------------------------------------

# Deliberate over-sampling targets (dev surface only). These are aims, not quotas:
# the selector fills scarce classes first, then tops up with the rest.
CLASS_TARGETS = {
    "suffix_omitted": 120,
    "recipient": 110,
    "box": 100,
    "spelled_out": 110,
    "unit": 110,
    "unit_inverted": 25,
    "suffix_present": 300,
}


def assemble(target, per_state_cap):
    states = {}
    for p in sorted(CKPT_DIR.glob("*.json")):
        with open(p, encoding="utf-8") as f:
            states[p.stem] = json.load(f)
    pool = []
    for st, d in states.items():
        if not d.get("records"):
            continue
        for rec in d["records"]:
            pool.append(rec)
    rng = random.Random(SEED + 7)
    rng.shuffle(pool)

    chosen, chosen_ids = [], set()
    per_state = Counter()
    have = Counter()

    def take(rec):
        nid = norm_identity(rec["raw"])
        if nid in chosen_ids or per_state[rec["state"]] >= per_state_cap:
            return False
        chosen_ids.add(nid)
        per_state[rec["state"]] += 1
        chosen.append(rec)
        for c in rec["_classes"]:
            have[c] += 1
        return True

    def round_robin(cands, stop):
        """Draw across states one at a time so no single source dominates a class."""
        buckets = {}
        for r in cands:
            buckets.setdefault(r["state"], []).append(r)
        for b in buckets.values():
            rng.shuffle(b)
        while buckets and not stop():
            for st in sorted(buckets, key=lambda s: (per_state[s], s)):
                if stop():
                    break
                b = buckets[st]
                while b:
                    rec = b.pop()
                    if norm_identity(rec["raw"]) in chosen_ids:
                        continue
                    take(rec)
                    break
            buckets = {s: b for s, b in buckets.items() if b}

    # Pass 1: scarce classes first (rarest target first), round-robin across states.
    for cls in sorted(CLASS_TARGETS, key=lambda c: CLASS_TARGETS[c]):
        round_robin([r for r in pool if cls in r["_classes"]],
                    lambda c=cls: have[c] >= CLASS_TARGETS[c] or len(chosen) >= target)
    # Pass 2: top up to target, still round-robin across states.
    if len(chosen) < target:
        round_robin([r for r in pool if norm_identity(r["raw"]) not in chosen_ids],
                    lambda: len(chosen) >= target)

    chosen.sort(key=lambda r: (r["state"], r["raw"]))
    GOLD2C_DIR.mkdir(parents=True, exist_ok=True)
    with open(CANDIDATES_OUT, "w", encoding="utf-8") as f:
        for rec in chosen:
            out = {k: v for k, v in rec.items() if not k.startswith("_")}
            f.write(json.dumps(out, ensure_ascii=False) + "\n")

    write_manifest(states, chosen, per_state, have, target, per_state_cap)
    print(f"Wrote {len(chosen)} records from {len(per_state)} sources -> {CANDIDATES_OUT}")
    print("class mix:", dict(sorted(have.items())))
    return chosen


def write_manifest(states, chosen, per_state, have, target, per_state_cap):
    tot_rem = Counter()
    L = []
    L.append("# Gold-2c Fetch Manifest (DEV SURFACE - never a claim surface)\n")
    L.append(f"Generated by `benchmark/fetch_gold2c.py --assemble` on {FETCH_DATE}. "
             f"Seed {SEED}. Target {target} records, per-source cap {per_state_cap}.\n")
    L.append("Status: gold-2c is the dev tier pre-registered in `eval/gold2/PROTOCOL2.md` "
             "(2026-08-17). It may be iterated against freely and may never be cited in a "
             "public claim. Enrichment (deliberate over-sampling of the classes that decided "
             "gold-2b) is legitimate here for that reason and only that reason.\n")
    L.append("`state` is the SOURCE jurisdiction (whose roll the record came from); owner "
             "mailing addresses may point anywhere in the US and out-of-state mail is kept. "
             "Rows are SELECTED, never synthesized or edited.\n")
    L.append("Dedupe by normalized identity (uppercase alphanumeric join) against gold-1, "
             "gold-2, gold-2b, clean, training/corpus/realtext.jsonl, "
             "training/corpus/realtext2.jsonl, eval/realtext_dev.jsonl and "
             "eval/realtext_hard_dev.jsonl, plus within gold-2c. Every kept row round-trips "
             "`usaddress.tokenize` (tokens rejoin to the same normalized identity).\n")

    L.append("## Per-source outcomes\n")
    L.append("| State | Outcome | Dataset | Publisher | Endpoint | Rows pulled | Kept (pool) | In set | Dedupe removed (by list) |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for st in sorted(states):
        d = states[st]
        rem = d.get("dedupe_removed", {})
        for k, v in rem.items():
            tot_rem[k] += v
        rem_s = ", ".join(f"{k}:{v}" for k, v in rem.items() if v) or "0"
        L.append(f"| {st} | {d['status']} | {d.get('dataset','')} | {d.get('publisher','')} | "
                 f"`{d.get('endpoint','')}` | {d.get('rows_pulled','')} | "
                 f"{len(d.get('records', []))} | {per_state.get(st, 0)} | {rem_s} |")
    L.append("")
    L.append("**Dedupe removals, totalled per exclusion list:** " +
             ", ".join(f"{k}={v}" for k, v in sorted(tot_rem.items())) + "\n")

    L.append("## Per-source detail (window, identity check, free-text evidence)\n")
    for st in sorted(states):
        d = states[st]
        L.append(f"### {st} - {d.get('dataset','')}\n")
        L.append(f"- Publisher: {d.get('publisher','')}")
        L.append(f"- Endpoint: `{d.get('endpoint','')}`")
        L.append(f"- Fetched: {FETCH_DATE}; {d.get('note','')}; rows pulled "
                 f"{d.get('rows_pulled','?')}; kept in pool {len(d.get('records', []))}; "
                 f"in set {per_state.get(st, 0)}")
        for ln in d.get("fetch_log", []):
            L.append(f"- window: {ln}")
        ev = d.get("evidence", {})
        if ev.get("modal_city_state"):
            L.append("- jurisdiction identity check (modal mailing city/state values): " +
                     "; ".join(f"{c} x{n}" for c, n in ev["modal_city_state"]))
        if d.get("lineage_flag"):
            L.append(f"- **JUDGMENT CALL / lineage flag:** {d['lineage_flag']}")
        rem = d.get("dedupe_removed", {})
        L.append("- dedupe removed: " + (", ".join(f"{k}={v}" for k, v in rem.items()) or "n/a"))
        if ev.get("sample_lines"):
            L.append("- composed-text spot-check (free-text eligibility evidence, "
                     "verbatim first lines of the pull):")
            for ln in ev["sample_lines"][:8]:
                L.append(f"    - `{ln}`")
        L.append("")

    L.append("## Achieved class mix (enrichment)\n")
    pool_counts = Counter()
    pool_n = 0
    for d in states.values():
        for rec in d.get("records", []):
            pool_n += 1
            for c in rec.get("_classes", []):
                pool_counts[c] += 1
    L.append(f"Selection pool after dedupe: {pool_n} rows across {len(states)} sources. "
             "Rows were SELECTED from that pool; nothing was synthesized or edited, so a "
             "class can only reach the count the pool actually supplies.\n")
    L.append("| Class | Target | Achieved | Share of set | Available in pool |")
    L.append("|---|---|---|---|---|")
    n = max(1, len(chosen))
    for cls in sorted(CLASS_TARGETS, key=lambda c: -CLASS_TARGETS[c]):
        short = "" if have.get(cls, 0) >= CLASS_TARGETS[cls] else \
            "  (supply-limited)" if pool_counts.get(cls, 0) <= CLASS_TARGETS[cls] else ""
        L.append(f"| {cls} | {CLASS_TARGETS[cls]} | {have.get(cls,0)}{short} | "
                 f"{have.get(cls,0)/n:.0%} | {pool_counts.get(cls,0)} |")
    L.append("")
    L.append("Classes are overlapping tags (a record can be both `recipient` and `box`), so "
             "shares do not sum to 100%. Tagging is heuristic and used only for selection "
             "and reporting; it carries no label authority.\n")
    L.append(f"**Totals: {len(chosen)} records from {len(per_state)} sources across "
             f"{len(per_state)} states.** Per-state counts: " +
             ", ".join(f"{s}={c}" for s, c in sorted(per_state.items())) + "\n")
    with open(MANIFEST_OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print(f"Manifest -> {MANIFEST_OUT}")


# ---------------------------------------------------------------------------


def preview(state):
    cfg = CONFIG[state]
    rng = random.Random(SEED)
    log = []
    rows, n = fetch_rows(cfg, rng, 40, log)
    EVID_DIR.mkdir(parents=True, exist_ok=True)
    out = [f"[{state}] {cfg['dataset']}", f"endpoint: {cfg['endpoint']}",
           f"rows in dataset: {n}", *log, ""]
    for r in rows[:25]:
        street, raw, first = build_parts(cfg, r)
        out.append(f"  {raw}    <<classes: {','.join(tag_classes(street, raw, first))}>>")
    ev = identity_evidence(cfg, rows)
    out.append("")
    out.append("modal city/state: " + str(ev["modal_city_state"]))
    txt = "\n".join(out)
    (EVID_DIR / f"{state}.txt").write_text(txt, encoding="utf-8")
    print(txt)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--preview", metavar="STATE")
    ap.add_argument("--fetch", metavar="STATE")
    ap.add_argument("--fetch-all", action="store_true")
    ap.add_argument("--assemble", action="store_true")
    ap.add_argument("--target", type=int, default=TARGET_TOTAL)
    ap.add_argument("--cap", type=int, default=PER_STATE_CAP)
    ap.add_argument("--want", type=int, default=PER_STATE_POOL)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if args.list:
        assert_disjoint()
        for s, c in sorted(CONFIG.items()):
            flag = "  [FLAG]" if c.get("lineage_flag") else ""
            print(f"{s}: {c['dataset']}{flag}")
        return
    if args.check:
        assert_disjoint()
        return
    if args.preview:
        assert_disjoint(verbose=False)
        preview(args.preview.upper())
        return

    targets = []
    if args.fetch:
        targets = [args.fetch.upper()]
    elif args.fetch_all:
        targets = sorted(CONFIG)

    if targets:
        assert_disjoint()
        excl = load_exclusion_sets()
        for name, s in excl.items():
            print(f"exclusion [{name}]: {len(s)} identities")
        in_set = set()
        for p in CKPT_DIR.glob("*.json"):
            with open(p, encoding="utf-8") as f:
                for rec in json.load(f).get("records", []):
                    in_set.add(norm_identity(rec["raw"]))
        rng = random.Random(SEED)
        for s in targets:
            if ckpt_path(s).exists() and not args.force:
                print(f"[{s}] checkpoint exists, skipping (use --force to refetch)")
                continue
            print(f"[{s}] fetching ...")
            res = fetch_state(s, CONFIG[s], excl, in_set, rng, args.want)
            save_ckpt(s, res)
            rem = ", ".join(f"{k}={v}" for k, v in res.get("dedupe_removed", {}).items() if v)
            print(f"[{s}] {res['status']}: {len(res['records'])} records "
                  f"({res.get('note','')}) dedupe[{rem}]")

    if args.assemble:
        assemble(args.target, args.cap)

    if not (args.list or args.check or args.preview or targets or args.assemble):
        ap.print_help()


if __name__ == "__main__":
    main()
