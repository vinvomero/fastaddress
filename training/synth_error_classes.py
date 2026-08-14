"""Targeted training data for the error classes the gold adjudication exposed.

Every pattern here traces to a specific human ruling or to Census evidence, and
the comment on each generator says which. Nothing is invented from intuition --
that is exactly how an earlier synthetic round (recipe 3) made the model worse.

Writes training/corpus/errclass.jsonl. Run validate_synth.py-style checks via
validate_errclass() before training.

Usage: python training/synth_error_classes.py [--per-pattern N]
"""

import argparse
import json
import random
from pathlib import Path

import usaddress

OUT = Path(__file__).parent / "corpus" / "errclass.jsonl"
SEED = 20260815

# ---------------------------------------------------------------- vocabularies

STREET_WORDS = [
    "WALNUT", "BEECHNUT", "BROOKHAVEN", "LAKESIDE", "COREY", "DEVEAUX", "WYCHWOOD",
    "STONE RIDGE", "SHENANDOAH", "OAKWOOD", "HAWTHORNE", "CHESTNUT", "MEADOW",
    "FOXPATH", "BRIARWOOD", "SADDLE", "HUNTINGTON", "WILLOW", "ASPEN", "CEDAR",
    "MAPLE", "PHEASANT", "TIMBER", "GLENDALE", "RIDGEFIELD", "SUTTON", "HARVEST",
]
TYPES = ["LN", "DR", "CT", "CIR", "RD", "WAY", "TER", "PL", "AVE", "ST", "BLVD",
         "LANE", "DRIVE", "COURT", "CIRCLE", "ROAD"]

# Cities whose first word is an abbreviated directional or descriptor. The
# ruling that created this list: the reviewer judged "425 SHORELINE RD LK
# BARRNGTN IL 60010" with LK labeled PlaceName -- an abbreviated city prefix
# belongs to the city, not to the street. Census confirms the same split for
# "S BARRINGTON" (its own city field comes back as "S BARRINGTON").
ABBREV_CITIES = [
    (["S", "BARRINGTON"], "IL", "60010"),
    (["N", "BARRINGTON"], "IL", "60010"),
    (["LK", "BARRNGTN"], "IL", "60010"),
    (["LK", "ZURICH"], "IL", "60047"),
    (["E", "DUNDEE"], "IL", "60118"),
    (["W", "DUNDEE"], "IL", "60118"),
    (["S", "ELGIN"], "IL", "60177"),
    (["N", "AURORA"], "IL", "60542"),
    (["W", "CHICAGO"], "IL", "60185"),
    (["MT", "PROSPECT"], "IL", "60056"),
    (["ARLINGTON", "HTS"], "IL", "60004"),
    (["HOFFMAN", "ESTA"], "IL", "60169"),
    (["S", "PASADENA"], "CA", "91030"),
    (["N", "HOLLYWOOD"], "CA", "91601"),
    (["E", "LANSING"], "MI", "48823"),
    (["W", "PALM", "BEACH"], "FL", "33401"),
    (["N", "LAS", "VEGAS"], "NV", "89030"),
    (["S", "SAN", "FRANCISCO"], "CA", "94080"),
]

# Real post-directionals, kept so the model does not learn that a trailing
# letter is ALWAYS a city prefix. Census showed both readings occur:
# "1305 Lake Shore Dr N, BARRINGTON" really is a post-directional.
PLAIN_CITIES = [("BARRINGTON", "IL", "60010"), ("SCHAUMBURG", "IL", "60173"),
                ("PALATINE", "IL", "60067"), ("EVANSTON", "IL", "60201"),
                ("NAPERVILLE", "IL", "60540"), ("OAK PARK", "IL", "60301")]
DIRS = ["N", "S", "E", "W", "NE", "NW", "SE", "SW"]

UNIT_TYPES = ["UNT", "UNIT", "APT", "STE", "SUITE", "RM", "FL", "BLDG", "TRLR", "LOT"]
UNIT_IDS = ["A", "B", "C", "D", "1", "2", "12", "3B", "204", "1500", "302"]


def seq(pairs):
    """pairs: [(token, label)] -> row dict, dropping empties."""
    toks = [t for t, _ in pairs if t]
    labs = [l for t, l in pairs if t]
    return {"tokens": toks, "labels": labs, "origin": "errclass"}


# ---------------------------------------------------------------- generators

def gen_abbrev_city(rng, n):
    """<number> <street> <type> S BARRINGTON IL 60010  ->  S is PlaceName.

    Ruling: reviewer confirmed LK in "LK BARRNGTN" as PlaceName (round 4, #3).
    Census agrees for S BARRINGTON, returning city='S BARRINGTON'."""
    out = []
    for _ in range(n):
        city, st, zc = rng.choice(ABBREV_CITIES)
        name = rng.choice(STREET_WORDS)
        typ = rng.choice(TYPES)
        p = [(str(rng.randint(1, 4999)), "AddressNumber")]
        p += [(w, "StreetName") for w in name.split()]
        p += [(typ, "StreetNamePostType")]
        p += [(w, "PlaceName") for w in city]
        p += [(st, "StateName"), (zc, "ZipCode")]
        out.append(seq(p))
    return out


def gen_true_post_directional(rng, n):
    """<number> <street> <type> N, BARRINGTON IL  ->  N really is a directional.

    Counterweight to the generator above so the model keeps both readings.
    Census showed "1305 Lake Shore Dr N" resolves with suffixDirection='N'."""
    out = []
    for _ in range(n):
        city, st, zc = rng.choice(PLAIN_CITIES)
        name = rng.choice(STREET_WORDS)
        p = [(str(rng.randint(1, 4999)), "AddressNumber")]
        p += [(w, "StreetName") for w in name.split()]
        p += [(rng.choice(TYPES), "StreetNamePostType"),
              (rng.choice(DIRS), "StreetNamePostDirectional")]
        p += [(w, "PlaceName") for w in city.split()]
        p += [(st, "StateName"), (zc, "ZipCode")]
        out.append(seq(p))
    return out


def gen_unit_abbrev(rng, n):
    """... ST UNT D CARY IL  ->  UNT is an OccupancyType, D its identifier.

    From the adjudicated both-wrong record "210 CRYSTAL ST UNT D CARY IL 60013",
    where both models failed to recognise the abbreviated unit designator."""
    out = []
    for _ in range(n):
        city, st, zc = rng.choice(PLAIN_CITIES)
        p = [(str(rng.randint(1, 4999)), "AddressNumber"),
             (rng.choice(STREET_WORDS).split()[0], "StreetName"),
             (rng.choice(TYPES), "StreetNamePostType"),
             (rng.choice(UNIT_TYPES), "OccupancyType"),
             (rng.choice(UNIT_IDS), "OccupancyIdentifier")]
        p += [(w, "PlaceName") for w in city.split()]
        p += [(st, "StateName"), (zc, "ZipCode")]
        out.append(seq(p))
    return out


def gen_bare_street_no_number(rng, n):
    """BROADWAY NEW YORK NY 10013  ->  BROADWAY is a StreetName, not a place.

    Reviewer ruling (round 4, #35): "Broadway is the street; NEW YORK is the
    locality." Both models had labelled it PlaceName."""
    named = ["BROADWAY", "COMMONWEALTH", "MAIN", "MARKET", "STATE", "MADISON",
             "LEXINGTON", "WABASH", "CANAL", "HOUSTON", "BOWERY"]
    cities = [(["NEW", "YORK"], "NY", "10013"), (["CHICAGO"], "IL", "60601"),
              (["BOSTON"], "MA", "02116"), (["SAN", "DIEGO"], "CA", "92101")]
    out = []
    for _ in range(n):
        city, st, zc = rng.choice(cities)
        p = [(rng.choice(named), "StreetName")]
        p += [(w, "PlaceName") for w in city]
        p += [(st, "StateName"), (zc, "ZipCode")]
        out.append(seq(p))
    return out


def gen_grid_predirectional(rng, n):
    """295 South 250 East, Burley, ID  ->  South is a PreDirectional, not a PreType.

    Reviewer ruling (round 4, #34), the one record the candidate lost."""
    words = ["North", "South", "East", "West", "N", "S", "E", "W"]
    cities = [(["Burley"], "ID", "83318"), (["Provo"], "UT", "84601"),
              (["Logan"], "UT", "84321"), (["Rexburg"], "ID", "83440"),
              (["Ogden"], "UT", "84401")]
    out = []
    for _ in range(n):
        city, st, zc = rng.choice(cities)
        p = [(str(rng.randint(1, 3999)), "AddressNumber"),
             (rng.choice(words), "StreetNamePreDirectional"),
             (str(rng.choice([100, 150, 200, 250, 300, 400, 500, 600, 800, 1200])), "StreetName"),
             (rng.choice(words), "StreetNamePostDirectional")]
        p += [(w, "PlaceName") for w in city]
        p += [(st, "StateName"), (zc, "ZipCode")]
        out.append(seq(p))
    return out


def gen_directional_multiword_street(rng, n):
    """340 E NORTH WATER 2500 CHICAGO  ->  NORTH WATER is the street name.

    Matches the reviewer-approved parse of "6 West South Water Market,
    Chicago" (round 4, #39), where West is the directional and South Water
    Market is all StreetName."""
    firsts = ["NORTH", "SOUTH", "EAST", "WEST"]
    seconds = ["WATER", "WACKER", "SHORE", "PARK", "MARKET", "HAVEN", "GROVE"]
    out = []
    for _ in range(n):
        p = [(str(rng.randint(1, 4999)), "AddressNumber"),
             (rng.choice(["E", "W", "N", "S"]), "StreetNamePreDirectional"),
             (rng.choice(firsts), "StreetName"),
             (rng.choice(seconds), "StreetName")]
        if rng.random() < 0.5:
            p.append((str(rng.randint(100, 4000)), "OccupancyIdentifier"))
        p += [("CHICAGO", "PlaceName"), ("IL", "StateName"),
              (rng.choice(["60611", "60601", "60608", "60654"]), "ZipCode")]
        out.append(seq(p))
    return out


def gen_milepost_route(rng, n):
    """Mile K Beach Road # 1, Kenai, AK  ->  Mile is a PreType, K Beach the name.

    Matches the reviewer-approved parse of "Mi K Beach Road # 2" (round 4,
    #19), where Mi=PreType, K Beach=StreetName, '# 2'=OccupancyIdentifier."""
    out = []
    for _ in range(n):
        p = [(rng.choice(["Mile", "Mi", "MP"]), "StreetNamePreType"),
             (rng.choice(["K", "J", "T", "C"]), "StreetName"),
             (rng.choice(["Beach", "Spur", "Bay", "River"]), "StreetName"),
             (rng.choice(["Road", "Rd", "Hwy"]), "StreetNamePostType"),
             ("#", "OccupancyIdentifier"),
             (str(rng.randint(1, 40)), "OccupancyIdentifier"),
             (rng.choice(["Kenai", "Soldotna", "Homer"]), "PlaceName"),
             ("AK", "StateName"),
             (rng.choice(["99611", "99669", "99603"]), "ZipCode")]
        out.append(seq(p))
    return out


def gen_truncated_type(rng, n):
    """810 BARRINGTON POINT R BARRINGTON IL  ->  R is a truncated street type.

    From the adjudicated both-wrong record; the mail file clips 'RD' to 'R'."""
    trunc = ["R", "D", "L", "C", "A", "S", "B", "T"]
    out = []
    for _ in range(n):
        city, st, zc = rng.choice(PLAIN_CITIES)
        name = rng.choice(STREET_WORDS)
        p = [(str(rng.randint(1, 4999)), "AddressNumber")]
        p += [(w, "StreetName") for w in name.split()]
        p += [(rng.choice(["POINT", "RIDGE", "PARK", "HILL", "VIEW"]), "StreetName"),
              (rng.choice(trunc), "StreetNamePostType")]
        p += [(w, "PlaceName") for w in city.split()]
        p += [(st, "StateName"), (zc, "ZipCode")]
        out.append(seq(p))
    return out


GENERATORS = [
    ("abbrev_city", gen_abbrev_city, 4.0),
    ("true_post_directional", gen_true_post_directional, 1.5),
    ("unit_abbrev", gen_unit_abbrev, 1.0),
    ("bare_street_no_number", gen_bare_street_no_number, 1.0),
    ("grid_predirectional", gen_grid_predirectional, 1.5),
    ("directional_multiword_street", gen_directional_multiword_street, 1.0),
    ("milepost_route", gen_milepost_route, 0.6),
    ("truncated_type", gen_truncated_type, 1.0),
]


def validate(rows):
    """Same discipline as validate_synth.py: labels must exist in the model's
    schema, and the tokens must be what usaddress.tokenize would produce."""
    valid = set(usaddress.LABELS)
    bad = []
    for r in rows:
        for t, l in zip(r["tokens"], r["labels"]):
            if l not in valid:
                bad.append((r["tokens"], f"{l} is not a model label"))
        if usaddress.tokenize(" ".join(r["tokens"])) != r["tokens"]:
            bad.append((r["tokens"], "tokens are not what usaddress.tokenize produces"))
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-pattern", type=int, default=3000)
    args = ap.parse_args()
    rng = random.Random(SEED)

    rows, counts = [], {}
    for name, fn, weight in GENERATORS:
        got = fn(rng, int(args.per_pattern * weight))
        counts[name] = len(got)
        rows += got

    bad = validate(rows)
    if bad:
        for toks, why in bad[:10]:
            print(f"VIOLATION: {' '.join(toks)[:60]} | {why}")
        raise SystemExit(f"{len(bad)} violations -- not writing")

    # Never train on an evaluation address.
    ex = set()
    for p in (Path(__file__).parent.parent / "eval" / "gold" / "candidates.jsonl",
              Path(__file__).parent.parent / "eval" / "clean" / "clean.jsonl"):
        for line in open(p, encoding="utf-8-sig"):
            if line.strip():
                ex.add("".join(c for c in json.loads(line)["raw"].upper() if c.isalnum()))
    kept = [r for r in rows if "".join(c for c in " ".join(r["tokens"]).upper() if c.isalnum()) not in ex]

    rng.shuffle(kept)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        for r in kept:
            f.write(json.dumps(r) + "\n")
    print(f"{len(kept)} sequences (dropped {len(rows)-len(kept)} eval collisions) -> {OUT}")
    for k, v in counts.items():
        print(f"  {k:30} {v}")


if __name__ == "__main__":
    main()
