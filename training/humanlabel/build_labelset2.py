"""Batch 2: target the failing classes by pattern, not by confidence.

Batch 1 ordered by model confidence and caught cases the model was unsure
about. The GitHub accuracy bugs are the opposite: the model is confidently
wrong ("La Quinta" read as Louisiana). A confidence filter misses those. So
this batch selects by CLASS PATTERN, drawn from the same disjoint real pool,
oversampling exactly the buckets that fail on gold-2c and that people filed
usaddress issues about.

Classes and the issues they map to:
  multiword_place   two-word+ cities (La Selva Beach, Belle Glade)  -> #406 #302 #330
  stateish_city     city starts LA/SAN/MT/NORTH/... (La Quinta)     -> #358 #294 #301 #406
  route             FM/RM/County Rd/State Hwy in the street          -> #315 #364
  directional       street starts or ends with a directional        -> #295 #317
  recipient         c/o, trustee, LLC, name-first lines              -> #393
  abbrev_city       abbreviated leading city word (S Barrington)     -> our adjudicated fails
  suffix_present    street carries its suffix type                   -> the decisive gold-2c class

Output: training/humanlabel/candidates_batch2.jsonl (ordered by class),
        training/humanlabel/BATCH2_MANIFEST.json,
        and a fill-out CSV emitted by make_label_csv2.py.
"""
import collections
import glob
import gzip
import json
import os
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE = "C:/cargo-target/us-address-parser/realtext_cache/checkpoints"
OUT = Path(__file__).parent / "candidates_batch2.jsonl"
MANIFEST = Path(__file__).parent / "BATCH2_MANIFEST.json"
SEED = 20260825
PER_CLASS = 340   # target per bucket; rare buckets take all they have

import fastaddress

DIRECTIONALS = {"N", "S", "E", "W", "NE", "NW", "SE", "SW",
                "NORTH", "SOUTH", "EAST", "WEST"}
STATEISH_LEADS = {"LA", "SAN", "SANTA", "MT", "MOUNT", "FORT", "FT", "LAKE", "LK",
                  "BELLE", "NORTH", "SOUTH", "EAST", "WEST", "NEW", "DE", "EL", "LOS", "LAS"}
ABBREV_LEADS = {"S", "N", "E", "W", "MT", "LK", "FT", "SO", "NO", "STE", "STA"}
ROUTE_WORDS = {"FM", "RM", "FARM", "COUNTY", "CO", "STATE", "HWY", "HIGHWAY",
               "ROUTE", "RTE", "SR", "US", "CNTY", "TRUNK", "RANCH"}
SUFFIX_WORDS = {"ST", "AVE", "RD", "DR", "LN", "CT", "BLVD", "WAY", "PL", "TER",
                "CIR", "TRL", "PKWY", "HWY", "LOOP", "PATH", "PT", "SQ", "RUN",
                "STREET", "AVENUE", "ROAD", "DRIVE", "LANE", "COURT", "BOULEVARD",
                "PLACE", "CIRCLE", "TRAIL", "PARKWAY", "TERRACE", "CROSSING", "COVE"}


def norm(s):
    return " ".join("".join(c for c in t.upper() if c.isalnum()) for t in s.split())


def reconstruct(row):
    lines = [l.strip() for l in row.get("lines", []) if l and l.strip()]
    tail = " ".join(x for x in [row.get("city", ""), row.get("st", ""), row.get("zip", "")] if x)
    return " ".join(lines + ([tail] if tail else [])).strip(), lines, row.get("city", "")


def classify(raw, lines, city):
    """Return every target class this record matches (a record can hit several)."""
    hits = set()
    citw = city.upper().split()
    street = " ".join(lines).upper()
    stoks = street.split()
    # recipient: more than one line, or a first line that does not start with a number/box
    if len(lines) > 1 or (lines and not re.match(r"^\s*(\d|P\.?\s*O|PO|RR|HC|BOX)", lines[0], re.I)):
        hits.add("recipient")
    if len(citw) >= 2:
        hits.add("multiword_place")
    if citw and citw[0] in STATEISH_LEADS:
        hits.add("stateish_city")
    if citw and citw[0] in ABBREV_LEADS and len(citw[0]) <= 2:
        hits.add("abbrev_city")
    if any(w in ROUTE_WORDS for w in stoks[:3]):
        hits.add("route")
    if any(w in DIRECTIONALS for w in stoks):
        hits.add("directional")
    if any(w in SUFFIX_WORDS for w in stoks):
        hits.add("suffix_present")
    return hits


def main():
    eval_ids = set()
    for f in ["eval/gold/candidates.jsonl", "eval/gold2/candidates.jsonl",
              "eval/gold2b/candidates.jsonl", "eval/gold2c/candidates.jsonl"]:
        p = ROOT / f
        if p.exists():
            for l in open(p, encoding="utf-8-sig"):
                if l.strip():
                    eval_ids.add(norm(json.loads(l)["raw"]))
    # also disjoint from batch 1
    b1 = Path(__file__).parent / "candidates_for_labeling.jsonl"
    if b1.exists():
        for l in open(b1, encoding="utf-8"):
            if l.strip():
                eval_ids.add(norm(json.loads(l)["raw"]))

    rng = random.Random(SEED)
    buckets = collections.defaultdict(list)
    seen = set()
    for f in sorted(glob.glob(f"{CACHE}/*.json.gz")):
        st = os.path.basename(f)[:-8]
        with gzip.open(f, "rt", encoding="utf-8") as fh:
            d = json.load(fh)
        rows = d.get("rows", []) if isinstance(d, dict) else d
        for r in rows:
            if not isinstance(r, dict):
                continue
            raw, lines, city = reconstruct(r)
            if len(raw.split()) < 3:
                continue
            nid = norm(raw)
            if nid in eval_ids or nid in seen:
                continue
            seen.add(nid)
            for cls in classify(raw, lines, city):
                buckets[cls].append((raw, st))

    # stratified draw: PER_CLASS from each bucket, assigning each raw to exactly
    # one class (its rarest matching bucket) so the total is deduplicated.
    order = ["recipient", "abbrev_city", "route", "stateish_city", "directional",
             "multiword_place", "suffix_present"]  # rarest-first priority
    assigned, used = collections.defaultdict(list), set()
    for cls in order:
        pool = [x for x in buckets[cls] if norm(x[0]) not in used]
        rng.shuffle(pool)
        take = pool[:PER_CLASS]
        for raw, stt in take:
            used.add(norm(raw))
            assigned[cls].append((raw, stt))

    scored = []
    for cls in order:
        for raw, stt in assigned[cls]:
            try:
                triples = fastaddress.parse_with_confidence(raw)
            except Exception:
                continue
            if not triples:
                continue
            scored.append({
                "raw": raw, "state": stt, "target_class": cls,
                "prelabel_tokens": [t for t, _, _ in triples],
                "prelabel_labels": [l for _, l, _ in triples],
                "min_confidence": round(min(c for _, _, c in triples), 5),
            })
    with open(OUT, "w", encoding="utf-8") as fh:
        for r in scored:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    mix = collections.Counter(r["target_class"] for r in scored)
    avail = {k: len(v) for k, v in buckets.items()}
    MANIFEST.write_text(json.dumps({
        "built": "2026-08-18", "seed": SEED, "records": len(scored),
        "source": "realtext_cache raw pool, no new fetch",
        "disjoint_from": ["gold-1", "gold-2", "gold-2b", "gold-2c", "humanlabel batch 1"],
        "selection": "by target class (confidently-wrong bugs the model is sure about), "
                     "not by confidence",
        "class_mix": dict(mix), "class_available_in_pool": avail,
        "maps_to_issues": {"multiword_place": "#406 #302 #330", "stateish_city": "#358 #294 #301",
                           "route": "#315 #364", "directional": "#295 #317", "recipient": "#393",
                           "abbrev_city": "adjudicated S-BARRINGTON fails",
                           "suffix_present": "the decisive gold-2c class"},
    }, indent=1), encoding="utf-8")
    print(f"wrote {len(scored)} candidates -> {OUT}")
    print("class mix:", dict(mix))


if __name__ == "__main__":
    main()
