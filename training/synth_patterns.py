"""Pattern-targeted synthetic training data (findings-report recipe 1).

The v2 round-1 clean-gate failures were all rare postal patterns that county
distant-supervision never contains: state/farm/county routes, HC-RR rural
boxes, business-route highways, zip-less state tails, and type-less occupancy
numbers. This generates labeled sequences for exactly those classes.

Labels follow the usaddress schema and the conventions in upstream's
labeled.xml. Deterministic under SEED.

Usage: python training/synth_patterns.py  ->  training/corpus/synth.jsonl
"""

import json
import random
from pathlib import Path

OUT = Path(__file__).parent / "corpus" / "synth.jsonl"
SEED = 20260813

STREETS = ["Main", "Oak", "Maple", "Washington", "Cedar", "Lincoln", "Park", "Hill",
           "Ridge", "Lake", "River", "Church", "Union", "Center", "Spring", "Franklin"]
TYPES = ["St", "Ave", "Rd", "Dr", "Ln", "Blvd", "Ct", "Way", "Pl", "Trl", "Hwy"]
CITIES = ["Leonard", "Marion", "Murrells Inlet", "Kenai", "Anamosa", "Springfield",
          "Clinton", "Fairview", "Georgetown", "Salem", "Madison", "Auburn"]
STATE_ABBR = ["TX", "KS", "SC", "IA", "IL", "PA", "NY", "MO", "OK", "AR", "AK", "NC"]
STATE_FULL = ["Texas", "Kansas", "South Carolina", "Iowa", "Illinois", "Missouri",
              "Oklahoma", "Arkansas", "North Carolina", "Alaska", "New Mexico"]
ROUTE_TYPES = ["PR", "FM", "CR", "RR", "SR", "TR"]  # state/farm/county/ranch routes
OCC_TYPES = ["Apt", "Unit", "Ste", "#"]


def seq(pairs):
    """pairs: [(token, label)] -> record"""
    return {"tokens": [t for t, _ in pairs], "labels": [l for _, l in pairs], "origin": "synth"}


def city_tail(rng, with_zip=True, full_state=False, comma=True):
    city = rng.choice(CITIES)
    out = []
    toks = city.split()
    for i, t in enumerate(toks):
        last = i == len(toks) - 1
        out.append((t + ("," if last and comma else ""), "PlaceName"))
    if full_state:
        st = rng.choice(STATE_FULL)
        for t in st.split():
            out.append((t, "StateName"))
    else:
        out.append((rng.choice(STATE_ABBR), "StateName"))
    if with_zip:
        out.append((str(rng.randint(10000, 99999)), "ZipCode"))
    return out


def gen_route(rng):
    """'519 PR 462 Leonard, TX 75452' — route type is StreetNamePreType."""
    pairs = [(str(rng.randint(100, 9999)), "AddressNumber"),
             (rng.choice(ROUTE_TYPES), "StreetNamePreType"),
             (str(rng.randint(1, 4000)), "StreetName")]
    pairs += city_tail(rng, with_zip=rng.random() < 0.85)
    return seq(pairs)


def gen_hc_rr_box(rng):
    """'HC R 32 Box # e3' — HC/RR group type + id, then box."""
    group = rng.choice(["HC", "RR", "HCR"])
    pairs = [(group, "USPSBoxGroupType")]
    if rng.random() < 0.5:
        pairs.append((rng.choice(["R", "C"]), "USPSBoxGroupType"))
    pairs.append((str(rng.randint(1, 99)), "USPSBoxGroupID"))
    pairs.append(("Box", "USPSBoxType"))
    # Convention (verified against upstream gold): a '#' preceding the number is
    # part of the IDENTIFIER, not the type.
    if rng.random() < 0.4:
        pairs.append(("#", "USPSBoxID"))
    pairs.append((rng.choice(["", "e", "a"]) + str(rng.randint(1, 400)), "USPSBoxID"))
    if rng.random() < 0.6:
        pairs += city_tail(rng)
    return seq(pairs)


def gen_business_highway(rng):
    """'4079 U.S. 17 Business Murrells Inlet, South Carolina 29576'."""
    pairs = [(str(rng.randint(100, 9999)), "AddressNumber")]
    style = rng.random()
    if style < 0.4:
        pairs += [("U.S.", "StreetNamePreType"), (str(rng.randint(1, 99)), "StreetName")]
    elif style < 0.7:
        pairs += [("US", "StreetNamePreType"), ("Highway", "StreetNamePreType"),
                  (str(rng.randint(1, 99)), "StreetName")]
    else:
        pairs += [("State", "StreetNamePreType"), ("Route", "StreetNamePreType"),
                  (str(rng.randint(1, 99)), "StreetName")]
    # Convention (verified against upstream gold): route qualifiers like
    # "Business" are part of the street name, not a post-type.
    if rng.random() < 0.6:
        pairs.append((rng.choice(["Business", "Bypass", "Alt"]), "StreetName"))
    pairs += city_tail(rng, full_state=rng.random() < 0.5)
    return seq(pairs)


def gen_zipless_tail(rng):
    """'610 EAST MAIN MARION KANSAS' — no zip, full state, no commas, upper."""
    pairs = [(str(rng.randint(100, 9999)), "AddressNumber")]
    if rng.random() < 0.6:
        pairs.append((rng.choice(["EAST", "WEST", "NORTH", "SOUTH"]), "StreetNamePreDirectional"))
    pairs.append((rng.choice(STREETS).upper(), "StreetName"))
    if rng.random() < 0.4:
        pairs.append((rng.choice(TYPES).upper(), "StreetNamePostType"))
    tail = city_tail(rng, with_zip=False, full_state=True, comma=False)
    pairs += [(t.upper(), l) for t, l in tail]
    return seq(pairs)


def gen_typeless_occupancy(rng):
    """'860 w Blackhawk 305 CHICAGO' — bare number after street = occupancy."""
    pairs = [(str(rng.randint(100, 9999)), "AddressNumber")]
    if rng.random() < 0.5:
        pairs.append((rng.choice(["w", "e", "n", "s"]), "StreetNamePreDirectional"))
    pairs.append((rng.choice(STREETS), "StreetName"))
    if rng.random() < 0.5:
        pairs.append((rng.choice(TYPES), "StreetNamePostType"))
    if rng.random() < 0.35:
        occ = rng.choice(OCC_TYPES)
        # '#' belongs to the identifier; word types (Apt/Unit/Ste) are the type.
        pairs.append((occ, "OccupancyIdentifier" if occ == "#" else "OccupancyType"))
    pairs.append((str(rng.randint(100, 999)), "OccupancyIdentifier"))
    pairs += city_tail(rng)
    return seq(pairs)


def gen_recipient(rng):
    """'LEXI HAGENSON 860 w Blackhawk 305 ...' — leading recipient names."""
    first = rng.choice(["LEXI", "JOHN", "MARIA", "SAM", "DANA", "PAT"])
    last = rng.choice(["HAGENSON", "SMITH", "GARCIA", "OBRIEN", "LEE", "NGUYEN"])
    base = gen_typeless_occupancy(rng)
    pairs = [(first, "Recipient"), (last, "Recipient")]
    pairs += list(zip(base["tokens"], base["labels"]))
    return seq(pairs)


GENERATORS = [
    (gen_route, 1800),
    (gen_hc_rr_box, 1500),
    (gen_business_highway, 1500),
    (gen_zipless_tail, 1500),
    (gen_typeless_occupancy, 1500),
    (gen_recipient, 1200),
]


def main():
    rng = random.Random(SEED)
    rows, seen = [], set()
    for fn, count in GENERATORS:
        made = 0
        attempts = 0
        while made < count and attempts < count * 20:
            attempts += 1
            r = fn(rng)
            key = " ".join(r["tokens"])
            if key in seen:
                continue
            seen.add(key)
            rows.append(r)
            made += 1
        print(f"{fn.__name__}: {made}")
    rng.shuffle(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"{len(rows)} synthetic sequences -> {OUT}")


if __name__ == "__main__":
    main()
