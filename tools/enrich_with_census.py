"""Attach US Census geocoder evidence to contested adjudication records.

The Census geocoder is free, key-less, US-only, and PUBLIC DOMAIN — unlike
Google's Address Validation API, whose terms forbid redistributing results,
which would make a published gold set unauditable.

Important scope limits (stated in the doc this feeds):
  * The geocoder answers "is this a real address and what is its canonical
    form", NOT "which of usaddress's 26 labels does each token carry". Its
    component names do not map onto the finer distinctions in our schema
    (pre- vs post-directional, LandmarkName vs BuildingName, USPS box groups).
  * It abstains on genuinely messy input — precisely the cases that are hard
    to adjudicate.

So this is EVIDENCE for the adjudicator, never a label source.

Usage: python tools/enrich_with_census.py
Output: eval/gold/census_evidence.json  (raw, cached, redistributable)
"""

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent.parent
SRC = ROOT / "eval" / "gold" / "disagreements.jsonl"
OUT = ROOT / "eval" / "gold" / "census_evidence.json"
BASE = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress"


def lookup(addr):
    url = BASE + "?" + urllib.parse.urlencode(
        {"address": addr, "benchmark": "Public_AR_Current",
         "vintage": "Current_Current", "format": "json"}
    )
    try:
        with urllib.request.urlopen(url, timeout=45) as r:
            data = json.load(r)
    except Exception as e:
        return {"status": "error", "detail": str(e)[:120]}
    matches = data.get("result", {}).get("addressMatches", [])
    if not matches:
        return {"status": "no_match"}
    m = matches[0]
    c = m.get("addressComponents", {})
    return {
        "status": "match",
        "matched": m.get("matchedAddress"),
        "house_number_range": f"{c.get('fromAddress')}-{c.get('toAddress')}",
        "street": c.get("streetName"),
        "pre_type": c.get("preType"),
        "suffix_type": c.get("suffixType"),
        "pre_direction": c.get("preDirection"),
        "suffix_direction": c.get("suffixDirection"),
        "city": c.get("city"),
        "state": c.get("state"),
        "zip": c.get("zip"),
    }


def main():
    rows = [json.loads(l) for l in open(SRC, encoding="utf-8") if l.strip()]
    seen, evidence = set(), {}
    for r in rows:
        raw = r["raw"]
        if raw in seen:
            continue
        seen.add(raw)
        evidence[raw] = lookup(raw)
        time.sleep(0.4)  # be polite to a free public service
    OUT.write_text(json.dumps(evidence, indent=1), encoding="utf-8")
    matched = sum(1 for v in evidence.values() if v["status"] == "match")
    print(f"{len(evidence)} addresses queried; {matched} matched, "
          f"{len(evidence) - matched} no-match/error -> {OUT}")


if __name__ == "__main__":
    main()
