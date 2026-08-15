#!/usr/bin/env python3
"""Gold-2 sampler: fetch ~30 true free-text owner-mailing address records per state.

Per eval/gold2/PROTOCOL2.md and eval/gold2/SOURCE_MAP.md (plan unit U6).

Rules enforced here:
- FREE TEXT ONLY: address line must be a single free-text field as written.
  Component-assembled sources are ineligible and are not configured.
- Statewide GIS aggregates (NC, WI, MN, MT, ME) require a composed-text spot-check
  (--spotcheck STATE) across 2+ counties before sampling; a config entry only gets
  "spotcheck_passed": True after human inspection of the dump.
- Cook County IL and Allegheny County PA are training sources and are excluded
  entirely (not configured).
- Records whose owner mailing address is out-of-state relative to the source state
  are KEPT (owner mail can be anywhere in the US); "state" in the output is the
  SOURCE state stratum.
- PO Box / RR / HC records are valid and kept at natural frequency.
- Dedupe: normalized identity (uppercase alphanumeric collapse) must not appear in
  eval/gold/candidates.jsonl, eval/clean/clean.jsonl, or within gold-2 itself.

Usage:
  python benchmark/fetch_gold2.py --list                # show configured states
  python benchmark/fetch_gold2.py --spotcheck NC        # composed-text spot-check dump
  python benchmark/fetch_gold2.py --fetch NC            # fetch one state (checkpointed)
  python benchmark/fetch_gold2.py --fetch-all           # fetch all pending states
  python benchmark/fetch_gold2.py --assemble            # write candidates.jsonl + manifest

Checkpoints: eval/gold2/checkpoints/<STATE>.json — a state with a checkpoint is
skipped on re-run (resumable); delete the file to refetch.
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
GOLD2_DIR = ROOT / "eval" / "gold2"
CKPT_DIR = GOLD2_DIR / "checkpoints"
CANDIDATES_OUT = GOLD2_DIR / "candidates.jsonl"
MANIFEST_OUT = GOLD2_DIR / "FETCH_MANIFEST.md"
GOLD1_CANDIDATES = ROOT / "eval" / "gold" / "candidates.jsonl"
CLEAN_JSONL = ROOT / "eval" / "clean" / "clean.jsonl"

TARGET_PER_STATE = 34          # a few extra; trimmed later
CHUNKS = 4                     # random-offset chunks per non-aggregate source
SEED = 20260815
TIMEOUT = 60
UA = "fastaddress-gold2-sampler/1.0 (research eval set; contact: repo maintainer)"

FETCH_DATE = dt.date.today().isoformat()

# ---------------------------------------------------------------------------
# Per-state source config, derived from eval/gold2/SOURCE_MAP.md.
# addr_fields: ordered free-text line fields (empties skipped, joined by space).
# city/state/zip fields may be None when the info lives inside a line field.
# "aggregate": statewide multi-county aggregate -> needs spotcheck_passed + county_field.
# ---------------------------------------------------------------------------
CONFIG = {
    "CT": {
        "type": "socrata", "domain": "data.ct.gov", "dataset_id": "pqrn-qghw",
        "dataset": "CT Parcel and CAMA Data (statewide)",
        "source": "https://data.ct.gov/resource/pqrn-qghw.json",
        "addr_fields": ["mailing_address"], "city": "mailing_city",
        "st": "mailing_state", "zip": "mailing_zip",
        "where": "mailing_address IS NOT NULL",
    },
    "DC": {
        "type": "arcgis",
        "endpoint": "https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Property_and_Land_WebMercator/MapServer/53",
        "dataset": "DC Integrated Tax System Public Extract (ITSPE)",
        "source": "https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Property_and_Land_WebMercator/MapServer/53",
        "addr_fields": ["ADDRESS1", "ADDRESS2"], "city": None, "st": None, "zip": None,
        "citystzip": "CITYSTZIP",
        "where": "ADDRESS1 IS NOT NULL",
    },
    "GA": {
        "type": "arcgis",
        "endpoint": "https://gismaps.fultoncountyga.gov/arcgispub2/rest/services/PropertyMapViewer/PropertyMapViewer/MapServer/11",
        "dataset": "Fulton County GA Tax Parcels",
        "source": "https://gismaps.fultoncountyga.gov/arcgispub2/rest/services/PropertyMapViewer/PropertyMapViewer/MapServer/11",
        "addr_fields": ["OwnerAddr1", "OwnerAddr2"], "city": None, "st": None, "zip": None,
        "where": "OwnerAddr1 IS NOT NULL AND OwnerAddr2 IS NOT NULL",
    },
    "LA": {
        "type": "socrata", "domain": "data.brla.gov", "dataset_id": "myfc-nh6n",
        "dataset": "East Baton Rouge Parish Tax Roll",
        "source": "https://data.brla.gov/resource/myfc-nh6n.json",
        "addr_fields": ["taxpayer_addr_1", "taxpayer_addr_2"],
        "city": None, "st": None, "zip": None,
        "where": "taxpayer_addr_1 IS NOT NULL AND taxpayer_addr_2 IS NOT NULL",
    },
    "MI": {
        "type": "arcgis",
        "endpoint": "https://services2.arcgis.com/qvkbeam7Wirps6zC/arcgis/rest/services/Parcels_Current/FeatureServer/0",
        "dataset": "Detroit Parcels (Current)",
        "source": "https://services2.arcgis.com/qvkbeam7Wirps6zC/arcgis/rest/services/Parcels_Current/FeatureServer/0",
        "addr_fields": ["taxpayer_street"], "city": "taxpayer_city",
        "st": "taxpayer_state", "zip": "taxpayer_zip",
        "where": "taxpayer_street IS NOT NULL",
    },
    "NY": {
        "type": "socrata", "domain": "data.buffalony.gov", "dataset_id": "4t8s-9yih",
        "dataset": "Buffalo NY Current Assessment Roll",
        "source": "https://data.buffalony.gov/resource/4t8s-9yih.json",
        "addr_fields": ["mail3", "mail4"], "city": None, "st": None, "zip": "mail_zipcode",
        "where": "mail3 IS NOT NULL AND mail4 IS NOT NULL",
    },
    "NC": {
        "type": "arcgis",
        "endpoint": "https://services.nconemap.gov/secure/rest/services/NC1Map_Parcels/FeatureServer/1",
        "dataset": "NC OneMap Parcels (statewide standardized)",
        "source": "https://services.nconemap.gov/secure/rest/services/NC1Map_Parcels/FeatureServer/1",
        "addr_fields": ["mailadd"], "city": "mcity", "st": "mstate", "zip": "mzip",
        "where": "mailadd IS NOT NULL",
        "aggregate": True, "county_field": "cntyname",
        # Spot-check 2026-08-15 (Burke, Anson, Wilkes; 75 lines): genuine free text —
        # abbreviation variety (ROAD/RD/CH RD/CTR RD), "P O BOX", "c/o Linda Thompson",
        # apostrophes, 20% PO Box. PASS. Anson embeds quote-mangled city/zip inside
        # mailadd -> skip_pattern excludes malformed rows.
        "spotcheck_passed": True,
        "skip_pattern": r'"',
    },
    "PA": {
        "type": "carto", "domain": "phl.carto.com", "table": "opa_properties_public",
        "dataset": "Philadelphia OPA Properties",
        "source": "https://phl.carto.com/api/v2/sql (opa_properties_public)",
        "addr_fields": ["mailing_street", "mailing_city_state"],
        "city": None, "st": None, "zip": "mailing_zip",
        "where": "mailing_street IS NOT NULL AND mailing_city_state IS NOT NULL",
    },
    "RI": {
        # NOTE: street_1/city_1 are parse COMPONENTS (civic_1+street_1+s_suffix) —
        # ineligible. free_line_2/free_line_3 are the true free-text mailing label
        # lines (mixed case, "PO Box", "Apt" variants observed). 2022 roll; newer
        # rolls dropped the free_line fields.
        "type": "socrata", "domain": "data.providenceri.gov", "dataset_id": "c3q4-f95q",
        "dataset": "Providence RI 2022 Property Tax Roll",
        "source": "https://data.providenceri.gov/resource/c3q4-f95q.json",
        "addr_fields": ["free_line_2", "free_line_3"],
        "city": None, "st": None, "zip": None,
        "where": "free_line_2 IS NOT NULL AND free_line_3 IS NOT NULL",
    },
    "FL": {
        "type": "arcgis",
        "endpoint": "https://services9.arcgis.com/Gh9awoU677aKree0/arcgis/rest/services/Florida_Statewide_Cadastral/FeatureServer/0",
        "dataset": "FDOR Florida Statewide Cadastral (NAL owner fields)",
        "source": "https://services9.arcgis.com/Gh9awoU677aKree0/arcgis/rest/services/Florida_Statewide_Cadastral/FeatureServer/0",
        "addr_fields": ["OWN_ADDR1", "OWN_ADDR2"], "city": "OWN_CITY",
        "st": "OWN_STATE", "zip": "OWN_ZIPCD",
        # Service rejects where-clauses on attribute fields and deep resultOffset;
        # sample by random OBJECTID windows instead, filter nulls client-side.
        "where": "1=1", "objectid_sampling": True,
    },
    "MA": {
        "type": "arcgis",
        "endpoint": "https://services1.arcgis.com/hGdibHYSPO59RG1h/arcgis/rest/services/Massachusetts_Property_Tax_Parcels/FeatureServer/0",
        "dataset": "MassGIS Standardized Assessors' Parcels (statewide)",
        "source": "https://services1.arcgis.com/hGdibHYSPO59RG1h/arcgis/rest/services/Massachusetts_Property_Tax_Parcels/FeatureServer/0",
        "addr_fields": ["OWN_ADDR"], "city": "OWN_CITY", "st": "OWN_STATE",
        "zip": "OWN_ZIP",
        "where": "OWN_ADDR IS NOT NULL",
    },
    "VT": {
        "type": "arcgis",
        "endpoint": "https://services1.arcgis.com/BkFxaEFNwHqX3tAw/arcgis/rest/services/FS_VCGI_OPENDATA_Cadastral_VTPARCELS_poly_standardized_parcels_SP_v1/FeatureServer/0",
        "dataset": "VCGI VT Statewide Standardized Parcels (Grand List owner mailing)",
        "source": "https://services1.arcgis.com/BkFxaEFNwHqX3tAw/arcgis/rest/services/FS_VCGI_OPENDATA_Cadastral_VTPARCELS_poly_standardized_parcels_SP_v1/FeatureServer/0",
        "addr_fields": ["ADDRGL1", "ADDRGL2"], "city": "CITYGL", "st": "STGL",
        "zip": "ZIPGL",
        "where": "ADDRGL1 IS NOT NULL",
    },
    "NJ": {
        "type": "arcgis",
        "endpoint": "https://services2.arcgis.com/XVOqAjTOJ5P6ngMu/arcgis/rest/services/Parcels_Composite_NJ_WM/FeatureServer/0",
        "dataset": "NJ Parcels and MOD-IV Composite (statewide)",
        "source": "https://services2.arcgis.com/XVOqAjTOJ5P6ngMu/arcgis/rest/services/Parcels_Composite_NJ_WM/FeatureServer/0",
        "addr_fields": ["ST_ADDRESS", "CITY_STATE"], "city": None, "st": None,
        "zip": "ZIP_CODE",
        "where": "ST_ADDRESS IS NOT NULL AND CITY_STATE IS NOT NULL",
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
        # Spot-check 2026-08-15 (3 counties, 75 lines): human inconsistency within
        # one complex ("Quarry Rdg Ln # D" / "Quarry Ridge Ln # D" / "Quarry Ridge
        # Lane Ct # 187"), 11% units. PASS.
        "spotcheck_passed": True,
    },
    "MT": {
        "type": "arcgis",
        "endpoint": "https://services.arcgis.com/qnjIrwR8z5Izc0ij/arcgis/rest/services/Montana_Cadastral_Framework/FeatureServer/1",
        "dataset": "Montana Cadastral Framework (DOR ORION owner mailing)",
        "source": "https://services.arcgis.com/qnjIrwR8z5Izc0ij/arcgis/rest/services/Montana_Cadastral_Framework/FeatureServer/1",
        "addr_fields": ["OwnerAddress1", "OwnerAddress2", "OwnerAddress3"],
        "city": "OwnerCity", "st": "OwnerState", "zip": "OwnerZipCode",
        "where": "OwnerAddress1 IS NOT NULL",
        "aggregate": True, "county_field": "CountyName",
        # Spot-check 2026-08-15 (3 counties, 75 lines): "MAIL TO: KELLY COSGRIFF",
        # "RR 1 BOX 1116", "DEPT OF STATE LANDS", 45% PO/RR/HC. Clearly free text. PASS.
        "spotcheck_passed": True,
    },
    "WI": {
        "type": "arcgis",
        "endpoint": "https://services3.arcgis.com/n6uYoouQZW75n5WI/arcgis/rest/services/Wisconsin_Statewide_Parcels_DB/FeatureServer/0",
        "dataset": "Wisconsin Statewide Parcels V12 (PSTLADRESS owner full mailing)",
        "source": "https://services3.arcgis.com/n6uYoouQZW75n5WI/arcgis/rest/services/Wisconsin_Statewide_Parcels_DB/FeatureServer/0",
        "addr_fields": ["PSTLADRESS"], "city": None, "st": None, "zip": None,
        "where": "PSTLADRESS IS NOT NULL",
        "aggregate": True, "county_field": "CONAME",
        # Spot-check 2026-08-15 (3 counties, 75 lines): SUITE/STE/UNIT embedded in
        # line, PO BOX, WI grid addresses (N85W16303), zip quirks (53095-0000).
        # One county joins segments with " , " but content is pass-through. PASS.
        "spotcheck_passed": True,
    },
    "IN": {
        "type": "arcgis",
        "endpoint": "https://gis.indy.gov/server/rest/services/MapIndy/MapIndyProperty/MapServer/10",
        "dataset": "Indy/Marion County Parcels w/ Owner Information",
        "source": "https://gis.indy.gov/server/rest/services/MapIndy/MapIndyProperty/MapServer/10",
        "addr_fields": ["OWNERADDRESS", "OWNERADDRESS2"], "city": "OWNERCITY",
        "st": "OWNERSTATE", "zip": "OWNERZIP",
        "where": "OWNERADDRESS IS NOT NULL",
    },
    "WA": {
        "type": "arcgis",
        "endpoint": "https://services.arcgis.com/Ej0PsM5Aw677QF1W/arcgis/rest/services/PARCEL_ADDRESS_PUB_AREA_3069/FeatureServer/0",
        "dataset": "King County WA Parcels with Ownership Information (taxpayer mailing)",
        "source": "https://services.arcgis.com/Ej0PsM5Aw677QF1W/arcgis/rest/services/PARCEL_ADDRESS_PUB_AREA_3069/FeatureServer/0",
        "addr_fields": ["KCTP_ADDR", "KCTP_CTYST"], "city": None, "st": None,
        "zip": "KCTP_ZIP",
        "where": "KCTP_ADDR IS NOT NULL AND KCTP_CTYST IS NOT NULL",
    },
    "OR": {
        "type": "arcgis",
        "endpoint": "https://services1.arcgis.com/znO8Hz1SuVVohYhZ/arcgis/rest/services/Taxlots/FeatureServer/4",
        "dataset": "Deschutes County OR Taxlots — GIS_MAILING (owner mailing)",
        "source": "https://services1.arcgis.com/znO8Hz1SuVVohYhZ/arcgis/rest/services/Taxlots/FeatureServer/4",
        "addr_fields": ["M_ADDRESS", "M_CITYSTZIP"], "city": None, "st": None,
        "zip": None,
        "where": "M_ADDRESS IS NOT NULL AND M_CITYSTZIP IS NOT NULL",
    },
    "TX": {
        "type": "arcgis",
        "endpoint": "https://gis.georgetowntexas.gov/arcgis/rest/services/OpenData/OpenData_FeatureService/FeatureServer/2",
        "dataset": "Williamson County TX Parcels (Georgetown open data)",
        "source": "https://gis.georgetowntexas.gov/arcgis/rest/services/OpenData/OpenData_FeatureService/FeatureServer/2",
        "addr_fields": ["MAILADD"], "city": "MAILCITY", "st": "MAILST",
        "zip": "MAILZIP",
        "where": "MAILADD IS NOT NULL",
    },
    "AZ": {
        # Pima County regional parcels via City of Tucson MapServer. ADDRESS is
        # the assessor's owner-mailing line (ADDRESSEE/MAIL1-5 carry the label);
        # SITE_* fields are the separate situs.
        "type": "arcgis",
        "endpoint": "https://mapdata.tucsonaz.gov/public/rest/services/PublicMaps/PropertyHousing/MapServer/40",
        "dataset": "Pima County AZ Parcels - Regional (Tucson PropertyHousing)",
        "source": "https://mapdata.tucsonaz.gov/public/rest/services/PublicMaps/PropertyHousing/MapServer/40",
        "addr_fields": ["ADDRESS"], "city": "CITY", "st": "STATE_PROVINCE",
        "zip": "POSTAL_CODE",
        "where": "ADDRESS IS NOT NULL",
    },
    "ME": {
        # Maine Parcels Organized Towns ADB ownership table (statewide town
        # aggregate). GEOCODE = town code, used as the aggregate stratum for the
        # PROTOCOL2 spot-check (town-level rolls; Maine assesses by town).
        "type": "arcgis",
        "endpoint": "https://services1.arcgis.com/RbMX0mRVOFNTdLzd/arcgis/rest/services/Maine_Parcels_Organized_Towns/FeatureServer/9",
        "dataset": "Maine Parcels Organized Towns ADB (ownership table)",
        "source": "https://services1.arcgis.com/RbMX0mRVOFNTdLzd/arcgis/rest/services/Maine_Parcels_Organized_Towns/FeatureServer/9",
        "addr_fields": ["OWN_ADDR1", "OWN_ADDR2"], "city": "OWN_CITY",
        "st": "OWN_STATE", "zip": "OWN_ZIP",
        "where": "OWN_ADDR1 IS NOT NULL AND OWN_ADDR1 <> ''",
        "aggregate": True, "county_field": "GEOCODE",
        # Spot-check 2026-08-15 (3 towns, 75 lines): per-town conventions with
        # human inconsistency ("P.O. Box 119"/"P.O. BOX 119", trailing periods
        # "32 SMITH AVE.", "c/o KARL D. WELLS", "3 CHASE ST., SUITE 1", 35%%
        # PO/RR). PASS.
        "spotcheck_passed": True,
    },
    "MD": {
        # MAILTOADD is a single free-text mail-to line including city/state/zip
        # as written (some rows quirky: "2633 GWYNNS FALLS PKWY, 21216" — no city).
        "type": "arcgis",
        "endpoint": "https://services1.arcgis.com/UWYHeuuJISiGmgXx/arcgis/rest/services/Real_property_CAMA/FeatureServer/0",
        "dataset": "Baltimore City MD Real Property CAMA",
        "source": "https://services1.arcgis.com/UWYHeuuJISiGmgXx/arcgis/rest/services/Real_property_CAMA/FeatureServer/0",
        "addr_fields": ["MAILTOADD"], "city": None, "st": None, "zip": None,
        "where": "MAILTOADD IS NOT NULL",
    },
    "OH": {
        "type": "arcgis",
        "endpoint": "https://gis.cuyahogacounty.us/server/rest/services/MyPLACE/Parcels_WMA_GJOIN_WGS84/MapServer/2",
        "dataset": "Cuyahoga County OH Parcels (MyPLACE, fiscal-office join)",
        "source": "https://gis.cuyahogacounty.us/server/rest/services/MyPLACE/Parcels_WMA_GJOIN_WGS84/MapServer/2",
        "addr_fields": ["mail_addr_street", "mail_unit"], "city": "mail_city",
        "st": "mail_state", "zip": "mail_zip",
        "where": "mail_addr_street IS NOT NULL",
    },
    "TN": {
        "type": "arcgis",
        "endpoint": "https://services2.arcgis.com/HdTo6HJqh92wn4D8/arcgis/rest/services/Parcels_view/FeatureServer/0",
        "dataset": "Metro Nashville/Davidson County TN Parcels",
        "source": "https://services2.arcgis.com/HdTo6HJqh92wn4D8/arcgis/rest/services/Parcels_view/FeatureServer/0",
        "addr_fields": ["OwnAddr1", "OwnAddr2", "OwnAddr3"], "city": "OwnCity",
        "st": "OwnState", "zip": "OwnZip",
        "where": "OwnAddr1 IS NOT NULL",
    },
    "VA": {
        "type": "arcgis",
        "endpoint": "https://services1.arcgis.com/k3vhq11XkBNeeOfM/arcgis/rest/services/Parcels/FeatureServer/0",
        "dataset": "City of Richmond VA Parcels (GeoHub)",
        "source": "https://services1.arcgis.com/k3vhq11XkBNeeOfM/arcgis/rest/services/Parcels/FeatureServer/0",
        "addr_fields": ["MailAddress"], "city": "MailCity", "st": "MailState",
        "zip": "MailZip",
        "where": "MailAddress IS NOT NULL",
    },
    "ND": {
        "type": "arcgis",
        "endpoint": "https://gisweb.casscountynd.gov/arcgis/rest/services/OpenData/OpenData/FeatureServer/7",
        "dataset": "Cass County ND Tax Parcels (Open Data)",
        "source": "https://gisweb.casscountynd.gov/arcgis/rest/services/OpenData/OpenData/FeatureServer/7",
        "addr_fields": ["MailAddr", "MailAddr2"], "city": "MailCity",
        "st": "MailState", "zip": "MailZip",
        "where": "MailAddr IS NOT NULL",
    },
    "AL": {
        "type": "arcgis",
        "endpoint": "https://jccgis.jccal.org/server/rest/services/Basemap/Parcels/MapServer/0",
        "dataset": "Jefferson County AL Parcels (Basemap)",
        "source": "https://jccgis.jccal.org/server/rest/services/Basemap/Parcels/MapServer/0",
        "addr_fields": ["PROP_MAIL"], "city": "CITYMAIL", "st": "STATE_Mail",
        "zip": "ZIP_MAIL",
        "where": "PROP_MAIL IS NOT NULL",
    },
    "NE": {
        "type": "arcgis",
        "endpoint": "https://services9.arcgis.com/ksv1wRvySwOGRs8x/arcgis/rest/services/Parcel_and_Address_(public)/FeatureServer/3",
        "dataset": "Washington County NE Ownership Parcels (Blair)",
        "source": "https://services9.arcgis.com/ksv1wRvySwOGRs8x/arcgis/rest/services/Parcel_and_Address_(public)/FeatureServer/3",
        "addr_fields": ["Mail1", "Mail2", "Mail3"], "city": None, "st": None,
        "zip": None,
        "where": "Mail1 IS NOT NULL",
    },
    "OK": {
        "type": "arcgis",
        "endpoint": "https://services2.arcgis.com/0NjdXxmJp53hZWPd/arcgis/rest/services/ParcelDataService_2_view/FeatureServer/3",
        "dataset": "Canadian County OK Parcel Data (Public)",
        "source": "https://services2.arcgis.com/0NjdXxmJp53hZWPd/arcgis/rest/services/ParcelDataService_2_view/FeatureServer/3",
        "addr_fields": ["mail_address"], "city": "mail_city", "st": "mail_state",
        "zip": "mail_zip",
        "where": "mail_address IS NOT NULL",
    },
    "SD": {
        # GranteeFullAddr is the stored line: component fields are truncated
        # derivatives (GranteeStreetName caps at 24 chars, e.g. "MILE HIGH
        # STADIUM CIR AP" vs full "1919 MILE HIGH STADIUM CIR APT 426"), and no
        # unit component exists — so the full line cannot be composed from them.
        "type": "arcgis",
        "endpoint": "https://gis.rcgov.org/server/rest/services/OpenData/TaxParcels/FeatureServer/0",
        "dataset": "Rapid City/Pennington County SD Tax Parcels (RCPC Open Data)",
        "source": "https://gis.rcgov.org/server/rest/services/OpenData/TaxParcels/FeatureServer/0",
        "addr_fields": ["GranteeFullAddr"], "city": "GranteeCity",
        "st": "GranteeState", "zip": "GranteeZip",
        "where": "GranteeFullAddr IS NOT NULL",
    },
    "CO": {
        # ADDRESS1/ADDRESS2 are the owner mailing label lines (ADDRESS1 often a
        # second recipient line, e.g. "RACUSIN WARREN ESQ"); STREET* fields are
        # the separate situs components.
        "type": "arcgis",
        "endpoint": "https://services.arcgis.com/aXqye4IXyXsdIpPb/arcgis/rest/services/TaxParcelsPublic/FeatureServer/0",
        "dataset": "San Miguel County CO Tax Parcels (Public)",
        "source": "https://services.arcgis.com/aXqye4IXyXsdIpPb/arcgis/rest/services/TaxParcelsPublic/FeatureServer/0",
        "addr_fields": ["ADDRESS1", "ADDRESS2"], "city": "CITY", "st": "STATE",
        "zip": "ZIPCODE",
        "where": "1=1", "objectid_sampling": True,
    },
    "WV": {
        "type": "arcgis",
        "endpoint": "https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/WV_Parcels/MapServer/0",
        "dataset": "WV Statewide Parcels (WVU GIS Tech Center, IAS owner mailing)",
        "source": "https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/WV_Parcels/MapServer/0",
        "addr_fields": ["FullOwnerAddress"], "city": None, "st": None, "zip": None,
        "where": "FullOwnerAddress IS NOT NULL",
        "aggregate": True, "county_field": "COUNTY",
        # Spot-check 2026-08-15 (3 county codes, 75 lines): ST/STREET side-by-side,
        # misspellings ("POCAHANTAS"), PO Box, embedded owner names, out-of-state
        # rows. Human-entered pass-through. PASS.
        "spotcheck_passed": True,
    },
    "SC": {
        "type": "arcgis",
        "endpoint": "https://services1.arcgis.com/2AGLxyiJoNiVHKwq/arcgis/rest/services/Parcels/FeatureServer/0",
        "dataset": "York County SC Parcels",
        "source": "https://services1.arcgis.com/2AGLxyiJoNiVHKwq/arcgis/rest/services/Parcels/FeatureServer/0",
        "addr_fields": ["MailAddr1", "MailAddr2", "MailApt"], "city": "MailCity",
        "st": "MailState", "zip": "MailZip",
        "where": "MailAddr1 IS NOT NULL",
    },
    "IL": {
        # Cook County is a training source (excluded); IL fulfilled from
        # Winnebago County (Rockford) instead.
        "type": "arcgis",
        "endpoint": "https://services9.arcgis.com/s8vOzt2hgxqrWawQ/arcgis/rest/services/Parcels_and_Addresses/FeatureServer/1",
        "dataset": "Winnebago County IL Parcel Ownership (taxpayer mailing)",
        "source": "https://services9.arcgis.com/s8vOzt2hgxqrWawQ/arcgis/rest/services/Parcels_and_Addresses/FeatureServer/1",
        "addr_fields": ["TaxpayerAddress1", "TaxpayerAddress2"],
        "city": "TaxpayerCity", "st": "TaxpayerState", "zip": "TaxpayerZip",
        "where": "TaxpayerAddress1 IS NOT NULL",
    },
    "MO": {
        "type": "arcgis",
        "endpoint": "https://services.arcgis.com/sbDzK061dd6DNPHv/arcgis/rest/services/COI_Parcels_2_view/FeatureServer/0",
        "dataset": "City of Independence MO (Jackson County) Parcels",
        "source": "https://services.arcgis.com/sbDzK061dd6DNPHv/arcgis/rest/services/COI_Parcels_2_view/FeatureServer/0",
        "addr_fields": ["owneraddress"], "city": "ownercity", "st": "ownerstate",
        "zip": "ownerzipcode",
        "where": "owneraddress IS NOT NULL",
    },
    "NM": {
        "type": "arcgis",
        "endpoint": "https://services7.arcgis.com/p0Gk2nDbPs7KEqSZ/arcgis/rest/services/SFC_Parcels_20250415/FeatureServer/0",
        "dataset": "Santa Fe County NM Land Parcels",
        "source": "https://services7.arcgis.com/p0Gk2nDbPs7KEqSZ/arcgis/rest/services/SFC_Parcels_20250415/FeatureServer/0",
        "addr_fields": ["Owner_Care", "Owner_Line", "Owner_Li_1", "Owner_Li_2"],
        "city": "Owner_City", "st": "Owner_Stat", "zip": "Owner_Zip",
        "where": "Owner_Line IS NOT NULL",
    },
    "IA": {
        "type": "arcgis",
        "endpoint": "https://services.arcgis.com/i14SLLmXo7Hn9vNc/arcgis/rest/services/RealEstateParcel/FeatureServer/0",
        "dataset": "Linn County IA Real Estate Parcels",
        "source": "https://services.arcgis.com/i14SLLmXo7Hn9vNc/arcgis/rest/services/RealEstateParcel/FeatureServer/0",
        "addr_fields": ["OwnerAttention", "OwnerAddress"], "city": "OwnerCity",
        "st": "OwnerState", "zip": "OwnerZip",
        "where": "OwnerAddress IS NOT NULL",
    },
    "AK": {
        "type": "arcgis",
        "endpoint": "https://maps.matsugov.us/map/rest/services/OpenData/Cadastral_Parcels/FeatureServer/0",
        "dataset": "Matanuska-Susitna Borough AK Cadastral Parcels",
        "source": "https://maps.matsugov.us/map/rest/services/OpenData/Cadastral_Parcels/FeatureServer/0",
        "addr_fields": ["MAILING_ADDRESS_LINE_A", "MAILING_ADDRESS_LINE_B"],
        "city": "MAILING_ADDRESS_CITY", "st": "MAILING_ADDRESS_STATE",
        "zip": "MAILING_ADDRESS_ZIP",
        "where": "MAILING_ADDRESS_LINE_B <> '' AND MAILING_ADDRESS_LINE_B IS NOT NULL",
    },
    "KS": {
        # City of Maize (Sedgwick County) parcels; small jurisdiction (~6k rows
        # with owner mailing) but genuine free text ("P.O. BOX 12198").
        "type": "arcgis",
        "endpoint": "https://services3.arcgis.com/PRyeAMTgQS8gkd0F/arcgis/rest/services/Maize_Parcels/FeatureServer/0",
        "dataset": "City of Maize KS Parcels (Sedgwick County)",
        "source": "https://services3.arcgis.com/PRyeAMTgQS8gkd0F/arcgis/rest/services/Maize_Parcels/FeatureServer/0",
        "addr_fields": ["Owner_madd"], "city": "Owner_City", "st": "Owner_Stat",
        "zip": "Owner_Zip",
        "where": "Owner_madd IS NOT NULL",
    },
    "NV": {
        # Carson City assessor data table: Mail_Addr is label line 1 (sometimes a
        # recipient/trustee line), Mail2_Addr line 2; MCity embeds "CITY, ST";
        # MZip has natural quirks ("89703-    ").
        "type": "arcgis",
        "endpoint": "https://portal.carsoncity.gov/server/rest/services/CarsonCity/CarsonCityNV_OpenData/MapServer/42",
        "dataset": "Carson City NV Assessor Data (AssrData)",
        "source": "https://portal.carsoncity.gov/server/rest/services/CarsonCity/CarsonCityNV_OpenData/MapServer/42",
        "addr_fields": ["Mail_Addr", "Mail2_Addr"], "city": "MCity", "st": None,
        "zip": "MZip",
        "where": "Mail_Addr IS NOT NULL",
    },
    "NE": {
        "type": "arcgis",
        "endpoint": "https://geodata.sarpy.gov/arcgis/rest/services/Cadastral/LandRecordsSearch/MapServer/5",
        "dataset": "Sarpy County NE Tax Parcels",
        "source": "https://geodata.sarpy.gov/arcgis/rest/services/Cadastral/LandRecordsSearch/MapServer/5",
        "addr_fields": ["PSTLADDRESS"], "city": "PSTLCITY", "st": "PSTLSTATE",
        "zip": "PSTLZIP5",
        "where": "PSTLADDRESS IS NOT NULL",
    },
}

# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def http_get(url, retries=3):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"GET failed after {retries} tries: {url} ({last})")


def get_json(url):
    return json.loads(http_get(url).decode("utf-8", "replace"))


# ---------------------------------------------------------------------------
# Normalization / dedupe
# ---------------------------------------------------------------------------

def norm_identity(raw: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", raw.upper())


def load_exclusion_set():
    seen = set()
    for path in (GOLD1_CANDIDATES, CLEAN_JSONL):
        if not path.exists():
            print(f"WARNING: exclusion file missing: {path}", file=sys.stderr)
            continue
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
                if raw:
                    seen.add(norm_identity(raw))
    return seen


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
            parts.append(clean_part(row.get(cfg[key])))
    parts = [p for p in parts if p]
    # Skip a line identical to the previous one (data-entry duplication seen in
    # ME ADB, where OWN_ADDR2 sometimes repeats OWN_ADDR1 verbatim).
    deduped = []
    for p in parts:
        if deduped and p.strip().upper() == deduped[-1].strip().upper():
            continue
        deduped.append(p)
    raw = " ".join(deduped)
    raw = re.sub(r"\s+", " ", raw).strip()
    return raw


def plausible(raw, cfg, row):
    """Minimal validity: the address LINE (first addr field with content) exists
    and the whole raw has at least 3 tokens. No format policing beyond that —
    free text is allowed to be weird."""
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
# Portal fetchers — each returns a list of row dicts
# ---------------------------------------------------------------------------

def soc_url(cfg, params):
    q = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    return f"https://{cfg['domain']}/resource/{cfg['dataset_id']}.json?{q}"


def fetch_socrata(cfg, rng, want):
    base_where = cfg.get("where")
    p = {"$select": "count(*) as n"}
    if base_where:
        p["$where"] = base_where
    n = int(get_json(soc_url(cfg, p))[0]["n"])
    rows = []
    chunk = max(10, want // CHUNKS + 2)
    offsets = sorted(rng.sample(range(max(1, n - chunk)), min(CHUNKS, max(1, n // chunk)))) if n > chunk else [0]
    for off in offsets:
        p = {"$limit": str(chunk), "$offset": str(off), "$order": ":id"}
        if base_where:
            p["$where"] = base_where
        rows.extend(get_json(soc_url(cfg, p)))
        time.sleep(0.5)
    return rows, n


def arcgis_query(endpoint, params):
    params = dict(params)
    params["f"] = "json"
    url = endpoint + "/query?" + urllib.parse.urlencode(params)
    d = get_json(url)
    if "error" in d:
        raise RuntimeError(f"ArcGIS error: {d['error']}")
    return d


def fetch_arcgis(cfg, rng, want, extra_where=None):
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
        # Random OBJECTID windows (for services that reject deep resultOffset).
        window = chunk * 4
        for _ in range(CHUNKS):
            r = rng.randrange(1, max(2, n - window))
            d = arcgis_query(cfg["endpoint"], {
                "where": f"OBJECTID >= {r} AND OBJECTID < {r + window}",
                "outFields": ",".join(out_fields),
                "returnGeometry": "false", "resultRecordCount": str(chunk),
            })
            rows.extend(f["attributes"] for f in d.get("features", []))
            time.sleep(0.5)
        return rows, n
    if n <= chunk:
        offsets = [0]
    else:
        offsets = sorted(rng.sample(range(max(1, n - chunk)), min(CHUNKS, max(1, n // chunk))))
    for off in offsets:
        d = arcgis_query(cfg["endpoint"], {
            "where": where, "outFields": ",".join(out_fields),
            "returnGeometry": "false", "resultOffset": str(off),
            "resultRecordCount": str(chunk),
        })
        rows.extend(f["attributes"] for f in d.get("features", []))
        time.sleep(0.5)
    return rows, n


def fetch_carto(cfg, rng, want):
    where = cfg.get("where", "TRUE")
    def sql(q):
        return get_json(f"https://{cfg['domain']}/api/v2/sql?q=" + urllib.parse.quote(q))
    n = sql(f"SELECT count(*) AS n FROM {cfg['table']} WHERE {where}")["rows"][0]["n"]
    rows = []
    chunk = max(10, want // CHUNKS + 2)
    offsets = sorted(rng.sample(range(max(1, n - chunk)), min(CHUNKS, max(1, n // chunk)))) if n > chunk else [0]
    cols = ",".join([*cfg["addr_fields"],
                     *[cfg[k] for k in ("city", "st", "zip") if cfg.get(k)]])
    for off in offsets:
        q = (f"SELECT {cols} FROM {cfg['table']} WHERE {where} "
             f"ORDER BY cartodb_id LIMIT {chunk} OFFSET {off}")
        rows.extend(sql(q)["rows"])
        time.sleep(0.5)
    return rows, n


def fetch_csv_url(cfg, rng, want):
    """Bulk CSV: size-check first; skip (deferred) if > 200MB."""
    url = cfg["csv_url"]
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            size = int(r.headers.get("Content-Length") or 0)
    except Exception:
        size = 0
    if size > 200 * 1024 * 1024:
        raise DeferredBulk(f"bulk file {size/1e6:.0f}MB > 200MB limit")
    data = http_get(url)
    if cfg.get("zip_member"):
        import zipfile
        zf = zipfile.ZipFile(io.BytesIO(data))
        data = zf.read(cfg["zip_member"])
    text = data.decode(cfg.get("encoding", "utf-8"), "replace")
    reader = csv.DictReader(io.StringIO(text), delimiter=cfg.get("delimiter", ","))
    all_rows = list(reader)
    rng.shuffle(all_rows)
    return all_rows[: want * 4], len(all_rows)


class DeferredBulk(Exception):
    pass


# ---------------------------------------------------------------------------
# Aggregate sampling (across counties) + spot-check
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


def fetch_aggregate(cfg, rng, want):
    counties = agg_counties(cfg)
    n_counties = min(6, len(counties))
    picks = rng.sample(counties, n_counties)
    per = want // n_counties + 2
    rows = []
    total = 0
    for c in picks:
        cw = f"{cfg['county_field']} = '{c}'"
        sub, n = fetch_arcgis(cfg, rng, per, extra_where=cw)
        rng.shuffle(sub)
        rows.extend(sub[:per])
        total += n
    return rows, total


def spotcheck(state, cfg, rng):
    """PROTOCOL2 composed-text spot-check: dump ~50 rows from 2+ counties for
    human inspection, plus variety heuristics."""
    counties = agg_counties(cfg)
    picks = rng.sample(counties, min(3, len(counties)))
    print(f"[{state}] spot-check counties: {picks}")
    all_lines = []
    for c in picks:
        sub, _ = fetch_arcgis(cfg, rng, 25, extra_where=f"{cfg['county_field']} = '{c}'")
        lines = [clean_part(r.get(cfg["addr_fields"][0])) for r in sub]
        lines = [l for l in lines if l][:25]
        all_lines.extend(lines)
        print(f"\n--- {c} ({len(lines)} lines) ---")
        for l in lines:
            print("   ", l)
    n = len(all_lines)
    if n:
        unit = sum(bool(re.search(r"\b(APT|UNIT|STE|SUITE|#|LOT|TRLR|FL|RM|BLDG)\b|#", l, re.I)) for l in all_lines)
        pob = sum(bool(re.search(r"\bP\.?\s?O\.?\s?BOX|\bBOX\s+\d|\bRR\s?\d|\bHC\s?\d", l, re.I)) for l in all_lines)
        punct = sum(bool(re.search(r"[.,#/&']", l)) for l in all_lines)
        mixed = sum(bool(re.search(r"[a-z]", l)) for l in all_lines)
        print(f"\nHeuristics over {n} lines: units/#: {unit} ({unit/n:.0%}), "
              f"PO/RR/HC: {pob} ({pob/n:.0%}), punctuation: {punct} ({punct/n:.0%}), "
              f"mixed-case: {mixed} ({mixed/n:.0%})")
        print("Perfectly uniform 'NUM STREET TYPE' with ~0% units/PO/quirks across "
              "counties => mark SUSPECT-COMPOSED and exclude.")


# ---------------------------------------------------------------------------
# Per-state driver
# ---------------------------------------------------------------------------

def ckpt_path(state):
    return CKPT_DIR / f"{state}.json"


def save_ckpt(state, payload):
    CKPT_DIR.mkdir(parents=True, exist_ok=True)
    with open(ckpt_path(state), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)


def fetch_state(state, cfg, excl, in_set, rng):
    if cfg.get("aggregate") and not cfg.get("spotcheck_passed"):
        return {"state": state, "status": "blocked-spotcheck",
                "note": "aggregate source; run --spotcheck and flip spotcheck_passed",
                "records": []}
    want = TARGET_PER_STATE
    try:
        if cfg["type"] == "socrata":
            rows, total = fetch_socrata(cfg, rng, want * 3)
        elif cfg["type"] == "arcgis":
            if cfg.get("aggregate"):
                rows, total = fetch_aggregate(cfg, rng, want * 2)
            else:
                rows, total = fetch_arcgis(cfg, rng, want * 3)
        elif cfg["type"] == "carto":
            rows, total = fetch_carto(cfg, rng, want * 3)
        elif cfg["type"] == "csv":
            rows, total = fetch_csv_url(cfg, rng, want)
        else:
            raise ValueError(f"unknown type {cfg['type']}")
    except DeferredBulk as e:
        return {"state": state, "status": "deferred-bulk", "note": str(e), "records": []}
    except Exception as e:  # noqa: BLE001
        return {"state": state, "status": "gap-unreachable", "note": str(e)[:300], "records": []}

    rng.shuffle(rows)
    records = []
    for row in rows:
        raw = build_raw(cfg, row)
        if not raw or not plausible(raw, cfg, row):
            continue
        nid = norm_identity(raw)
        if nid in excl or nid in in_set:
            continue
        in_set.add(nid)
        records.append({
            "raw": raw, "state": state, "source": cfg["source"],
            "dataset": cfg["dataset"], "fetched": FETCH_DATE,
        })
        if len(records) >= want:
            break
    status = "fetched" if len(records) >= 20 else ("thin" if records else "gap-unreachable")
    return {"state": state, "status": status, "note": f"dataset rows={total}",
            "records": records}


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
LEGAL_GAPS = {"CA": "Gov. Code §7928.205", "ID": "Idaho Code 74-120",
              "KY": "fee-based PVA rolls", "WY": "no bulk open source"}


def assemble():
    states = {}
    for p in sorted(CKPT_DIR.glob("*.json")):
        with open(p, encoding="utf-8") as f:
            states[p.stem] = json.load(f)
    # candidates.jsonl
    n_rec = 0
    with open(CANDIDATES_OUT, "w", encoding="utf-8") as f:
        for state in sorted(states):
            for rec in states[state].get("records", []):
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                n_rec += 1
    # manifest
    fetched_states = {s for s, d in states.items()
                      if d["status"] in ("fetched", "thin") and d.get("records")}
    lines = []
    lines.append("# Gold-2 Fetch Manifest\n")
    lines.append(f"Generated by `benchmark/fetch_gold2.py --assemble` on {FETCH_DATE}.\n")
    lines.append("Stratification note: the `state` field is the SOURCE state (the "
                 "jurisdiction whose roll the record came from). Owner mailing "
                 "addresses may point anywhere in the US; out-of-state mail "
                 "addresses are kept deliberately.\n")
    lines.append("PO Box / RR / HC records are valid and kept at natural frequency. "
                 "Dedupe enforced against eval/gold/candidates.jsonl, "
                 "eval/clean/clean.jsonl, and within gold-2 (normalized "
                 "uppercase-alphanumeric identity).\n")
    lines.append("## Per-state outcomes\n")
    lines.append("| State | Outcome | Records | Dataset | Note |")
    lines.append("|---|---|---|---|---|")
    all_states = sorted(set(sum(DIVISIONS.values(), [])))
    for s in all_states:
        if s in states:
            d = states[s]
            lines.append(f"| {s} | {d['status']} | {len(d.get('records', []))} | "
                         f"{d.get('dataset', states[s].get('records', [{}])[0].get('dataset', '') if states[s].get('records') else '')} | {d.get('note', '')} |")
        elif s in LEGAL_GAPS:
            lines.append(f"| {s} | gap-legal | 0 |  | {LEGAL_GAPS[s]} |")
        else:
            lines.append(f"| {s} | not-attempted | 0 |  |  |")
    lines.append("")
    lines.append("## Census-division coverage\n")
    lines.append("| Division | States fetched | Covered |")
    lines.append("|---|---|---|")
    covered = 0
    for div, members in DIVISIONS.items():
        got = sorted(fetched_states & set(members))
        ok = "YES" if got else "no"
        covered += bool(got)
        lines.append(f"| {div} | {', '.join(got) if got else '—'} | {ok} |")
    lines.append("")
    n_states = len(fetched_states - {"DC"})
    has_dc = "DC" in fetched_states
    floor = "MET" if (covered == 9 and n_states >= 40) else "NOT MET"
    lines.append(f"**Totals: {n_states} states{' + DC' if has_dc else ''}, "
                 f"{n_rec} records, {covered}/9 divisions. Pre-registered coverage "
                 f"floor (all 9 divisions + >=40 states): {floor}.** "
                 f"(DC is counted separately, not as a state.)")
    lines.append("")
    with open(MANIFEST_OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Wrote {n_rec} records for {n_states} states -> {CANDIDATES_OUT}")
    print(f"Manifest -> {MANIFEST_OUT}; divisions {covered}/9; floor {floor}")


# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--spotcheck", metavar="STATE")
    ap.add_argument("--fetch", metavar="STATE")
    ap.add_argument("--fetch-all", action="store_true")
    ap.add_argument("--assemble", action="store_true")
    ap.add_argument("--force", action="store_true", help="refetch even if checkpointed")
    args = ap.parse_args()

    rng = random.Random(SEED)

    if args.list:
        for s, c in sorted(CONFIG.items()):
            print(f"{s}: {c['type']:8s} {c['dataset']}")
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
        excl = load_exclusion_set()
        print(f"Exclusion set: {len(excl)} normalized identities (gold-1 + clean)")
        in_set = set()
        # seed in_set with already-checkpointed records so cross-state dedupe holds
        for p in CKPT_DIR.glob("*.json"):
            if p.stem in targets and not args.force:
                pass
            with open(p, encoding="utf-8") as f:
                for rec in json.load(f).get("records", []):
                    in_set.add(norm_identity(rec["raw"]))
        for s in targets:
            if ckpt_path(s).exists() and not args.force:
                print(f"[{s}] checkpoint exists, skipping (use --force to refetch)")
                continue
            print(f"[{s}] fetching ...")
            result = fetch_state(s, CONFIG[s], excl, in_set, rng)
            result["dataset"] = CONFIG[s]["dataset"]
            save_ckpt(s, result)
            print(f"[{s}] {result['status']}: {len(result['records'])} records "
                  f"({result.get('note','')})")

    if args.assemble:
        assemble()

    if not (args.list or args.spotcheck or targets or args.assemble):
        ap.print_help()


if __name__ == "__main__":
    main()
