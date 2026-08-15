"""U2: national vocabulary inventories from TIGER, at the real granularity.

PLACE files are per-state; FEATNAMES files are per-county (~3,200 nationally).
This sweep enumerates every county FIPS from the national TIGER COUNTY file,
then runs a RESUMABLE per-county FEATNAMES fetch+extract with a checkpoint
every 50 counties, accumulating:

  street_type_pre    PRETYPABRV frequency table (Camino/Cmo/Rue/... as TIGER
                     actually abbreviates them)
  street_type_suf    SUFTYPABRV frequency table (Pike/Wynd/Xing/... rarities)
  qualifiers         PREQUALABR/SUFQUALABR forms
  name_lead_words    leading words of street NAMEs (route designators surface here)
  cities             ALL multi-word place names, no word-count cap (the 2-word
                     cap caused three failure rounds), from per-state PLACE files

Partial sweeps are recorded as partial in the manifest and never presented as
national. Cache and checkpoints live outside OneDrive.

Usage:
  python training/build_vocab_inventories.py --sweep     (long; resumable)
  python training/build_vocab_inventories.py --finalize  (write inventories json)
"""

import argparse
import collections
import io
import json
import re
import urllib.request
import zipfile
from pathlib import Path

import shapefile

CACHE = Path("C:/cargo-target/us-address-parser/tiger_national_cache")
CKPT = CACHE / "sweep_checkpoint.json"
OUT = Path(__file__).parent / "vocab_inventories.json"
MANIFEST = Path(__file__).parent / "INVENTORY_MANIFEST.json"
BASE = "https://www2.census.gov/geo/tiger/TIGER2024"

STATE_FIPS = ["01","02","04","05","06","08","09","10","11","12","13","15","16","17","18","19",
              "20","21","22","23","24","25","26","27","28","29","30","31","32","33","34","35",
              "36","37","38","39","40","41","42","44","45","46","47","48","49","50","51","53",
              "54","55","56","72"]


def fetch(url, dest):
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "vocab-inventory/0.1"})
    with urllib.request.urlopen(req, timeout=600) as r, open(dest, "wb") as f:
        f.write(r.read())
    return dest


def read_dbf(zip_path):
    z = zipfile.ZipFile(zip_path)
    name = [n for n in z.namelist() if n.endswith(".dbf")][0]
    sf = shapefile.Reader(dbf=io.BytesIO(z.read(name)))
    for rec in sf.records():
        yield rec.as_dict()


def enumerate_counties():
    dest = CACHE / "tl_2024_us_county.zip"
    fetch(f"{BASE}/COUNTY/tl_2024_us_county.zip", dest)
    fips = sorted(d["GEOID"] for d in read_dbf(dest))
    print(f"national county enumeration: {len(fips)} counties", flush=True)
    return fips


def load_ckpt():
    if CKPT.exists():
        return json.loads(CKPT.read_text(encoding="utf-8"))
    return {"done": [], "missing": [],
            "street_type_pre": {}, "street_type_suf": {},
            "qualifiers": {}, "name_lead_words": {}}


def save_ckpt(state):
    CKPT.parent.mkdir(parents=True, exist_ok=True)
    CKPT.write_text(json.dumps(state), encoding="utf-8")


def sweep():
    fips = enumerate_counties()
    st = load_ckpt()
    done = set(st["done"])
    counters = {k: collections.Counter(st[k]) for k in
                ("street_type_pre", "street_type_suf", "qualifiers", "name_lead_words")}
    todo = [f for f in fips if f not in done and f not in set(st["missing"])]
    print(f"{len(done)} done, {len(todo)} to go", flush=True)
    for i, cf in enumerate(todo, 1):
        dest = CACHE / "featnames" / f"tl_2024_{cf}_featnames.zip"
        try:
            fetch(f"{BASE}/FEATNAMES/tl_2024_{cf}_featnames.zip", dest)
            for d in read_dbf(dest):
                pre = (d.get("PRETYPABRV") or "").strip()
                suf = (d.get("SUFTYPABRV") or "").strip()
                if pre:
                    counters["street_type_pre"][pre] += 1
                if suf:
                    counters["street_type_suf"][suf] += 1
                for q in ("PREQUALABR", "SUFQUALABR"):
                    v = (d.get(q) or "").strip()
                    if v:
                        counters["qualifiers"][v] += 1
                name = (d.get("NAME") or "").strip()
                if name and " " in name:
                    lead = name.split()[0]
                    if re.fullmatch(r"[A-Za-z.-]+", lead):
                        counters["name_lead_words"][lead] += 1
            done.add(cf)
        except Exception as e:
            st["missing"].append(cf)
            print(f"  MISS {cf}: {type(e).__name__}", flush=True)
        if i % 50 == 0 or i == len(todo):
            st["done"] = sorted(done)
            for k in counters:
                st[k] = dict(counters[k])
            save_ckpt(st)
            print(f"  checkpoint: {len(done)}/{len(fips)} counties", flush=True)
    print("sweep complete", flush=True)


def finalize():
    st = load_ckpt()
    fips = enumerate_counties()
    coverage = len(st["done"]) / len(fips)

    # Cities: all multi-word place names, no cap, plain-alpha (tokenizer round-trip
    # and Census-bookkeeping filtering happen downstream, same rules as before).
    cities = []
    seen = set()
    for sf_ in STATE_FIPS:
        dest = CACHE / "place" / f"tl_2024_{sf_}_place.zip"
        try:
            fetch(f"{BASE}/PLACE/tl_2024_{sf_}_place.zip", dest)
        except Exception:
            continue
        for d in read_dbf(dest):
            name = (d.get("NAME") or "").strip()
            if re.fullmatch(r"[A-Za-z ]+", name) and " " in name and name.lower() not in seen:
                seen.add(name.lower())
                cities.append([name, sf_])

    inv = {
        "street_type_pre": st["street_type_pre"],
        "street_type_suf": st["street_type_suf"],
        "qualifiers": st["qualifiers"],
        "name_lead_words": {k: v for k, v in st["name_lead_words"].items() if v >= 5},
        "cities_multiword": cities,
    }
    OUT.write_text(json.dumps(inv), encoding="utf-8")
    manifest = {
        "counties_swept": len(st["done"]),
        "counties_total": len(fips),
        "coverage": round(coverage, 4),
        "national": coverage >= 0.99,
        "missing": st["missing"],
        "source": "US Census Bureau TIGER/Line 2024 (public domain)",
        "cities_multiword": len(cities),
        "distinct_pre_types": len(st["street_type_pre"]),
        "distinct_suf_types": len(st["street_type_suf"]),
    }
    MANIFEST.write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print(json.dumps(manifest, indent=1)[:600])
    if not manifest["national"]:
        print("WARNING: partial sweep — inventories are NOT national; manifest says so.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--finalize", action="store_true")
    a = ap.parse_args()
    if a.sweep:
        sweep()
    if a.finalize:
        finalize()
    if not (a.sweep or a.finalize):
        print("pass --sweep and/or --finalize")
