"""Resolve the '<letter> <CITY>' ambiguity with Census evidence, per record.

"9 WALNUT LN S BARRINGTON IL 60010" has two readings: Walnut Ln South in
Barrington, or Walnut Ln in South Barrington. Both Barrington and South
Barrington are real places in ZIP 60010, so the string alone cannot decide it.

The Census geocoder returns the address already decomposed, including which
side the letter fell on:

    9 WALNUT LN S BARRINGTON   -> city 'S BARRINGTON', suffixDirection ''   -> PlaceName
    1305 Lake Shore Dr N BARR. -> city 'BARRINGTON',   suffixDirection 'N'  -> PostDirectional

So the answer differs record by record and must not be applied as a blanket
rule -- a uniform "it's always the city" would have mislabeled the genuine
post-directionals, and a uniform "it's always a directional" is the error the
models make today.

Writes eval/gold/citydir_evidence.json. Nothing here changes a label on its
own; it produces the evidence a human reviewer rules on.

Usage: python tools/census_classify_citydir.py [--limit N]
"""

import argparse
import json
import re
import time
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent.parent
G = ROOT / "eval" / "gold"
OUT = G / "citydir_evidence.json"
BASE = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"

# A single letter directly before a city-looking word, at the tail of the string.
PATTERN = re.compile(r"\b([NSEWL])\s+([A-Z][A-Za-z]{3,})\b")


def geocode(addr):
    q = urllib.parse.urlencode({"address": addr, "benchmark": "Public_AR_Current", "format": "json"})
    req = urllib.request.Request(f"{BASE}?{q}", headers={"User-Agent": "usaddr-eval/0.1"})
    with urllib.request.urlopen(req, timeout=90) as r:
        d = json.load(r)
    matches = d["result"]["addressMatches"]
    if not matches:
        return None
    m = matches[0]
    c = m["addressComponents"]
    return {
        "matched": m["matchedAddress"],
        "city": c.get("city"),
        "street": c.get("streetName"),
        "suffix_direction": c.get("suffixDirection"),
        "pre_direction": c.get("preDirection"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    gold = [json.loads(l) for l in open(G / "candidates.jsonl", encoding="utf-8-sig") if l.strip()]
    todo = []
    for r in gold:
        m = PATTERN.search(r["raw"])
        if m:
            todo.append((r["raw"], m.group(1).upper(), m.group(2).upper()))
    if args.limit:
        todo = todo[: args.limit]

    existing = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    verdicts = Counter()
    for i, (raw, letter, word) in enumerate(todo, 1):
        if raw in existing:
            verdicts[existing[raw]["reading"]] += 1
            continue
        try:
            ev = geocode(raw)
        except Exception as e:
            existing[raw] = {"reading": "error", "detail": str(e)[:120]}
            continue
        if not ev:
            existing[raw] = {"reading": "no_match", "letter": letter}
            verdicts["no_match"] += 1
        else:
            city = (ev.get("city") or "").upper()
            sufd = (ev.get("suffix_direction") or "").upper()
            # The letter belongs to the city when the geocoder's own city field
            # starts with it; it is a directional when the geocoder put it in
            # suffixDirection instead.
            if city.startswith(letter + " "):
                reading = "place"
            elif sufd == letter:
                reading = "directional"
            else:
                reading = "unclear"
            existing[raw] = {"reading": reading, "letter": letter, **ev}
            verdicts[reading] += 1
        if i % 10 == 0:
            OUT.write_text(json.dumps(existing, indent=1), encoding="utf-8")
            print(f"  {i}/{len(todo)} ...", flush=True)
        time.sleep(0.6)

    OUT.write_text(json.dumps(existing, indent=1), encoding="utf-8")
    print(f"\n{len(todo)} candidate records; Census readings: {dict(verdicts)}")
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
