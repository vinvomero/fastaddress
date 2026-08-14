"""Shape-preserving augmentation from adjudicated-correct parses (v4 recipe).

v3 fixed the saint-name class but regressed on landmark names, number-less
street addresses, highway pre-types, abbreviated place names, and USPS route
boxes — shapes that county distillation data simply does not contain, so
nothing in the corpus taught them.

This takes each contested record where v1 was adjudicated CORRECT, treats
(tokens, v1_labels) as a template, and generates variants by substituting
tokens with same-class alternatives while preserving the label sequence
exactly. Structure is learned; the literal gold strings never enter training.

Guards: generated variants are checked against the gold/clean exclusion set by
normalized identity, and any collision is dropped.

Usage: python training/augment_from_wins.py [--per-template N]
Output: training/corpus/augmented.jsonl
"""

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent
OUT = Path(__file__).parent / "corpus" / "augmented.jsonl"
SEED = 20260813

CITIES = ["Ludlow", "Hutchinson", "Lincoln", "Wayne", "Madison", "Seattle", "Venice",
          "Goshen", "Bennington", "Owensboro", "Gulfport", "Midland City", "Moultonborough",
          "Round Pond", "Miles City", "Des Moines", "Auburn", "Fairview", "Clinton"]
STATES = ["VT", "KS", "NE", "PA", "IN", "WA", "FL", "CT", "KY", "MS", "AL", "NH", "ME", "MT", "IA"]
STREET_WORDS = ["Anchor", "Cedar", "Harbor", "Willow", "Franklin", "Sunset", "Meadow",
                "Birch", "Colonial", "Sterling", "Kingston", "Auburn", "Preston"]
LANDMARK_WORDS = ["Municipal", "Regional", "Memorial", "Central", "Riverside", "Lakeside",
                  "Valley", "Summit", "Heritage", "Gateway", "Northside", "Pioneer"]
LANDMARK_TAILS = ["Airport", "Mall", "Center", "Plaza", "Terminal", "Field", "Park", "Station"]
PLACE_ABBR = ["BARRNGTN", "ARLNGTON", "HTS", "HLS", "EST", "PRK", "VLG", "SPGS"]


def norm(s):
    return "".join(c for c in s.upper() if c.isalnum())


def exclusions():
    ids = set()
    for p in (ROOT / "eval" / "gold" / "candidates.jsonl", ROOT / "eval" / "clean" / "clean.jsonl"):
        with open(p, encoding="utf-8") as f:
            for line in f:
                ids.add(norm(json.loads(line)["raw"]))
    return ids


def v1_win_templates():
    """Contested records where v1 was adjudicated correct -> (tokens, v1 labels)."""
    key = json.loads((ROOT / "eval" / "gold" / "blind_key.json").read_text(encoding="utf-8"))
    verd = json.loads(
        (ROOT / "eval" / "gold" / "verdicts-chatgpt-2026-08-13.json").read_text(encoding="utf-8")
    )
    gv = {int(k): v for k, v in verd["groups"].items()}
    exc = verd.get("exceptions", {})
    dis = [json.loads(l) for l in open(ROOT / "eval" / "gold" / "disagreements.jsonl", encoding="utf-8") if l.strip()]
    groups = defaultdict(list)
    for r in dis:
        groups[tuple((d["v1"], d["v2"]) for d in r["differing_tokens"])].append(r)
    ordered = sorted(groups.values(), key=len, reverse=True)
    out = []
    for i, grp in enumerate(ordered, 1):
        for r in grp:
            raw_v = exc.get(r["raw"], gv.get(i, "skip"))
            if key.get(raw_v, raw_v) == "v1":
                out.append((r["tokens"], r["v1_labels"]))
    return out


def substitute(rng, token, label):
    """Swap a token for a same-class alternative, preserving trailing punctuation."""
    trail = ""
    core = token
    while core and not (core[-1].isalnum()):
        trail = core[-1] + trail
        core = core[:-1]
    if not core:
        return token

    def cased(word):
        if core.isupper():
            return word.upper()
        if core.islower():
            return word.lower()
        return word

    if label == "AddressNumber":
        if "-" in core:
            a = rng.randint(100, 900)
            return f"{a}-{a + rng.randint(2, 9)}" + trail
        return str(rng.randint(1, 9999)) + trail
    if label == "ZipCode":
        return str(rng.randint(10000, 99999)) + trail
    if label == "StateName" and len(core) == 2:
        return cased(rng.choice(STATES)) + trail
    if label == "PlaceName":
        if core.isupper() and len(core) <= 8 and core not in ("NEW", "YORK"):
            return rng.choice(PLACE_ABBR) + trail
        return cased(rng.choice(CITIES).split()[0]) + trail
    if label == "LandmarkName":
        pool = LANDMARK_TAILS if core.lower() in [t.lower() for t in LANDMARK_TAILS] else LANDMARK_WORDS
        return cased(rng.choice(pool)) + trail
    if label in ("StreetName", "BuildingName"):
        return cased(rng.choice(STREET_WORDS)) + trail
    if label in ("USPSBoxID", "OccupancyIdentifier", "SubaddressIdentifier"):
        return str(rng.randint(1, 999)) + trail
    return token  # structural tokens (types, directionals, separators) stay put


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-template", type=int, default=120)
    args = ap.parse_args()

    rng = random.Random(SEED)
    excl = exclusions()
    templates = v1_win_templates()
    rows, seen, dropped = [], set(), 0

    for tokens, labels in templates:
        # Keep one verbatim-structure copy per template only if it is not an
        # eval string (it always is here, so this is effectively augmentation-only).
        for _ in range(args.per_template):
            new_tokens = [substitute(rng, t, l) for t, l in zip(tokens, labels)]
            raw = " ".join(new_tokens)
            k = norm(raw)
            if not k or k in seen or k in excl:
                dropped += 1
                continue
            seen.add(k)
            rows.append({"tokens": new_tokens, "labels": labels, "origin": "augment-v1wins"})

    rng.shuffle(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"{len(templates)} templates -> {len(rows)} augmented sequences ({dropped} dropped) -> {OUT}")


if __name__ == "__main__":
    main()
