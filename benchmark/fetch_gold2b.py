#!/usr/bin/env python3
"""Gold-2b sampler: fetch ~70+ true free-text owner-mailing address records per
jurisdiction from sources DISJOINT (dataset-level) from gold-2 and training.

Per eval/gold2/PROTOCOL2.md (gold-2b pre-registration + correction, 2026-08-16)
and eval/gold2/GOLD2B_SOURCES.md (amended disjointness rules).

Rules enforced here:
- FREE TEXT ONLY: the address line must be a single free-text field as the
  assessor wrote it. Component-assembled sources are ineligible.
- Dataset-level disjointness: no dataset fetched for gold-2 (FETCH_MANIFEST.md)
  and no dataset consumed by training (Cook IL, Allegheny PA, the 30 realtext
  datasets) may be configured here. Exception, documented in GOLD2B_SOURCES.md
  strategy #1 and flagged for human review in SOURCE_MAP_2B.md: the WI/WV/MN
  single-blob-tail statewide aggregates, which training could NOT use.
- Statewide/multi-county aggregates need a composed-text spot-check BEFORE
  sampling (--spotcheck STATE); evidence is written to the cache and quoted in
  FETCH_MANIFEST_2B.md. spotcheck_passed flips only after human inspection.
- Owner mailing addresses pointing out of state are KEPT ("state" = SOURCE
  jurisdiction). PO Box / RR / HC kept at natural frequency.
- Dedupe by normalized identity (uppercase alphanumeric collapse) against:
  gold-1 (eval/gold/candidates.jsonl), gold-2 (eval/gold2/candidates.jsonl),
  clean (eval/clean/clean.jsonl), realtext training corpus
  (training/corpus/realtext.jsonl, identity from token join), and the dev
  holdout (eval/realtext_dev.jsonl) — plus within gold-2b itself. Removal
  counts are tracked PER exclusion source.

Checkpoints: C:/cargo-target/us-address-parser/gold2b_cache/checkpoints/<STATE>.json
(outside OneDrive; delete a file to refetch that state).

Usage:
  python benchmark/fetch_gold2b.py --list
  python benchmark/fetch_gold2b.py --spotcheck WI
  python benchmark/fetch_gold2b.py --fetch WI [--want N]
  python benchmark/fetch_gold2b.py --fetch-all
  python benchmark/fetch_gold2b.py --assemble [--trim N]
"""

import argparse
import csv
import datetime as dt
import io
import json
import random
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GOLD2B_DIR = ROOT / "eval" / "gold2b"
CACHE = Path("C:/cargo-target/us-address-parser/gold2b_cache")
CKPT_DIR = CACHE / "checkpoints"
SPOT_DIR = CACHE / "spotchecks"
CANDIDATES_OUT = GOLD2B_DIR / "candidates.jsonl"
MANIFEST_OUT = GOLD2B_DIR / "FETCH_MANIFEST_2B.md"

EXCLUSION_FILES = {
    "gold-1": ROOT / "eval" / "gold" / "candidates.jsonl",
    "gold-2": ROOT / "eval" / "gold2" / "candidates.jsonl",
    "clean": ROOT / "eval" / "clean" / "clean.jsonl",
    "realtext-train": ROOT / "training" / "corpus" / "realtext.jsonl",
    "realtext-dev": ROOT / "eval" / "realtext_dev.jsonl",
}

TARGET_PER_STATE = 85          # headroom above the ~65-70 even-trim target
CHUNKS = 5
SEED = 20260819                # fresh seed, distinct from gold-2's 20260815
TIMEOUT = 60
UA = "fastaddress-gold2b-sampler/1.0 (research eval set; contact: repo maintainer)"
SIZE_FLOOR = 2900

FETCH_DATE = dt.date.today().isoformat()

# ---------------------------------------------------------------------------
# Per-state source config. Every entry names a dataset that is ABSENT from
# eval/gold2/FETCH_MANIFEST.md and from training/REALTEXT_MANIFEST.json
# per_source (checked at config time; rationale per state in SOURCE_MAP_2B.md),
# except WI/WV/MN (documented exception, flagged for review).
# ---------------------------------------------------------------------------
CONFIG = {
    # --- Primary leads: single-blob-tail statewide aggregates (GOLD2B_SOURCES #1)
    "WI": {
        "type": "arcgis",
        "endpoint": "https://services3.arcgis.com/n6uYoouQZW75n5WI/arcgis/rest/services/Wisconsin_Statewide_Parcels_DB/FeatureServer/0",
        "dataset": "Wisconsin Statewide Parcels V12 (PSTLADRESS owner full mailing)",
        "source": "https://services3.arcgis.com/n6uYoouQZW75n5WI/arcgis/rest/services/Wisconsin_Statewide_Parcels_DB/FeatureServer/0",
        "addr_fields": ["PSTLADRESS"], "city": None, "st": None, "zip": None,
        "where": "PSTLADRESS IS NOT NULL",
        "aggregate": True, "county_field": "CONAME",
        # Spot-check 2026-08-16 (VERNON, SAUK, WAUPACA; 75 lines): per-county
        # convention differences (comma vs no-comma), WI grid addresses
        # (E10168/S3708/N8343), PO BOX, STE/APT embedded, ", ," double-comma
        # quirk, -0000 zips. Pass-through free text. PASS
        # (gold2b_cache/spotchecks/WI.txt).
        "spotcheck_passed": True,
    },
    "WV": {
        "type": "arcgis",
        "endpoint": "https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/WV_Parcels/MapServer/0",
        "dataset": "WV Statewide Parcels (WVU GIS Tech Center, IAS owner mailing)",
        "source": "https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/WV_Parcels/MapServer/0",
        "addr_fields": ["FullOwnerAddress"], "city": None, "st": None, "zip": None,
        "where": "FullOwnerAddress IS NOT NULL",
        "aggregate": True, "county_field": "COUNTY",
        # Spot-check 2026-08-16 (county codes incl. 28, 35; 75 lines):
        # ROAD/RD side-by-side, "BULLTAIL"/"BULL TAIL" spacing inconsistency,
        # embedded owner-name line ("MOORE JAMES & KAREN, 322 WEBB FARM RD"),
        # truncated "159 14TH STREET," artifact, PO BOX 13%. Pass-through. PASS
        # (gold2b_cache/spotchecks/WV.txt).
        "spotcheck_passed": True,
    },
    "MN": {
        "type": "arcgis",
        "endpoint": "https://enterprise.gisdata.mn.gov/aghost/rest/services/us_mn_state_mngeo/plan_parcels_open/FeatureServer/1",
        "dataset": "MN Parcels, Compiled from Opt-In Open Data Counties",
        "source": "https://enterprise.gisdata.mn.gov/aghost/rest/services/us_mn_state_mngeo/plan_parcels_open/FeatureServer/1",
        "addr_fields": ["own_add_l1", "own_add_l2", "own_add_l3", "own_add_l4"],
        "city": None, "st": None, "zip": None,
        "where": "own_add_l1 IS NOT NULL AND own_add_l3 IS NOT NULL",
        "aggregate": True, "county_field": "co_name",
        # Spot-check 2026-08-16 (incl. St. Louis, Wilkin; 75 lines): 100%
        # mixed-case, C/O + Attn: + trustee recipient lines concatenated,
        # "Po Box" inside line, corporate tax-dept repeats at natural
        # frequency. Pass-through free text. PASS
        # (gold2b_cache/spotchecks/MN.txt).
        "spotcheck_passed": True,
    },
    # --- Second-publisher county/city portals (GOLD2B_SOURCES #2/#3) ---
    "AK": {
        "type": "arcgis",
        "endpoint": "https://services.arcgis.com/ba4DH9pIcqkXJVfl/arcgis/rest/services/Redacted_Parcels_view/FeatureServer/0",
        "dataset": "Kenai Peninsula Borough AK Parcels (KPB, redacted-names view)",
        "source": "https://services.arcgis.com/ba4DH9pIcqkXJVfl/arcgis/rest/services/Redacted_Parcels_view/FeatureServer/0",
        "addr_fields": ["MAILING_ADDRESS"], "city": "MAILING_CITY",
        "st": "MAILING_STATE", "zip": "MAILING_ZIP",
        "where": "MAILING_ADDRESS IS NOT NULL AND MAILING_ADDRESS <> ''",
    },
    "AR": {
        # City of Hope GIS "Parcel Ownership (From Assessor)"; sample cities
        # Murfreesboro/Delight/Hot Springs => Pike/Hempstead-area assessor roll.
        # AR was a gold-2 gap (statewide CAMP is situs-components-only).
        "type": "arcgis",
        "endpoint": "https://services5.arcgis.com/RVMSajYQji1bjmZ4/arcgis/rest/services/Parcel_Ownership/FeatureServer/0",
        "dataset": "Hope AR area Parcel Ownership from assessor (hopegis)",
        "source": "https://services5.arcgis.com/RVMSajYQji1bjmZ4/arcgis/rest/services/Parcel_Ownership/FeatureServer/0",
        "addr_fields": ["MailingAd1", "MailingAd2"], "city": "MailingCty",
        "st": "MailingSt", "zip": "MailingZip",
        "where": "MailingAd1 <> ''",
    },
    "CO": {
        "type": "arcgis",
        "endpoint": "https://maps1.larimer.org/arcgis/rest/services/MapServices/Parcels/MapServer/3",
        "dataset": "Larimer County CO Tax Parcels (county GIS)",
        "source": "https://maps1.larimer.org/arcgis/rest/services/MapServices/Parcels/MapServer/3",
        "addr_fields": ["MAILINGADDRESS"], "city": "MAILINGCITY",
        "st": "MAILINGSTATE", "zip": "MAILINGZIPCODE",
        "where": "MAILINGADDRESS IS NOT NULL",
    },
    "DE": {
        # Kent County DE official parcels. DE was a gold-2 gap (NCC endpoint
        # rejected queries). Free-text tells: "HICKMAN RD" vs "HICKMAN ROAD"
        # side by side in adjacent rows.
        "type": "arcgis",
        "endpoint": "https://gis.kentcountyde.gov/server/rest/services/Parcels/Parcels/FeatureServer/0",
        "dataset": "Kent County DE Parcels (county GIS)",
        "source": "https://gis.kentcountyde.gov/server/rest/services/Parcels/Parcels/FeatureServer/0",
        "addr_fields": ["MAILINGADDRESS", "MAILINGADDRESS2"], "city": "OWNERCITY",
        "st": "OWNERSTATE", "zip": "OWNERZIP",
        "where": "MAILINGADDRESS IS NOT NULL AND MAILINGADDRESS <> ''",
    },
    "FL": {
        # Hernando County Property Appraiser basemap parcels. MAIL_ADDR1..4 are
        # the label lines as stored (tail line inside ADDR2+); separate
        # MAIL_CITY etc. NOT joined to avoid duplicating the tail.
        "type": "arcgis",
        "endpoint": "https://services2.arcgis.com/x5zvhhxfUuRDntRe/arcgis/rest/services/Basemap_PublicMapGallery/FeatureServer/18",
        "dataset": "Hernando County FL Property Appraiser Parcels (Basemap)",
        "source": "https://services2.arcgis.com/x5zvhhxfUuRDntRe/arcgis/rest/services/Basemap_PublicMapGallery/FeatureServer/18",
        "addr_fields": ["MAIL_ADDR1", "MAIL_ADDR2", "MAIL_ADDR3", "MAIL_ADDR4"],
        "city": None, "st": None, "zip": None,
        "where": "MAIL_ADDR1 <> '' AND MAIL_ADDR2 <> ''",
    },
    "GA": {
        "type": "arcgis",
        "endpoint": "https://gis.atlantaga.gov/dpcd/rest/services/AdministrativeArea/TaxParcel/MapServer/0",
        "dataset": "City of Atlanta GA Tax Parcels 2025 (DCP)",
        "source": "https://gis.atlantaga.gov/dpcd/rest/services/AdministrativeArea/TaxParcel/MapServer/0",
        "addr_fields": ["PSTLADDRESS", "PSTLADDRESS2"], "city": "PSTLCITY",
        "st": "PSTLSTATE", "zip": "PSTLZIP5",
        "where": "PSTLADDRESS IS NOT NULL",
    },
    "HI": {
        # Maui County certified parcels (county GIS). HI was a gold-2 gap.
        "type": "arcgis",
        "endpoint": "https://services3.arcgis.com/fsrDo0QMPlK9CkZD/arcgis/rest/services/MC_Parcels_2020_gdb/FeatureServer/2",
        "dataset": "Maui County HI Certified Parcels 2020 (county GIS)",
        "source": "https://services3.arcgis.com/fsrDo0QMPlK9CkZD/arcgis/rest/services/MC_Parcels_2020_gdb/FeatureServer/2",
        # MailAddr2 IS the tail line ("HANA HI 96713"); MailCity/State/Zip are
        # parsed duplicates of it - joining both duplicated the tail (caught in
        # sample review), so the separate fields are NOT used.
        "addr_fields": ["MailCareOf", "MailAddr", "MailAddr2"],
        "city": None, "st": None, "zip": None,
        "where": "MailAddr <> '' AND MailAddr2 <> ''",
    },
    "IA": {
        "type": "arcgis",
        "endpoint": "https://services.arcgis.com/ovln19YRWV44nBqV/arcgis/rest/services/Cadastral/FeatureServer/3",
        "dataset": "Scott County IA Cadastral Parcels (county GIS)",
        "source": "https://services.arcgis.com/ovln19YRWV44nBqV/arcgis/rest/services/Cadastral/FeatureServer/3",
        # MailAddr2/3 carry the tail line ("LECLAIRE, IA 52753"); MailZip is a
        # parsed duplicate and is NOT used (caught in sample review).
        "addr_fields": ["MailAddr1", "MailAddr2", "MailAddr3"],
        "city": None, "st": None, "zip": None,
        "where": "MailAddr1 IS NOT NULL AND MailAddr1 <> '' AND MailAddr3 IS NOT NULL",
    },
    "IL": {
        "type": "arcgis",
        "endpoint": "https://services3.arcgis.com/HESxeTbDliKKvec2/arcgis/rest/services/OpenData_ParcelPolygons/FeatureServer/0",
        "dataset": "Lake County IL Tax Parcels (county open data, taxpayer mailing)",
        "source": "https://services3.arcgis.com/HESxeTbDliKKvec2/arcgis/rest/services/OpenData_ParcelPolygons/FeatureServer/0",
        # Lines 2/3 carry the tail ("LAKE ZURICH IL 60047-1330"); the separate
        # city/state/zip fields are parsed duplicates and are NOT used
        # (caught in sample review).
        "addr_fields": ["taxpayer_addr_line_care_of", "taxpayer_addr_line_1",
                         "taxpayer_addr_line_2", "taxpayer_addr_line_3"],
        "city": None, "st": None, "zip": None,
        "where": "taxpayer_addr_line_1 IS NOT NULL AND taxpayer_addr_line_3 IS NOT NULL",
    },
    "LA": {
        # St. Tammany Parish assessor data via Slidell planning layers
        # (DesireLine consultant publication of parish assessor roll).
        "type": "arcgis",
        "endpoint": "https://services2.arcgis.com/LJwIycC0yIuqCBxq/arcgis/rest/services/Slidell_Future_Land_Use/FeatureServer/0",
        "dataset": "Slidell LA parcels w/ St. Tammany assessor owner mailing",
        "source": "https://services2.arcgis.com/LJwIycC0yIuqCBxq/arcgis/rest/services/Slidell_Future_Land_Use/FeatureServer/0",
        "addr_fields": ["CARE_OF", "MAIL_ADDRE"], "city": "MAIL_CITY",
        "st": "MAIL_STATE", "zip": "MAIL_ZIP",
        "where": "MAIL_ADDRE IS NOT NULL AND MAIL_ADDRE <> ''",
    },
    "MA": {
        "type": "arcgis",
        "endpoint": "https://gisportal.boston.gov/arcgis/rest/services/Assessing/PROPERTY_ASSESSMENT_PARCEL_JOIN_FY26/FeatureServer/0",
        "dataset": "Boston MA Property Assessment FY26 (Assessing Dept)",
        "source": "https://gisportal.boston.gov/arcgis/rest/services/Assessing/PROPERTY_ASSESSMENT_PARCEL_JOIN_FY26/FeatureServer/0",
        "addr_fields": ["MAIL_STREET_ADDRESS"], "city": "MAIL_CITY",
        "st": "MAIL_STATE", "zip": "MAIL_ZIP_CODE",
        "where": "MAIL_STREET_ADDRESS IS NOT NULL",
    },
    "MD": {
        "type": "arcgis",
        "endpoint": "https://services8.arcgis.com/cbDaIA5xFnHBUlC1/arcgis/rest/services/Gaithersburg_Parcels/FeatureServer/0",
        "dataset": "City of Gaithersburg MD Parcels (owner mailing)",
        "source": "https://services8.arcgis.com/cbDaIA5xFnHBUlC1/arcgis/rest/services/Gaithersburg_Parcels/FeatureServer/0",
        "addr_fields": ["owner_address_line_1", "owner_address_line_2"],
        "city": "owner_address_city", "st": "owner_address_state",
        "zip": "owner_address_zip_code",
        "where": "owner_address_line_1 IS NOT NULL",
    },
    "MO": {
        # Single free-text mail-to line incl. city/state/zip as written
        # ("803 S MAIN ST, ST CHARLES MO, 63301-3444").
        "type": "arcgis",
        "endpoint": "https://gis-dev.sccmo.org/scc_gis/rest/services/open_data/Tax_Information_o/FeatureServer/1",
        "dataset": "St. Charles County MO Tax Information (open data)",
        "source": "https://gis-dev.sccmo.org/scc_gis/rest/services/open_data/Tax_Information_o/FeatureServer/1",
        "addr_fields": ["MailingAddress"], "city": None, "st": None, "zip": None,
        "where": "MailingAddress IS NOT NULL",
    },
    "MT": {
        # Lake County monthly parcel extract (county-published). NOTE upstream
        # is MT DOR ORION, the same DB behind training's statewide Cadastral
        # Framework - different dataset/publisher (eligible per amended rule),
        # flagged in SOURCE_MAP_2B for review.
        "type": "arcgis",
        "endpoint": "https://services2.arcgis.com/qQ6tqy9VSUry3ySt/arcgis/rest/services/9_1_2020_Lake_Parcels/FeatureServer/0",
        "dataset": "Lake County MT Parcels (county monthly extract)",
        "source": "https://services2.arcgis.com/qQ6tqy9VSUry3ySt/arcgis/rest/services/9_1_2020_Lake_Parcels/FeatureServer/0",
        "addr_fields": ["CareOfTaxp", "OwnerAddre", "OwnerAdd_1", "OwnerAdd_2"],
        "city": "OwnerCity", "st": "OwnerState", "zip": "OwnerZipCo",
        "where": "OwnerAddre <> ''",
    },
    "NC": {
        "type": "arcgis",
        "endpoint": "https://gcgis.guilfordcountync.gov/arcgis/rest/services/GC_Cadastral_Current/GC_Parcels/FeatureServer/0",
        "dataset": "Guilford County NC Parcels (county GIS)",
        "source": "https://gcgis.guilfordcountync.gov/arcgis/rest/services/GC_Cadastral_Current/GC_Parcels/FeatureServer/0",
        "addr_fields": ["OWNER_MAIL_1", "OWNER_MAIL_2", "OWNER_MAIL_3"],
        "city": "OWNER_MAIL_CITY", "st": "OWNER_MAIL_STATE", "zip": "OWNER_MAIL_ZIP",
        "where": "OWNER_MAIL_1 IS NOT NULL",
    },
    "ND": {
        "type": "arcgis",
        "endpoint": "https://services2.arcgis.com/8r0lsT7QHelkANsD/arcgis/rest/services/Tax_Parcels_Burleigh_County_ND/FeatureServer/0",
        "dataset": "Burleigh County ND Tax Parcels (county GIS)",
        "source": "https://services2.arcgis.com/8r0lsT7QHelkANsD/arcgis/rest/services/Tax_Parcels_Burleigh_County_ND/FeatureServer/0",
        "addr_fields": ["Mail_Address_1", "Mail_Address_2", "Mail_Address_3"],
        "city": "Mail_City", "st": "Mail_State", "zip": "Mail_Zip",
        "where": "Mail_Address_1 IS NOT NULL",
    },
    "NE": {
        # Lancaster County parcels via Lower Platte South NRD view (the
        # GOLD2B_SOURCES "NE Lancaster" second-choice lead).
        "type": "arcgis",
        "endpoint": "https://services2.arcgis.com/iTf0MCf7KYGMrPY1/arcgis/rest/services/Parcels_in_LPSNRD_view/FeatureServer/0",
        "dataset": "Lancaster County NE Parcels (LPSNRD view)",
        "source": "https://services2.arcgis.com/iTf0MCf7KYGMrPY1/arcgis/rest/services/Parcels_in_LPSNRD_view/FeatureServer/0",
        "addr_fields": ["Attn_Contact", "MailAddr", "MailAddr2"],
        "city": "MailCity", "st": "MailState", "zip": "MailZip",
        "where": "MailAddr IS NOT NULL",
    },
    "NJ": {
        # Newark city parcel layer (city-published MOD-IV attributes). NOTE
        # underlying MOD-IV municipal tax list also feeds the statewide
        # composite used in training - different dataset/publisher (eligible
        # per amended rule), flagged in SOURCE_MAP_2B.
        "type": "arcgis",
        "endpoint": "https://services1.arcgis.com/WAUuvHqqP3le2PMh/arcgis/rest/services/Newark_Parcels_with_Ownership/FeatureServer/0",
        "dataset": "Newark NJ Parcels with Ownership (city GIS)",
        "source": "https://services1.arcgis.com/WAUuvHqqP3le2PMh/arcgis/rest/services/Newark_Parcels_with_Ownership/FeatureServer/0",
        # ZIPCODE is stored numeric (leading zero lost; zip+4 as a float,
        # e.g. 7107.1731). zip_fix undoes that storage artifact -> 07107-1731.
        "addr_fields": ["OWNERADD1", "OWNERADD2"], "city": None, "st": None,
        "zip": "ZIPCODE", "zip_fix": True,
        "where": "OWNERADD1 IS NOT NULL AND OWNERADD2 IS NOT NULL",
    },
    "NM": {
        # Dona Ana County assessor parcels via City of Las Cruces layer.
        "type": "arcgis",
        "endpoint": "https://services1.arcgis.com/ejcbAsQEUUGWEyzb/arcgis/rest/services/DAC_Parcel/FeatureServer/0",
        "dataset": "Dona Ana County NM Parcels (Las Cruces DAC_Parcel)",
        "source": "https://services1.arcgis.com/ejcbAsQEUUGWEyzb/arcgis/rest/services/DAC_Parcel/FeatureServer/0",
        "addr_fields": ["CAREOFNAME", "MAILADDR1", "MAILADDR2"],
        "city": "CITY", "st": "STATE", "zip": "ZIP",
        "where": "MAILADDR1 IS NOT NULL",
    },
    "NV": {
        # Washoe County assessor nightly open-data parcels (the GOLD2B_SOURCES
        # "NV Washoe" second-choice lead; county-published).
        "type": "arcgis",
        "endpoint": "https://services.arcgis.com/iCGWaR7ZHc5saRIl/arcgis/rest/services/Nightly_OpenData_Update/FeatureServer/1",
        "dataset": "Washoe County NV Parcels (assessor nightly open data)",
        "source": "https://services.arcgis.com/iCGWaR7ZHc5saRIl/arcgis/rest/services/Nightly_OpenData_Update/FeatureServer/1",
        "addr_fields": ["MAILING1", "MAILING2"], "city": "MAILCITY",
        "st": "MAILSTATE", "zip": "MAILZIP",
        "where": "MAILING1 IS NOT NULL",
    },
    "OH": {
        "type": "arcgis",
        "endpoint": "https://gis.franklincountyohio.gov/hosting/rest/services/ParcelFeatures/Parcel_Features/MapServer/0",
        "dataset": "Franklin County OH Parcels (Auditor, PSTL mailing fields)",
        "source": "https://gis.franklincountyohio.gov/hosting/rest/services/ParcelFeatures/Parcel_Features/MapServer/0",
        # PSTLADDRES already embeds the full tail; PSTLCITYSTZIP is a
        # duplicate and is NOT used (caught in sample review).
        "addr_fields": ["PSTLADDRES"], "city": None, "st": None, "zip": None,
        "where": "PSTLADDRES IS NOT NULL",
    },
    "OK": {
        # Oklahoma County assessor Tax Parcels Public (AGOL view; sample tax
        # districts e.g. "Luther #3" confirm Oklahoma County).
        "type": "arcgis",
        "endpoint": "https://services8.arcgis.com/euhkr1dAJeQBIjV0/arcgis/rest/services/TaxParcelsPublics_view/FeatureServer/0",
        "dataset": "Oklahoma County OK Tax Parcels Public (assessor)",
        "source": "https://services8.arcgis.com/euhkr1dAJeQBIjV0/arcgis/rest/services/TaxParcelsPublics_view/FeatureServer/0",
        "addr_fields": ["mailingaddress1"], "city": "city", "st": "state",
        "zip": "zipcode",
        "where": "mailingaddress1 IS NOT NULL",
    },
    "OR": {
        "type": "arcgis",
        "endpoint": "https://services3.arcgis.com/NbWCmkRTtvyr63CT/arcgis/rest/services/Taxlot__Public/FeatureServer/100",
        "dataset": "Lane County OR Taxlots (LCOG public, owner mail lines)",
        "source": "https://services3.arcgis.com/NbWCmkRTtvyr63CT/arcgis/rest/services/Taxlot__Public/FeatureServer/100",
        "addr_fields": ["mail_address_line_1", "mail_address_line_2",
                         "mail_address_line_3"],
        "city": "mail_address_city_name", "st": "mail_address_state_code",
        "zip": "mail_address_zip_code",
        "where": "mail_address_line_1 IS NOT NULL",
    },
    "PA": {
        "type": "arcgis",
        "endpoint": "https://arcweb1.ycpc.org/server/rest/services/OPEN_DATA/Parcels/FeatureServer/0",
        "dataset": "York County PA Parcels (YCPC open data, owner mail lines)",
        "source": "https://arcweb1.ycpc.org/server/rest/services/OPEN_DATA/Parcels/FeatureServer/0",
        "addr_fields": ["MAIL_ADDR1", "MAIL_ADDR2", "MAIL_ADDR3"],
        "city": None, "st": None, "zip": None,
        "where": "MAIL_ADDR1 IS NOT NULL",
    },
    "RI": {
        "type": "arcgis",
        "endpoint": "https://arcgisserver.cranstonri.org/arcgis/rest/services/Parcels/FeatureServer/54",
        "dataset": "City of Cranston RI Parcels (CAMA extract owner mailing)",
        "source": "https://arcgisserver.cranstonri.org/arcgis/rest/services/Parcels/FeatureServer/54",
        "addr_fields": ["CAMAExtract_OwnerAddress"], "city": "CAMAExtract_OwnerCity",
        "st": "CAMAExtract_OwnerState", "zip": "CAMAExtract_OwnerZip",
        "where": "CAMAExtract_OwnerAddress IS NOT NULL",
    },
    "SC": {
        # Kershaw County parcels (Fairfield/Kershaw/Richland map, layer 7 =
        # Kershaw_Parcels). taxMailing=line, taxMaili1=line2, taxMaili2=city,
        # taxMailSta=state, taxMaili3=zip.
        "type": "arcgis",
        "endpoint": "https://services9.arcgis.com/RvqSyw3diI7dTKo5/arcgis/rest/services/Fairfield_Kershaw_Richland_Map_WFL1/FeatureServer/7",
        "dataset": "Kershaw County SC Parcels (tax mailing fields)",
        "source": "https://services9.arcgis.com/RvqSyw3diI7dTKo5/arcgis/rest/services/Fairfield_Kershaw_Richland_Map_WFL1/FeatureServer/7",
        "addr_fields": ["taxMailing", "taxMaili1"], "city": "taxMaili2",
        "st": "taxMailSta", "zip": "taxMaili3",
        "where": "taxMailing IS NOT NULL",
    },
    "SD": {
        "type": "arcgis",
        "endpoint": "https://gis.siouxfalls.gov/arcgis/rest/services/Data/Property/MapServer/1",
        "dataset": "City of Sioux Falls SD Parcels (owner mailing)",
        "source": "https://gis.siouxfalls.gov/arcgis/rest/services/Data/Property/MapServer/1",
        "addr_fields": ["OWNADDRESS"], "city": "OWNCITY", "st": "OWNSTATE",
        "zip": "OWNZIP",
        "where": "OWNADDRESS IS NOT NULL",
    },
    "TX": {
        # Bexar CAD parcel attributes (AGOL copy "Bexar parcels all").
        # MAIL_LINE1=addressee/line1, MAIL_LINE2=street line; MAIL_ADDR is a
        # concatenation and is NOT used.
        "type": "arcgis",
        "endpoint": "https://services2.arcgis.com/82iS1Pc7dgs3LFZv/arcgis/rest/services/Bexar_parcels_all/FeatureServer/0",
        "dataset": "Bexar County TX Parcels (BCAD attributes, AGOL copy)",
        "source": "https://services2.arcgis.com/82iS1Pc7dgs3LFZv/arcgis/rest/services/Bexar_parcels_all/FeatureServer/0",
        "addr_fields": ["MAIL_LINE1", "MAIL_LINE2"], "city": "MAIL_CITY",
        "st": "MAIL_STAT", "zip": "MAIL_ZIP",
        "where": "MAIL_LINE2 IS NOT NULL",
    },
    "MI": {
        # Ottawa County official historical parcel assessment data (county
        # self-hosted; most recent annual layer probed).
        "type": "arcgis",
        "endpoint": "https://gis.miottawa.org/arcgis/rest/services/HostedServices/HistoricParcels/FeatureServer/10",
        "dataset": "Ottawa County MI Parcel Assessment Data (county GIS)",
        "source": "https://gis.miottawa.org/arcgis/rest/services/HostedServices/HistoricParcels/FeatureServer/10",
        "addr_fields": ["MAILADDRESS"], "city": "MAILCITY", "st": "MAILSTATE",
        "zip": "MAILZIP",
        "where": "MAILADDRESS IS NOT NULL AND MAILADDRESS <> ''",
    },
    "AL": {
        # Montgomery County AL parcel boundary layer (MailCity/PropertyCity
        # "MONTGOMERY", muni code 01; C/O lines in MailAddress1 confirm
        # free text). Published inside an ALEA web-map service; data is the
        # county assessor roll. Fixed-width padded values (build_raw strips).
        "type": "arcgis",
        "endpoint": "https://services7.arcgis.com/xNUwUjOJqYE54USz/arcgis/rest/services/Sex_Offender_Residential_Restrictions_WFL1/FeatureServer/3",
        "dataset": "Montgomery County AL Parcel Boundary (assessor roll copy)",
        "source": "https://services7.arcgis.com/xNUwUjOJqYE54USz/arcgis/rest/services/Sex_Offender_Residential_Restrictions_WFL1/FeatureServer/3",
        "addr_fields": ["MailAddress1", "MailAddress2"], "city": "MailCity",
        "st": "MailState", "zip": "MailZip",
        "where": "MailAddress1 IS NOT NULL",
    },
    "TN": {
        # Rutherford County TN (samples: Murfreesboro, La Vergne; n~123k).
        "type": "arcgis",
        "endpoint": "https://services5.arcgis.com/A5C0MR9xfkxVRwat/arcgis/rest/services/Parcel_Data/FeatureServer/1",
        "dataset": "Rutherford County TN Parcel Data (grantee mailing)",
        "source": "https://services5.arcgis.com/A5C0MR9xfkxVRwat/arcgis/rest/services/Parcel_Data/FeatureServer/1",
        "addr_fields": ["MailingAddress", "MailingAddress2"],
        "city": "MailingCity", "st": "MailingState", "zip": "MailingZipCode",
        "where": "MailingAddress IS NOT NULL",
    },
    "WA": {
        # Pierce County assessor taxpayer fields via City of Milton planning
        # layer (Milton + surrounding Pierce County area).
        "type": "arcgis",
        "endpoint": "https://services6.arcgis.com/RLW8Rymck77KYbSO/arcgis/rest/services/Planning_Public/FeatureServer/17",
        "dataset": "Pierce County WA Parcels via Milton Planning (taxpayer mailing)",
        "source": "https://services6.arcgis.com/RLW8Rymck77KYbSO/arcgis/rest/services/Planning_Public/FeatureServer/17",
        "addr_fields": ["taxpayer_address"], "city": "taxpayer_city",
        "st": "taxpayer_state", "zip": "taxpayer_zip",
        "where": "taxpayer_address IS NOT NULL",
    },
    "UT": {
        # Millcreek city parcels (Salt Lake County assessor attributes;
        # own_addr line + own_citystate + own_zip; own_apt_num included after
        # the line, same precedent as gold-2's York SC MailApt). UT was a
        # gold-2 gap.
        "type": "arcgis",
        "endpoint": "https://services9.arcgis.com/XRrSFvEwSsReIxuA/arcgis/rest/services/Millcreek_Parcels/FeatureServer/0",
        "dataset": "Millcreek UT Parcels (Salt Lake County assessor attributes)",
        "source": "https://services9.arcgis.com/XRrSFvEwSsReIxuA/arcgis/rest/services/Millcreek_Parcels/FeatureServer/0",
        "addr_fields": ["care_of", "own_addr", "own_apt_num"],
        "city": "own_citystate", "st": None, "zip": "own_zip",
        "where": "own_addr IS NOT NULL",
    },
    "MS": {
        # Harrison County MS assessor roll (County Parcels layer inside the
        # Gulfport-Biloxi International Airport public service; n~100k =
        # Harrison County). MS was a gold-2 gap. Free-text tells: "ROAD 429",
        # "LENNIS CUEVAS ROAD" vs RD, "(600.00 AC)" deed-acre quirks.
        "type": "arcgis",
        "endpoint": "https://services1.arcgis.com/XwK5zAS8O0b6s3Tp/arcgis/rest/services/Public_Data_Layers/FeatureServer/1",
        "dataset": "Harrison County MS Parcels (via Gulfport-Biloxi Airport GIS)",
        "source": "https://services1.arcgis.com/XwK5zAS8O0b6s3Tp/arcgis/rest/services/Public_Data_Layers/FeatureServer/1",
        "addr_fields": ["MAIL_1", "MAIL_2"], "city": "CITY", "st": "ST",
        "zip": "ZIP",
        "where": "MAIL_1 IS NOT NULL",
    },
    "VA": {
        # City of Newport News official parcels ("97 28TH ST, UNIT B" comma
        # style, "TRAIL"/"BLVD" variety, STE embedded => pass-through).
        "type": "arcgis",
        "endpoint": "https://maps.nnva.gov/gis/rest/services/Operational/Parcel/MapServer/0",
        "dataset": "City of Newport News VA Parcels (PSTL owner mailing)",
        "source": "https://maps.nnva.gov/gis/rest/services/Operational/Parcel/MapServer/0",
        "addr_fields": ["PSTLADDRESS1", "PSTLADDRESS2"], "city": "PSTLCITY",
        "st": "PSTLSTATE", "zip": "PSTLZIP5",
        "where": "PSTLADDRESS1 IS NOT NULL",
    },
    "AZ": {
        # Yavapai County assessor attributes via Town of Prescott Valley
        # parcels (Own_Addr stored line, STE embedded; zip9-no-hyphen quirks).
        "type": "arcgis",
        "endpoint": "https://services.arcgis.com/NxZdAmj8rBzdRpTr/arcgis/rest/services/PV_PARCELS/FeatureServer/1",
        "dataset": "Prescott Valley AZ Parcels (Yavapai assessor owner mailing)",
        "source": "https://services.arcgis.com/NxZdAmj8rBzdRpTr/arcgis/rest/services/PV_PARCELS/FeatureServer/1",
        "addr_fields": ["Own_Addr"], "city": "Own_City", "st": "Own_State",
        "zip": "Own_Zip",
        "where": "Own_Addr IS NOT NULL AND Own_Addr <> ''",
    },
    "IN": {
        # Vanderburgh County Assessor parcel data (county open-data portal
        # item; XSoft assessment system attributes).
        "type": "arcgis",
        "endpoint": "https://maps.evansvillegis.com/arcgis_server/rest/services/ASSESSOR/PARCEL_DATA/MapServer/0",
        "dataset": "Vanderburgh County IN Assessor Parcel Data",
        "source": "https://maps.evansvillegis.com/arcgis_server/rest/services/ASSESSOR/PARCEL_DATA/MapServer/0",
        "addr_fields": ["OWNERSTREET"], "city": "OWNERCITY", "st": "OWNERSTATE",
        "zip": "OWNERZIP",
        "where": "OWNERSTREET IS NOT NULL",
    },
    "WY": {
        # JUDGMENT CALL, flagged for review: WY was pre-registered as a hard
        # gap ("no bulk open source") - an availability finding, not a legal
        # bar (unlike CA/ID). Sheridan County WY parcels are now openly
        # queryable with owner mailing (name/address/city/state/zip) showing
        # free-text tells ("1156 S  SHERIDAN AVE" double space, C/O embedded
        # in name). Fetched so the option exists; Vin decides at review
        # whether including WY amends the pre-registered gap list.
        "type": "arcgis",
        "endpoint": "https://services5.arcgis.com/V4b98G4pSkzvUam9/arcgis/rest/services/Parcels/FeatureServer/0",
        "dataset": "Sheridan County WY Parcels (owner mailing)",
        "source": "https://services5.arcgis.com/V4b98G4pSkzvUam9/arcgis/rest/services/Parcels/FeatureServer/0",
        "addr_fields": ["address"], "city": "city", "st": "state", "zip": "zip",
        "where": "address IS NOT NULL AND address <> ''",
    },
    "NY": {
        # NYS GIS Program Office Tax Parcels (statewide aggregate; RPS
        # MAIL_ADDR line + separate PO_BOX field). DIFFERENT dataset from the
        # components-only data.ny.gov assessment roll (7vem-aaz7) recorded as
        # ineligible in gold-2's SOURCE_MAP, and from gold-2's Buffalo roll.
        # Aggregate => composed-text spot-check required before sampling.
        "type": "arcgis",
        "endpoint": "https://services6.arcgis.com/EbVsqZ18sv1kVJ3k/arcgis/rest/services/NYS_Tax_Parcels_Public/FeatureServer/1",
        "dataset": "NYS Tax Parcels Public (GIS Program Office, RPS owner mailing)",
        "source": "https://services6.arcgis.com/EbVsqZ18sv1kVJ3k/arcgis/rest/services/NYS_Tax_Parcels_Public/FeatureServer/1",
        "addr_fields": ["MAIL_ADDR", "PO_BOX"], "city": "MAIL_CITY",
        "st": "MAIL_STATE", "zip": "MAIL_ZIP",
        "where": "MAIL_ADDR IS NOT NULL",
        "aggregate": True, "county_field": "COUNTY_NAME",
        # Spot-check 2026-08-16 (Tompkins, Lewis + one more; 75 lines): highway
        # spelling variety within one county (State Hwy 58 / State Route 30 /
        # St Rte 26 / State Rte 812), "Old State Rd" vs "Old State Road"
        # adjacent, malformed zip9s (136199610), Youngs Mill/Mills drift,
        # 67% mixed-case. Pass-through RPS text, NOT composed. PASS
        # (gold2b_cache/spotchecks/NY.txt).
        "spotcheck_passed": True,
    },
}

# ---------------------------------------------------------------------------
# HTTP helpers (same machinery as benchmark/fetch_gold2.py)
# ---------------------------------------------------------------------------

def http_get(url, retries=2):
    """Explicit 60s timeout per request; at most 2 attempts, then the failure
    is documented in the state checkpoint (coordinator guardrail 2026-08-16)."""
    last = None
    for i in range(retries):
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


# ---------------------------------------------------------------------------
# Normalization / dedupe
# ---------------------------------------------------------------------------

def norm_identity(raw: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", raw.upper())


def load_exclusion_sets():
    """Returns {name: set-of-identities}. realtext-train uses token join when
    'raw' is absent (identity strips non-alphanumerics, so join is exact)."""
    out = {}
    for name, path in EXCLUSION_FILES.items():
        s = set()
        if not path.exists():
            print(f"FATAL: exclusion file missing: {path}", file=sys.stderr)
            sys.exit(2)
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


def clean_part(v):
    if v is None:
        return ""
    s = str(v).strip()
    if s.lower() in ("null", "none", "nan"):
        return ""
    return s


def build_raw(cfg, row):
    parts = []
    for f in cfg["addr_fields"]:
        parts.append(clean_part(row.get(f)))
    for key in ("citystzip",):
        if cfg.get(key):
            parts.append(clean_part(row.get(cfg[key])))
    for key in ("city", "st", "zip"):
        if cfg.get(key):
            v = clean_part(row.get(cfg[key]))
            if key == "zip" and v and cfg.get("zip_fix"):
                m = re.fullmatch(r"(\d{1,5})(?:\.(\d{1,4}))?", v)
                if m:
                    v = m.group(1).zfill(5)
                    if m.group(2):
                        v += "-" + m.group(2).ljust(4, "0")
            parts.append(v)
    parts = [p for p in parts if p]
    deduped = []
    for p in parts:
        if deduped and p.strip().upper() == deduped[-1].strip().upper():
            continue
        deduped.append(p)
    raw = " ".join(deduped)
    raw = re.sub(r"\s+", " ", raw).strip()
    return raw


def plausible(raw, cfg, row):
    line = ""
    for f in cfg["addr_fields"]:
        line = clean_part(row.get(f))
        if line:
            break
    if not line or len(line) < 3:
        return False
    if len(raw.split()) < 3:
        return False
    sp = cfg.get("skip_pattern")
    if sp and re.search(sp, raw):
        return False
    return True


# ---------------------------------------------------------------------------
# Portal fetchers
# ---------------------------------------------------------------------------

def soc_url(cfg, params):
    q = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    return f"https://{cfg['domain']}/resource/{cfg['dataset_id']}.json?{q}"


def fetch_socrata(cfg, rng, want, log):
    base_where = cfg.get("where")
    p = {"$select": "count(*) as n"}
    if base_where:
        p["$where"] = base_where
    n = int(get_json(soc_url(cfg, p))[0]["n"])
    rows = []
    chunk = max(10, want // CHUNKS + 2)
    offsets = sorted(rng.sample(range(max(1, n - chunk)), min(CHUNKS, max(1, n // chunk)))) if n > chunk else [0]
    log.append(f"socrata n={n} offsets={offsets} chunk={chunk}")
    for off in offsets:
        p = {"$limit": str(chunk), "$offset": str(off), "$order": ":id"}
        if base_where:
            p["$where"] = base_where
        rows.extend(get_json(soc_url(cfg, p)))
        time.sleep(0.4)
    return rows, n


def arcgis_query(endpoint, params):
    params = dict(params)
    params["f"] = "json"
    url = endpoint + "/query?" + urllib.parse.urlencode(params)
    d = get_json(url)
    if "error" in d:
        raise RuntimeError(f"ArcGIS error: {d['error']}")
    return d


def fetch_arcgis(cfg, rng, want, log, extra_where=None):
    where = cfg.get("where", "1=1")
    if extra_where:
        where = f"({where}) AND ({extra_where})"
    d = arcgis_query(cfg["endpoint"], {"where": where, "returnCountOnly": "true"})
    n = d.get("count", 0)
    out_fields = [f for f in cfg["addr_fields"]]
    for key in ("city", "st", "zip", "citystzip", "county_field"):
        if cfg.get(key):
            out_fields.append(cfg[key])
    rows = []
    chunk = max(10, want // CHUNKS + 2)
    if cfg.get("objectid_sampling"):
        window = chunk * 4
        oid = cfg.get("oid_field", "OBJECTID")
        for _ in range(CHUNKS):
            r = rng.randrange(1, max(2, n - window))
            log.append(f"oid-window [{r},{r + window})")
            d = arcgis_query(cfg["endpoint"], {
                "where": f"{oid} >= {r} AND {oid} < {r + window}",
                "outFields": ",".join(out_fields),
                "returnGeometry": "false", "resultRecordCount": str(chunk),
            })
            rows.extend(f["attributes"] for f in d.get("features", []))
            time.sleep(0.4)
        return rows, n
    if n <= chunk:
        offsets = [0]
    else:
        offsets = sorted(rng.sample(range(max(1, n - chunk)), min(CHUNKS, max(1, n // chunk))))
    log.append(f"arcgis n={n} offsets={offsets} chunk={chunk}"
               + (f" where+=({extra_where})" if extra_where else ""))
    for off in offsets:
        d = arcgis_query(cfg["endpoint"], {
            "where": where, "outFields": ",".join(out_fields),
            "returnGeometry": "false", "resultOffset": str(off),
            "resultRecordCount": str(chunk),
        })
        rows.extend(f["attributes"] for f in d.get("features", []))
        time.sleep(0.4)
    return rows, n


def fetch_carto(cfg, rng, want, log):
    where = cfg.get("where", "TRUE")
    def sql(q):
        return get_json(f"https://{cfg['domain']}/api/v2/sql?q=" + urllib.parse.quote(q))
    n = sql(f"SELECT count(*) AS n FROM {cfg['table']} WHERE {where}")["rows"][0]["n"]
    rows = []
    chunk = max(10, want // CHUNKS + 2)
    offsets = sorted(rng.sample(range(max(1, n - chunk)), min(CHUNKS, max(1, n // chunk)))) if n > chunk else [0]
    log.append(f"carto n={n} offsets={offsets} chunk={chunk}")
    cols = ",".join([*cfg["addr_fields"],
                     *[cfg[k] for k in ("city", "st", "zip") if cfg.get(k)]])
    for off in offsets:
        q = (f"SELECT {cols} FROM {cfg['table']} WHERE {where} "
             f"ORDER BY cartodb_id LIMIT {chunk} OFFSET {off}")
        rows.extend(sql(q)["rows"])
        time.sleep(0.4)
    return rows, n


def fetch_csv_url(cfg, rng, want, log):
    """Bulk CSV/TXT (optionally zipped), cached under gold2b_cache/bulk/."""
    url = cfg["csv_url"]
    bulk_dir = CACHE / "bulk"
    bulk_dir.mkdir(exist_ok=True)
    fname = re.sub(r"[^A-Za-z0-9._-]", "_", url.split("/")[-1] or "bulk.bin")
    local = bulk_dir / f"{cfg['_state']}_{fname}"
    if not local.exists():
        log.append(f"downloading bulk {url}")
        data = http_get(url)
        local.write_bytes(data)
    else:
        log.append(f"bulk cache hit {local.name}")
    data = local.read_bytes()
    if cfg.get("zip_member") is not None or url.lower().endswith(".zip"):
        import zipfile
        zf = zipfile.ZipFile(io.BytesIO(data))
        member = cfg.get("zip_member")
        if not member:
            names = [n for n in zf.namelist() if not n.endswith("/")]
            member = names[0]
        log.append(f"zip member: {member}")
        data = zf.read(member)
    text = data.decode(cfg.get("encoding", "utf-8"), "replace")
    reader = csv.DictReader(io.StringIO(text), delimiter=cfg.get("delimiter", ","))
    all_rows = list(reader)
    rng.shuffle(all_rows)
    log.append(f"csv rows={len(all_rows)}")
    return all_rows[: want * 6], len(all_rows)


# ---------------------------------------------------------------------------
# Aggregate sampling + spot-check
# ---------------------------------------------------------------------------

def agg_counties(cfg):
    d = arcgis_query(cfg["endpoint"], {
        "where": cfg.get("where", "1=1"),
        "outFields": cfg["county_field"], "returnDistinctValues": "true",
        "returnGeometry": "false",
    })
    vals = sorted({f["attributes"][cfg["county_field"]] for f in d.get("features", [])
                   if f["attributes"].get(cfg["county_field"])})
    return vals


def fetch_aggregate(cfg, rng, want, log):
    counties = agg_counties(cfg)
    avoid = set(cfg.get("avoid_counties", []))
    pool = [c for c in counties if c not in avoid] or counties
    n_counties = min(8, len(pool))
    picks = rng.sample(pool, n_counties)
    log.append(f"aggregate counties sampled: {picks}")
    per = want // n_counties + 2
    rows = []
    total = 0
    for c in picks:
        cw = f"{cfg['county_field']} = '{c}'"
        sub, n = fetch_arcgis(cfg, rng, per, log, extra_where=cw)
        rng.shuffle(sub)
        rows.extend(sub[:per])
        total += n
    return rows, total


def spotcheck(state, cfg, rng):
    """Composed-text spot-check: dump rows from 3 counties, compare heuristics,
    save evidence file under gold2b_cache/spotchecks/."""
    SPOT_DIR.mkdir(parents=True, exist_ok=True)
    counties = agg_counties(cfg)
    picks = rng.sample(counties, min(3, len(counties)))
    lines_out = [f"[{state}] spot-check {FETCH_DATE} counties: {picks}"]
    all_lines = []
    for c in picks:
        log = []
        sub, _ = fetch_arcgis(cfg, rng, 25, log, extra_where=f"{cfg['county_field']} = '{c}'")
        lines = [build_raw(cfg, r) for r in sub]
        lines = [l for l in lines if l][:25]
        all_lines.extend(lines)
        lines_out.append(f"\n--- {c} ({len(lines)} lines) ---")
        lines_out.extend("    " + l for l in lines)
    n = len(all_lines)
    if n:
        unit = sum(bool(re.search(r"\b(APT|UNIT|STE|SUITE|LOT|TRLR|FL|RM|BLDG)\b|#", l, re.I)) for l in all_lines)
        pob = sum(bool(re.search(r"\bP\.?\s?O\.?\s?BOX|\bBOX\s+\d|\bRR\s?\d|\bHC\s?\d", l, re.I)) for l in all_lines)
        punct = sum(bool(re.search(r"[.,#/&']", l)) for l in all_lines)
        mixed = sum(bool(re.search(r"[a-z]", l)) for l in all_lines)
        lines_out.append(
            f"\nHeuristics over {n} lines: units/#: {unit} ({unit/n:.0%}), "
            f"PO/RR/HC: {pob} ({pob/n:.0%}), punctuation: {punct} ({punct/n:.0%}), "
            f"mixed-case: {mixed} ({mixed/n:.0%})")
        lines_out.append("Perfect 'NUM STREET TYPE' uniformity with ~0% units/PO/quirks "
                         "across counties => SUSPECT-COMPOSED, exclude.")
    text = "\n".join(lines_out)
    (SPOT_DIR / f"{state}.txt").write_text(text, encoding="utf-8")
    print(text)
    print(f"\nEvidence saved: {SPOT_DIR / (state + '.txt')}")


# ---------------------------------------------------------------------------
# Per-state driver
# ---------------------------------------------------------------------------

def ckpt_path(state):
    return CKPT_DIR / f"{state}.json"


def save_ckpt(state, payload):
    CKPT_DIR.mkdir(parents=True, exist_ok=True)
    with open(ckpt_path(state), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)


def fetch_state(state, cfg, excl_sets, in_set, rng, want):
    if cfg.get("aggregate") and not cfg.get("spotcheck_passed"):
        return {"state": state, "status": "blocked-spotcheck",
                "note": "aggregate source; run --spotcheck and flip spotcheck_passed",
                "records": []}
    log = []
    cfg = dict(cfg)
    cfg["_state"] = state
    try:
        if cfg["type"] == "socrata":
            rows, total = fetch_socrata(cfg, rng, want * 3, log)
        elif cfg["type"] == "arcgis":
            if cfg.get("aggregate"):
                rows, total = fetch_aggregate(cfg, rng, int(want * 2.2), log)
            else:
                rows, total = fetch_arcgis(cfg, rng, want * 3, log)
        elif cfg["type"] == "carto":
            rows, total = fetch_carto(cfg, rng, want * 3, log)
        elif cfg["type"] == "csv":
            rows, total = fetch_csv_url(cfg, rng, want, log)
        else:
            raise ValueError(f"unknown type {cfg['type']}")
    except Exception as e:  # noqa: BLE001
        return {"state": state, "status": "gap-unreachable", "note": str(e)[:300],
                "records": [], "fetch_log": log}

    rng.shuffle(rows)
    records = []
    removed = {k: 0 for k in excl_sets}
    removed["within-gold2b"] = 0
    n_pulled = len(rows)
    for row in rows:
        raw = build_raw(cfg, row)
        if not raw or not plausible(raw, cfg, row):
            continue
        nid = norm_identity(raw)
        hit = None
        for name, s in excl_sets.items():
            if nid in s:
                hit = name
                break
        if hit is None and nid in in_set:
            hit = "within-gold2b"
        if hit:
            removed[hit] += 1
            continue
        in_set.add(nid)
        records.append({
            "raw": raw, "state": state, "source": cfg["source"],
            "dataset": cfg["dataset"], "fetched": FETCH_DATE,
        })
        if len(records) >= want:
            break
    status = "fetched" if len(records) >= 50 else ("thin" if records else "gap-unreachable")
    return {"state": state, "status": status,
            "note": f"dataset rows={total}", "rows_pulled": n_pulled,
            "dedupe_removed": removed, "fetch_log": log, "records": records}


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------

DIVISIONS = {
    "New England": ["CT", "ME", "MA", "NH", "RI", "VT"],
    "Middle Atlantic": ["NJ", "NY", "PA"],
    "East North Central": ["IL", "IN", "MI", "OH", "WI"],
    "West North Central": ["IA", "KS", "MN", "MO", "NE", "ND", "SD"],
    "South Atlantic": ["DE", "DC", "FL", "GA", "MD", "NC", "SC", "VA", "WV"],
    "East South Central": ["AL", "KY", "MS", "TN"],
    "West South Central": ["AR", "LA", "OK", "TX"],
    "Mountain": ["AZ", "CO", "ID", "MT", "NV", "NM", "UT", "WY"],
    "Pacific": ["AK", "CA", "HI", "OR", "WA"],
}
LEGAL_GAPS = {"CA": "Gov. Code \u00a77928.205", "ID": "Idaho Code 74-120",
              "KY": "fee-based PVA rolls"}
# WY was pre-registered as a hard gap but an open source was found and fetched
# (flagged judgment call, see SOURCE_MAP_2B.md).
DOCUMENTED_GAPS = {
    "CT": "gap-no-disjoint-source: reachable CT parcel layers are subsets of the "
          "statewide CAMA dataset (training-consumed) or lack owner mailing",
    "DC": "gap-no-disjoint-source: every public DC owner-mailing dataset is a view "
          "of the same OTR ITSPE dataset gold-2 used",
    "KS": "gap-no-disjoint-source: Sedgwick open-data parcels geometry-only; "
          "JoCo/Shawnee/Riley/Wyandotte/Saline/Reno expose no owner mailing",
    "ME": "gap-no-disjoint-source: town assessing flows through the statewide "
          "Organized Towns ADB (training-consumed); no independent town dataset found",
    "NH": "gap-no-disjoint-source: GRANIT mosaic has no owner attributes; no "
          "city/town dataset with owner mailing found",
    "VT": "gap-no-disjoint-source: all VT parcel data flows through VCGI statewide "
          "(training-consumed)",
}


def assemble(trim):
    states = {}
    for p in sorted(CKPT_DIR.glob("*.json")):
        with open(p, encoding="utf-8") as f:
            states[p.stem] = json.load(f)
    fetched = {s: d for s, d in states.items()
               if d["status"] in ("fetched", "thin") and d.get("records")}
    counts = {s: len(d["records"]) for s, d in fetched.items()}
    n_jur = len(fetched)
    if trim is None:
        # even per-jurisdiction n: smallest kept count, but never more than 70
        trim = min(min(counts.values()), 70) if counts else 0
    rng = random.Random(SEED + 1)
    GOLD2B_DIR.mkdir(parents=True, exist_ok=True)
    n_rec = 0
    with open(CANDIDATES_OUT, "w", encoding="utf-8") as f:
        for state in sorted(fetched):
            recs = list(fetched[state]["records"])
            if len(recs) > trim:
                recs = rng.sample(recs, trim)
            for rec in recs:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                n_rec += 1
    # manifest
    lines = []
    lines.append("# Gold-2b Fetch Manifest\n")
    lines.append(f"Generated by `benchmark/fetch_gold2b.py --assemble` on {FETCH_DATE}. "
                 f"Seed {SEED}. Even per-jurisdiction trim n={trim}.\n")
    lines.append("Stratification note: `state` is the SOURCE jurisdiction (whose roll "
                 "the record came from). Owner mailing addresses may point anywhere in "
                 "the US and out-of-state mail addresses are kept deliberately. "
                 "PO Box / RR / HC kept at natural frequency.\n")
    lines.append("Dedupe (normalized uppercase-alphanumeric identity) enforced against "
                 "gold-1, gold-2, clean, the realtext training corpus, and "
                 "eval/realtext_dev.jsonl, plus within gold-2b. Per-source removal "
                 "counts below.\n")
    lines.append("## Per-state outcomes\n")
    lines.append("| State | Outcome | Kept (pre-trim) | In set | Dataset | Rows pulled | Dedupe removed (by list) | Note |")
    lines.append("|---|---|---|---|---|---|---|---|")
    all_states = sorted(set(sum(DIVISIONS.values(), [])))
    for s in all_states:
        if s in states:
            d = states[s]
            rem = d.get("dedupe_removed", {})
            rem_s = ", ".join(f"{k}:{v}" for k, v in rem.items() if v) or "0"
            in_set_n = min(len(d.get("records", [])), trim) if s in fetched else 0
            lines.append(f"| {s} | {d['status']} | {len(d.get('records', []))} | {in_set_n} | "
                         f"{d.get('dataset', '')} | {d.get('rows_pulled', '')} | {rem_s} | {d.get('note', '')} |")
        elif s in LEGAL_GAPS:
            lines.append(f"| {s} | gap-legal | 0 | 0 |  |  |  | {LEGAL_GAPS[s]} |")
        elif s in DOCUMENTED_GAPS:
            lines.append(f"| {s} | gap-documented | 0 | 0 |  |  |  | {DOCUMENTED_GAPS[s]} (full reasoning in SOURCE_MAP_2B.md) |")
        else:
            lines.append(f"| {s} | not-attempted | 0 | 0 |  |  |  |  |")
    lines.append("")
    # fetch windows / logs per source
    lines.append("## Per-source fetch details (URL, windows/offsets, spot-checks)\n")
    for s in sorted(fetched):
        d = fetched[s]
        cfg = CONFIG.get(s, {})
        lines.append(f"### {s} — {d.get('dataset', '')}\n")
        lines.append(f"- Endpoint: `{cfg.get('source', d.get('records', [{}])[0].get('source', ''))}`")
        lines.append(f"- Fetched: {d['records'][0]['fetched'] if d.get('records') else ''};"
                     f" rows pulled: {d.get('rows_pulled', '?')}; kept pre-trim: {len(d.get('records', []))};"
                     f" in set after trim: {min(len(d.get('records', [])), trim)}")
        for ln in d.get("fetch_log", []):
            lines.append(f"- fetch: {ln}")
        rem = d.get("dedupe_removed", {})
        lines.append("- dedupe removed: " + (", ".join(f"{k}={v}" for k, v in rem.items()) or "n/a"))
        spot = SPOT_DIR / f"{s}.txt"
        if spot.exists():
            txt = spot.read_text(encoding="utf-8")
            tail = txt[txt.rfind("Heuristics"):].strip() if "Heuristics" in txt else ""
            lines.append(f"- spot-check evidence: `{spot}`" + (f" — {tail.splitlines()[0]}" if tail else ""))
        lines.append("")
    # divisions
    lines.append("## Census-division coverage\n")
    lines.append("| Division | States fetched | Covered |")
    lines.append("|---|---|---|")
    covered = 0
    for div, members in DIVISIONS.items():
        got = sorted(set(fetched) & set(members))
        ok = "YES" if got else "no"
        covered += bool(got)
        lines.append(f"| {div} | {', '.join(got) if got else '\u2014'} | {ok} |")
    lines.append("")
    n_states = len(set(fetched) - {"DC"})
    has_dc = "DC" in fetched
    floor = "MET" if (covered == 9 and n_states >= 40) else "NOT MET"
    size_ok = "MET" if n_rec >= SIZE_FLOOR else "NOT MET"
    lines.append(f"**Totals: {n_states} states{' + DC' if has_dc else ''}, {n_rec} records "
                 f"(even n={trim} \u00d7 {n_jur} jurisdictions), {covered}/9 divisions. "
                 f"Coverage floor (9 divisions + >=40 states): {floor}. "
                 f"Size floor (>= {SIZE_FLOOR}): {size_ok}.** "
                 f"(DC counted separately, not as a state.)")
    lines.append("")
    with open(MANIFEST_OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Wrote {n_rec} records (n={trim} x {n_jur} jurisdictions) -> {CANDIDATES_OUT}")
    print(f"Manifest -> {MANIFEST_OUT}; divisions {covered}/9; coverage {floor}; size {size_ok}")


# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--spotcheck", metavar="STATE")
    ap.add_argument("--fetch", metavar="STATE")
    ap.add_argument("--fetch-all", action="store_true")
    ap.add_argument("--assemble", action="store_true")
    ap.add_argument("--trim", type=int, default=None)
    ap.add_argument("--want", type=int, default=TARGET_PER_STATE)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    rng = random.Random(SEED)

    if args.list:
        for s, c in sorted(CONFIG.items()):
            agg = " [aggregate%s]" % ("/SPOTCHECKED" if c.get("spotcheck_passed") else "/needs-spotcheck") if c.get("aggregate") else ""
            print(f"{s}: {c['type']:8s} {c['dataset']}{agg}")
        return

    if args.spotcheck:
        s = args.spotcheck.upper()
        spotcheck(s, CONFIG[s], rng)
        return

    targets = []
    if args.fetch:
        targets = [args.fetch.upper()]
    elif args.fetch_all:
        targets = sorted(CONFIG)

    if targets:
        excl = load_exclusion_sets()
        for name, s in excl.items():
            print(f"exclusion [{name}]: {len(s)} identities")
        in_set = set()
        for p in CKPT_DIR.glob("*.json"):
            with open(p, encoding="utf-8") as f:
                for rec in json.load(f).get("records", []):
                    in_set.add(norm_identity(rec["raw"]))
        for s in targets:
            if ckpt_path(s).exists() and not args.force:
                print(f"[{s}] checkpoint exists, skipping (use --force to refetch)")
                continue
            print(f"[{s}] fetching ...")
            result = fetch_state(s, CONFIG[s], excl, in_set, rng, args.want)
            result["dataset"] = CONFIG[s]["dataset"]
            save_ckpt(s, result)
            rem = result.get("dedupe_removed", {})
            rem_s = ", ".join(f"{k}={v}" for k, v in rem.items() if v)
            print(f"[{s}] {result['status']}: {len(result['records'])} records "
                  f"({result.get('note', '')}) dedupe[{rem_s}]")

    if args.assemble:
        assemble(args.trim)

    if not (args.list or args.spotcheck or targets or args.assemble):
        ap.print_help()


if __name__ == "__main__":
    main()
