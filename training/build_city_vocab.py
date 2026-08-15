"""National city-name vocabulary from Census PLACE files.

WHY
---
The v23 error-class generators used an invented city list, and the national
divergence scan showed the cost: taught that "New Jersey" is a state, the model
began reading "New Orleans" as one; taught that "S" before BARRINGTON is a city
prefix, it began reading "South Fulton" as a directional. The counterweights
need the real national distribution of confusable city names, and the Census
publishes exactly that: every incorporated place name in the country.

Extracts from all state PLACE files:
  confusable_start  cities whose FIRST word is a direction/state-word/box-word
                    ("New Orleans", "South Fulton", "West Jordan", "Box Elder")
  confusable_end    cities whose LAST word looks like a street type or
                    directional ("Tinley Park", "Hazel Crest", "Oak Lawn")
  two_word          other multi-word cities, for general balance

Cache lives OUTSIDE OneDrive (it breaks large file churn).

Usage: python training/build_city_vocab.py
Writes training/vocab_cities.json
"""

import io
import json
import re
import urllib.request
import zipfile
from pathlib import Path

import shapefile

OUT = Path(__file__).parent / "vocab_cities.json"
CACHE = Path("C:/cargo-target/us-address-parser/place_cache")
BASE = "https://www2.census.gov/geo/tiger/TIGER2024/PLACE"

STATE_FIPS = [
    "01", "02", "04", "05", "06", "08", "09", "10", "11", "12", "13", "15", "16",
    "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29",
    "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42",
    "44", "45", "46", "47", "48", "49", "50", "51", "53", "54", "55", "56",
]

FIPS_ABBR = {
    "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO",
    "09": "CT", "10": "DE", "11": "DC", "12": "FL", "13": "GA", "15": "HI",
    "16": "ID", "17": "IL", "18": "IN", "19": "IA", "20": "KS", "21": "KY",
    "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN",
    "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH",
    "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND", "39": "OH",
    "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD",
    "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA",
    "54": "WV", "55": "WI", "56": "WY",
}

CONFUSABLE_START = {
    "new", "north", "south", "east", "west", "lake", "box", "saint", "st",
    "mount", "mt", "port", "grand", "park", "fort", "ft",
}
CONFUSABLE_END = {
    "park", "heights", "hills", "grove", "beach", "city", "falls", "springs",
    "crest", "point", "square", "gardens", "shores", "lawn", "ridge", "creek",
    "junction", "center", "corners", "lake", "valley", "view", "acres",
}


def fetch(fips):
    dest = CACHE / f"place_{fips}.zip"
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    url = f"{BASE}/tl_2024_{fips}_place.zip"
    req = urllib.request.Request(url, headers={"User-Agent": "city-vocab/0.1"})
    with urllib.request.urlopen(req, timeout=600) as r, open(dest, "wb") as f:
        f.write(r.read())
    return dest


def names_from(zip_path):
    z = zipfile.ZipFile(zip_path)
    dbf = [n for n in z.namelist() if n.endswith(".dbf")][0]
    sf = shapefile.Reader(dbf=io.BytesIO(z.read(dbf)))
    for rec in sf.records():
        yield (rec.as_dict().get("NAME") or "").strip()


def main():
    start, end, two, plain = [], [], [], []
    seen = set()
    for fips in STATE_FIPS:
        st = FIPS_ABBR[fips]
        n_st = 0
        for name in names_from(fetch(fips)):
            # Keep plain-alpha names only, so usaddress.tokenize round-trips
            # exactly (hyphens/apostrophes tokenize differently than .split()).
            if not re.fullmatch(r"[A-Za-z ]+", name):
                continue
            words = name.split()
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)
            n_st += 1
            entry = [name, st]
            if len(words) >= 2 and words[0].lower() in CONFUSABLE_START:
                start.append(entry)
            elif len(words) >= 2 and words[-1].lower() in CONFUSABLE_END:
                end.append(entry)
            elif len(words) == 2:
                two.append(entry)
            elif len(words) == 1 and len(name) >= 5:
                plain.append(entry)
        print(f"  {st}: {n_st} usable place names", flush=True)

    # Plain single-word cities (Wichita, Billings, Seattle) are the
    # counterweight the v24 scan showed missing: a genuine post-directional
    # right before one of these must stay a directional.
    vocab = {"confusable_start": start, "confusable_end": end, "two_word": two,
             "plain": plain[:6000]}
    OUT.write_text(json.dumps(vocab), encoding="utf-8")
    print(f"\nconfusable_start {len(start)}  confusable_end {len(end)}  two_word {len(two)}")
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
