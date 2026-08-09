"""Fetch address samples from public county open-data APIs.

Reproducible data pull for the pre-build gate benchmark (requirements R5).
Each source writes benchmark/data/<county>.csv with columns:
  raw_address  - the single-line address string as a tax-roll consumer would parse it
  source_zip   - the zip code the source record carries (used as a weak ground-truth check)

Sources (all public, no API key required for these volumes):
  nyc       - NYC PLUTO (data.cityofnewyork.us, 64uk-42ks)
  cook      - Cook County Assessor Parcel Addresses (datacatalog.cookcountyil.gov, 3723-97qp)
  allegheny - Allegheny County Property Assessments (data.wprdc.org CKAN datastore)
"""

import csv
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

LIMIT = 5000
DATA_DIR = Path(__file__).parent / "data"

BOROUGH_CITY = {"MN": "NEW YORK", "BX": "BRONX", "BK": "BROOKLYN", "QN": "QUEENS", "SI": "STATEN ISLAND"}


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "address-benchmark/0.1"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.load(resp)


def fetch_nyc():
    params = urllib.parse.quote(
        "$select=address,zipcode,borough&$where=address IS NOT NULL AND zipcode IS NOT NULL"
        f"&$limit={LIMIT}&$order=bbl", safe="$=&,()' "
    ).replace(" ", "%20")
    rows = get_json(f"https://data.cityofnewyork.us/resource/64uk-42ks.json?{params}")
    out = []
    for r in rows:
        city = BOROUGH_CITY.get(r.get("borough", ""), "NEW YORK")
        out.append((f"{r['address']} {city} NY {r['zipcode']}", r["zipcode"]))
    return out


def fetch_cook():
    for year in ("2024", "2023", "2022"):
        params = urllib.parse.quote(
            "$select=prop_address_full,prop_address_city_name,prop_address_state,prop_address_zipcode_1"
            f"&$where=year='{year}' AND prop_address_full IS NOT NULL AND prop_address_zipcode_1 IS NOT NULL"
            f"&$limit={LIMIT}&$order=pin", safe="$=&,()' "
        ).replace(" ", "%20")
        rows = get_json(f"https://datacatalog.cookcountyil.gov/resource/3723-97qp.json?{params}")
        if rows:
            out = []
            for r in rows:
                line = " ".join(
                    p for p in (
                        (r.get("prop_address_full") or "").strip(),
                        (r.get("prop_address_city_name") or "").strip(),
                        (r.get("prop_address_state") or "").strip(),
                        (r.get("prop_address_zipcode_1") or "").strip(),
                    ) if p
                )
                zipc = (r.get("prop_address_zipcode_1") or "").strip()
                if line and zipc:
                    out.append((line, zipc))
            return out
    return []


def fetch_cook_mail():
    """Owner mailing addresses — genuinely messy free-text (PO boxes, c/o lines, out-of-state)."""
    params = urllib.parse.quote(
        "$select=mail_address_full,mail_address_city_name,mail_address_state,mail_address_zipcode_1"
        "&$where=year='2024' AND mail_address_full IS NOT NULL AND mail_address_zipcode_1 IS NOT NULL"
        f"&$limit={LIMIT}&$order=pin", safe="$=&,()' "
    ).replace(" ", "%20")
    rows = get_json(f"https://datacatalog.cookcountyil.gov/resource/3723-97qp.json?{params}")
    out = []
    for r in rows:
        line = " ".join(
            p for p in (
                (r.get("mail_address_full") or "").strip(),
                (r.get("mail_address_city_name") or "").strip(),
                (r.get("mail_address_state") or "").strip(),
                (r.get("mail_address_zipcode_1") or "").strip(),
            ) if p
        )
        zipc = (r.get("mail_address_zipcode_1") or "").strip()
        if line and zipc:
            out.append((line, zipc))
    return out


def fetch_allegheny():
    url = (
        "https://data.wprdc.org/api/3/action/datastore_search"
        f"?resource_id=65855e14-549e-4992-b5be-d629afc676fa&limit={LIMIT}"
    )
    records = get_json(url)["result"]["records"]
    out = []
    for r in records:
        parts = [
            (r.get("PROPERTYHOUSENUM") or "").strip(),
            (r.get("PROPERTYFRACTION") or "").strip(),
            (r.get("PROPERTYADDRESS") or "").strip(),
            (r.get("PROPERTYUNIT") or "").strip(),
            (r.get("PROPERTYCITY") or "").strip(),
            (r.get("PROPERTYSTATE") or "").strip(),
            (r.get("PROPERTYZIP") or "").strip(),
        ]
        zipc = parts[-1]
        line = " ".join(p for p in parts if p)
        if line and zipc:
            out.append((line, zipc))
    return out


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for name, fn in (("nyc", fetch_nyc), ("cook", fetch_cook), ("cook_mail", fetch_cook_mail), ("allegheny", fetch_allegheny)):
        rows = fn()
        path = DATA_DIR / f"{name}.csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["raw_address", "source_zip"])
            w.writerows(rows)
        print(f"{name}: {len(rows)} rows -> {path}")
    if not rows:
        sys.exit(1)


if __name__ == "__main__":
    main()
