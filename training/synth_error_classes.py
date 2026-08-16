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

from build_corpus import add_noise

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
    # Round-6 ruling: FOX RVR GRV is a city. GRV/RVR double as TIGER suffix
    # abbreviations, and the realtext corpus's 146k genuine-suffix rows pull
    # these tokens toward street labels; these entries hold the city reading.
    (["FOX", "RVR", "GRV"], "IL", "60021"),
    (["ELK", "GRV", "VLG"], "IL", "60007"),
    (["BUFF", "GRV"], "IL", "60089"),
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
    Census showed "1305 Lake Shore Dr N" resolves with suffixDirection='N'.
    Spelled forms added for the realtext era: round-6 ruling kept "Southwest"
    in "2926 Franklin Road Southwest, Roanoke VA" as the post-directional
    (quadrant style), and no frame covered spelled directions after a named
    street; v41 regressed exactly there."""
    spelled = ["North", "South", "East", "West",
               "Northeast", "Northwest", "Southeast", "Southwest"]
    out = []
    for _ in range(n):
        city, st, zc = rng.choice(PLAIN_CITIES)
        name = rng.choice(STREET_WORDS)
        p = [(str(rng.randint(1, 4999)), "AddressNumber")]
        p += [(w, "StreetName") for w in name.split()]
        p += [(rng.choice(TYPES), "StreetNamePostType"),
              (rng.choice(DIRS + spelled), "StreetNamePostDirectional")]
        p += [(w, "PlaceName") for w in city.split()]
        p += [(st, "StateName"), (zc, "ZipCode")]
        out.append(seq(p))
    return out


def gen_landmark_field(rng, n):
    """Lee Bird Fld, North Platte NE  ->  the pre-city phrase is a landmark.

    Ruling: round 1 approved the LandmarkName reading of "Lee Bird Fld" (the
    North Platte airfield). The realtext corpus contains zero LandmarkName
    rows, so suffix pressure (Fld=Field) pulls these toward street labels;
    this is the counterweight. No address number -- that absence plus the
    landmark-typical final word is what distinguishes the class."""
    firsts = ["Lee", "Casey", "Miller", "Baker", "Wiley", "Hays", "Ross", "Ward"]
    seconds = ["Bird", "Jones", "Young", "Webb", "Clark", "Boyd", "Reed"]
    ends = ["Fld", "Field", "Airport", "Arpt", "Municipal Airport",
            "Fairgrounds", "Stadium", "Regional Airport"]
    out = []
    for _ in range(n):
        city, st, zc = rng.choice(PLAIN_CITIES)
        words = [rng.choice(firsts)]
        if rng.random() < 0.8:
            words.append(rng.choice(seconds))
        words += rng.choice(ends).split()
        p = [(w, "LandmarkName") for w in words]
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


# ------------------------------------------- counterweights (added after v21)
# v21 cleared the target classes but broke four clean-set records. Each
# generator below repairs one of those breaks. They exist because the first
# pass taught a pattern without teaching its neighbours, which is the same
# mistake that made an earlier synthetic round degrade the model.

SPELLED_STATES = [
    ("New Jersey", "NJ"), ("New York", "NY"), ("New Mexico", "NM"),
    ("New Hampshire", "NH"), ("North Carolina", "NC"), ("South Carolina", "SC"),
    ("North Dakota", "ND"), ("South Dakota", "SD"), ("West Virginia", "WV"),
    ("Rhode Island", "RI"), ("Puerto Rico", "PR"),
]


def gen_spelled_state(rng, n):
    """... Pitman, New Jersey 08071  ->  New Jersey is a two-word StateName.

    v21 broke "43 South Broadway Pitman, New Jersey 08071", reading New Jersey
    as a city. The corpus was dense with two-word PLACE names and had almost no
    spelled-out two-word STATE names, so the model learned the wrong prior for
    "New <Word>". Same root cause as the v20 clean-set regression."""
    cities = ["Pitman", "Trenton", "Camden", "Dover", "Concord", "Raleigh",
              "Durham", "Fargo", "Providence", "Charleston", "Santa Fe"]
    out = []
    for _ in range(n):
        state, _ = rng.choice(SPELLED_STATES)
        p = [(str(rng.randint(1, 999)), "AddressNumber")]
        if rng.random() < 0.5:
            p.append((rng.choice(["North", "South", "East", "West"]), "StreetNamePreDirectional"))
        p += [(rng.choice(["Broadway", "Main", "Market", "Union", "Chestnut"]), "StreetName")]
        if rng.random() < 0.6:
            p.append((rng.choice(["Street", "Avenue", "Road", "St", "Ave"]), "StreetNamePostType"))
        city = rng.choice(cities)
        p += [(w, "PlaceName") for w in city.split()]
        p += [(w, "StateName") for w in state.split()]
        p += [(f"{rng.randint(1000,99999):05d}", "ZipCode")]
        out.append(seq(p))
    return out


def gen_postdir_then_building(rng, n):
    """2908 Bryant Ave S Uptown Square, Minneapolis  ->  S stays a direction.

    v21 relabelled that S as a BuildingName: the abbreviated-city generator had
    taught it that a trailing letter before a capitalised word belongs to a
    place. A building name can follow a genuine post-directional, so both
    shapes must be present."""
    buildings = ["Uptown Square", "Riverside Tower", "Lakeview Commons",
                 "Grand Plaza", "Harbor Point", "The Metropolitan"]
    out = []
    for _ in range(n):
        city, st, zc = rng.choice(PLAIN_CITIES)
        p = [(str(rng.randint(1, 4999)), "AddressNumber"),
             (rng.choice(STREET_WORDS).split()[0], "StreetName"),
             (rng.choice(["Ave", "St", "Blvd", "Rd"]), "StreetNamePostType"),
             (rng.choice(DIRS), "StreetNamePostDirectional")]
        p += [(w, "BuildingName") for w in rng.choice(buildings).split()]
        p += [(w, "PlaceName") for w in city.split()]
        p += [(st, "StateName"), (zc, "ZipCode")]
        out.append(seq(p))
    return out


def gen_street_then_building(rng, n):
    """3705 N Overlook Blvd Overlook Park Flats, Portland  ->  street survives.

    v21 swallowed "Overlook Blvd" into the BuildingName. The street phrase and
    the building name can share a word, so the boundary has to be learned
    rather than guessed from the vocabulary."""
    stems = ["Overlook", "Riverside", "Lakeview", "Hillcrest", "Fairview"]
    out = []
    for _ in range(n):
        stem = rng.choice(stems)
        p = [(str(rng.randint(1, 4999)), "AddressNumber"),
             (rng.choice(["N", "S", "E", "W"]), "StreetNamePreDirectional"),
             (stem, "StreetName"),
             (rng.choice(["Blvd", "Ave", "St", "Dr"]), "StreetNamePostType")]
        p += [(stem, "BuildingName"),
              (rng.choice(["Park", "Court", "Garden"]), "BuildingName"),
              (rng.choice(["Flats", "Apartments", "Lofts"]), "BuildingName")]
        p += [(rng.choice(["Portland", "Seattle", "Denver"]), "PlaceName"),
              (rng.choice(["OR", "WA", "CO"]), "StateName"),
              (f"{rng.randint(10000,99999)}", "ZipCode")]
        out.append(seq(p))
    return out


def gen_the_named_street(rng, n):
    """1 The Square, Lillington, NC  ->  Square is part of the NAME.

    A type-word preceded by "The" is the street's proper name, not its suffix.
    v21 reverted this to StreetNamePostType and lost a record the reviewer had
    already ruled on in round 3."""
    words = ["Square", "Circle", "Green", "Commons", "Mall", "Crescent", "Grove", "Row"]
    cities = [("Lillington", "NC"), ("Bethesda", "MD"), ("Concord", "MA"), ("Salem", "OR")]
    out = []
    for _ in range(n):
        city, st = rng.choice(cities)
        p = [(str(rng.randint(1, 99)), "AddressNumber"),
             ("The", "StreetName"),
             (rng.choice(words), "StreetName"),
             (city, "PlaceName"), (st, "StateName"),
             (f"{rng.randint(10000,99999)}", "ZipCode")]
        out.append(seq(p))
    return out


def gen_national_cities(rng, n):
    """Real city names from the national Census PLACE inventory.

    The national divergence scan showed the invented-vocabulary generators
    overcorrecting outside the states they were written from: "New Orleans"
    read as a state, "South Fulton" as a directional, "Box Elder" as a PO box,
    "Tinley Park" as a state. This teaches the actual national distribution of
    confusable city names, in four shapes:

      <num> <street> <type> <City> <ST> <zip>     the standard frame
      <num> <street> <type> <City>, <ST>          comma, no zip
      <num> <street> <type> <City> <zip>          no state (the Tinley Park case)
      <num> <street> <type> <City>                bare tail

    Requires training/vocab_cities.json (build_city_vocab.py). Returns [] if
    absent so the pipeline still runs, but the build script should fail loudly
    in that case rather than silently training without it."""
    vocab_path = Path(__file__).parent / "vocab_cities.json"
    if not vocab_path.exists():
        return []
    vocab = json.loads(vocab_path.read_text(encoding="utf-8"))
    # Coverage, not sampling, for the confusable-start class. Sampling 1,549
    # cities into a few thousand slots gave each one ~1.5 exposures per tail
    # shape -- the v27 Georgia result showed that is not enough to learn a
    # vocabulary. Every confusable-start city now appears a guaranteed number
    # of times; the other pools stay sampled.
    # The 32-state holdout showed the hand-picked confusable prefix list was
    # the wrong boundary: Little Rock, Sans Souci, Cross Plains, and Fair Oaks
    # all failed, and none starts with a word on that list. ANY multi-word
    # city whose first word could read as street material is confusable, so
    # every multi-word city gets guaranteed coverage -- confusable-start ones
    # twice, everything else at least once.
    conf = [tuple(x) for x in vocab["confusable_start"]]
    rest = [tuple(x) for x in vocab["confusable_end"]] + [tuple(x) for x in vocab["two_word"]]
    schedule = conf * 2 + rest
    rng.shuffle(schedule)
    out = []
    for i in range(n):
        city, st = schedule[i % len(schedule)]
        p = [(str(rng.randint(1, 9999)), "AddressNumber"),
             (rng.choice(STREET_WORDS).split()[0], "StreetName"),
             (rng.choice(TYPES), "StreetNamePostType")]
        shape = rng.random()
        cw = city.split()
        p += [(w, "PlaceName") for w in cw]
        if shape < 0.45:
            p += [(st, "StateName"), (f"{rng.randint(1000, 99999):05d}", "ZipCode")]
        elif shape < 0.70:
            p += [(st, "StateName")]
        elif shape < 0.90:
            p += [(f"{rng.randint(1000, 99999):05d}", "ZipCode")]
        out.append(seq(p))
    return out


def gen_national_post_directional(rng, n):
    """<num> <street> <type> <DIR> <PlainCity> ...  ->  DIR stays a directional.

    The v24 national scan showed the city-prefix training overfiring in grid
    cities: "e 1st st n wichita" read the n as part of Wichita, failing the
    3:1 ship rule in KS (67:458) and MO (3:76). The distinguishing signal is
    the city itself -- Wichita has no directional-prefixed variant, S
    Barrington does -- and that is vocabulary, learnable only if plain cities
    appear in this frame. Uses the national single-word city pool."""
    vocab_path = Path(__file__).parent / "vocab_cities.json"
    if not vocab_path.exists():
        return []
    plain = [tuple(x) for x in json.loads(vocab_path.read_text(encoding="utf-8")).get("plain", [])]
    if not plain:
        return []
    out = []
    for _ in range(n):
        city, st = plain[rng.randrange(len(plain))]
        # Numbered ordinal streets half the time -- the failing shape was
        # "e 1st st n wichita", and ordinals carry their own features.
        if rng.random() < 0.5:
            k = rng.randint(1, 99)
            suf = "th" if 10 <= k % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(k % 10, "th")
            name = f"{k}{suf}"
        else:
            name = rng.choice(STREET_WORDS).split()[0]
        p = [(str(rng.randint(1, 9999)), "AddressNumber")]
        if rng.random() < 0.5:
            p.append((rng.choice(["N", "S", "E", "W"]), "StreetNamePreDirectional"))
        p += [(name, "StreetName"),
              (rng.choice(TYPES), "StreetNamePostType"),
              (rng.choice(DIRS), "StreetNamePostDirectional"),
              (city, "PlaceName")]
        if rng.random() < 0.8:
            p.append((st, "StateName"))
        if rng.random() < 0.7:
            p.append((f"{rng.randint(1000, 99999):05d}", "ZipCode"))
        out.append(seq(p))
    return out


SPELLED_STATES_ONE_WORD = [
    ("California", "CA"), ("Texas", "TX"), ("Florida", "FL"), ("Illinois", "IL"),
    ("Ohio", "OH"), ("Georgia", "GA"), ("Michigan", "MI"), ("Washington", "WA"),
    ("Arizona", "AZ"), ("Colorado", "CO"), ("Oregon", "OR"), ("Nevada", "NV"),
    ("Wisconsin", "WI"), ("Minnesota", "MN"), ("Missouri", "MO"), ("Alabama", "AL"),
    ("Kentucky", "KY"), ("Oklahoma", "OK"), ("Connecticut", "CT"), ("Iowa", "IA"),
]


def gen_spelled_state_one_word(rng, n):
    """... VAN NUYS, CALIFORNIA  ->  CALIFORNIA is a StateName.

    v24 broke the clean record "5 NORTH MAIN, VAN NUYS, CALIFORNIA": the
    spelled-state generator covered only two-word states, so a single-word
    spelled state at the tail lost to the city-heavy prior."""
    cities = ["Van Nuys", "Fresno", "Amarillo", "Tampa", "Peoria", "Dayton",
              "Spokane", "Tucson", "Boulder", "Salem", "Reno", "Madison"]
    out = []
    for _ in range(n):
        state, _ = rng.choice(SPELLED_STATES_ONE_WORD)
        p = [(str(rng.randint(1, 999)), "AddressNumber")]
        if rng.random() < 0.4:
            p.append((rng.choice(["NORTH", "SOUTH", "EAST", "WEST"]), "StreetNamePreDirectional"))
        p.append((rng.choice(["MAIN", "OAK", "ELM", "MARKET", "BROADWAY"]), "StreetName"))
        if rng.random() < 0.5:
            p.append((rng.choice(["ST", "AVE", "BLVD"]), "StreetNamePostType"))
        city = rng.choice(cities)
        p += [(w, "PlaceName") for w in city.split()]
        p += [(w, "StateName") for w in state.split()]
        if rng.random() < 0.5:
            p.append((f"{rng.randint(10000, 99999)}", "ZipCode"))
        out.append(seq(p))
    return out


def gen_wisconsin_grid_number(rng, n):
    """N165 W2123 Tartan Ct  ->  both alphanumeric tokens are the address number.

    Wisconsin's fire-numbering system. v24 read W2123 as a StreetName after the
    national city vocabulary taught leading directional letters near the start
    of a string; the counterweight is the actual shape."""
    out = []
    for _ in range(n):
        a = f"{rng.choice(['N','S','W'])}{rng.randint(1, 199)}"
        b = f"{rng.choice(['N','S','W'])}{rng.randint(1000, 39999)}"
        p = [(a, "AddressNumber"), (b, "AddressNumber"),
             (rng.choice(STREET_WORDS).split()[0].title(), "StreetName"),
             (rng.choice(["Ct", "Rd", "Dr", "Ln", "Ave"]), "StreetNamePostType"),
             (rng.choice(["Jackson", "Menomonee Falls", "Germantown", "Richfield"]).split()[0], "PlaceName"),
             ("WI", "StateName"), (f"{rng.randint(53000, 54999)}", "ZipCode")]
        out.append(seq(p))
    return out


def gen_person_named_street(rng, n):
    """250 JOHN W MORROW JR PKWY  ->  the middle initial stays StreetName.

    v25 read the W as a post-directional after the plain-city post-directional
    counterweight landed. Person-named streets carry initials and suffixes in
    the middle of the name; the whole phrase before the type is StreetName."""
    firsts = ["JOHN", "JAMES", "ROBERT", "MARY", "MARTIN", "GEORGE", "CESAR"]
    lasts = ["MORROW", "KING", "CHAVEZ", "PARKS", "LEE", "BYRD", "LUCAS"]
    sufs = ["JR", "SR", "III"]
    out = []
    for _ in range(n):
        p = [(str(rng.randint(1, 4999)), "AddressNumber"), (rng.choice(firsts), "StreetName")]
        if rng.random() < 0.6:
            p.append((rng.choice("WEABCDHLM"), "StreetName"))  # middle initial
        p.append((rng.choice(lasts), "StreetName"))
        if rng.random() < 0.5:
            p.append((rng.choice(sufs), "StreetName"))
        p.append((rng.choice(["PKWY", "BLVD", "DR", "AVE", "WAY"]), "StreetNamePostType"))
        if rng.random() < 0.6:
            city, st, zc = rng.choice(PLAIN_CITIES)
            p += [(w, "PlaceName") for w in city.split()]
            p += [(st, "StateName"), (zc, "ZipCode")]
        out.append(seq(p))
    return out


def gen_the_building(rng, n):
    """102 Sottile St The Merchant, Unit 305  ->  The Merchant is a building.

    The counterweight for gen_the_named_street: "The <word>" after a COMPLETE
    street phrase is a building name, not more street. v25 ate one."""
    names = ["Merchant", "Residences", "Metropolitan", "Standard", "Foundry",
             "Armory", "Exchange", "Landmark", "Waverly"]
    out = []
    for _ in range(n):
        p = [(str(rng.randint(1, 4999)), "AddressNumber"),
             (rng.choice(STREET_WORDS).split()[0].title(), "StreetName"),
             (rng.choice(["St", "Ave", "Blvd", "Dr"]), "StreetNamePostType"),
             ("The", "BuildingName"), (rng.choice(names), "BuildingName")]
        if rng.random() < 0.6:
            p += [(rng.choice(["Unit", "Apt", "Ste"]), "OccupancyType"),
                  (str(rng.randint(1, 999)), "OccupancyIdentifier")]
        city, st, zc = rng.choice(PLAIN_CITIES)
        p += [(w, "PlaceName") for w in city.split()]
        p += [(st, "StateName"), (zc, "ZipCode")]
        out.append(seq(p))
    return out


def gen_county_letter_road(rng, n):
    """7575 COUNTY ROAD ZZZ, MILWAUKEE, WI  ->  COUNTY ROAD is a pre-type.

    Wisconsin letter-series county roads. This clean-set record went from
    passing to failing across corpus rebuilds -- a borderline route-designation
    record destabilised by churn -- so the shape gets an explicit anchor.
    Convention per upstream labeled.xml: route designators are
    StreetNamePreType, the letters are the StreetName."""
    letters = ["ZZZ", "KK", "J", "QQ", "XX", "M", "VV", "EE", "T"]
    pairs = [("MILWAUKEE", "WI"), ("WAUKESHA", "WI"), ("OSHKOSH", "WI"),
             ("GREENVILLE", "SC"), ("CHARLESTON", "WV"), ("LITTLE ROCK", "AR"),
             ("APPLETON", "WI"), ("MADISON", "WI"), ("NASHVILLE", "TN")]
    # The holdout added the abbreviated designators: SC/WV/WI county routes
    # arrive as "Co Rd 653" / "Co Rte 21" / "Co Hwy D", and v28 read Co Rd as
    # part of the street name. Same upstream convention: designators are
    # StreetNamePreType, what follows is the StreetName.
    first = ["COUNTY", "CO", "Co", "CNTY", "US", "STATE", "State"]
    second = ["ROAD", "RD", "Rd", "RTE", "Rte", "HWY", "Hwy", "HIGHWAY", "TRUNK"]
    out = []
    for _ in range(n):
        city, st = rng.choice(pairs)
        name = rng.choice(letters) if rng.random() < 0.4 else str(rng.randint(10, 9999))
        if name.isdigit() and rng.random() < 0.25:
            name += rng.choice(["W", "S", "E", "N", "A"])
        p = [(str(rng.randint(1, 9999)), "AddressNumber"),
             (rng.choice(first), "StreetNamePreType"),
             (rng.choice(second), "StreetNamePreType"),
             (name, "StreetName")]
        p += [(w, "PlaceName") for w in city.split()]
        p += [(st, "StateName"), (f"{rng.randint(10000, 99999)}", "ZipCode")]
        out.append(seq(p))
    return out


def gen_letter_avenue_grid(rng, n):
    """5025 N 13th E Ave Tulsa  ->  the E belongs to the street name.

    Tulsa's grid names avenues "13th E Ave" / "8th W Pl"; the letter is part
    of the name, not a post-directional. 115 holdout records failed on it."""
    out = []
    for _ in range(n):
        k = rng.randint(1, 99)
        suf = "th" if 10 <= k % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(k % 10, "th")
        p = [(str(rng.randint(1, 9999)), "AddressNumber"),
             (rng.choice(["N", "S", "E", "W"]), "StreetNamePreDirectional"),
             (f"{k}{suf}", "StreetName"),
             (rng.choice(["E", "W"]), "StreetName"),
             (rng.choice(["Ave", "Pl", "St"]), "StreetNamePostType"),
             ("Tulsa", "PlaceName"), ("OK", "StateName"),
             (f"{rng.randint(74100, 74199)}", "ZipCode")]
        out.append(seq(p))
    return out


def gen_bare_route(rng, n):
    """474 Rte 101 Bedford NH  ->  Rte is a pre-type even with no prefix word.

    All 40 New Hampshire holdout failures were this one shape: the route
    generators always carried a prefix (State Rte, US Hwy, Co Rd), so a bare
    designator read as a street name."""
    cities = [("BEDFORD", "NH"), ("CONCORD", "NH"), ("KEENE", "NH"),
              ("BRATTLEBORO", "VT"), ("AUBURN", "ME"), ("KEARNEY", "NE")]
    out = []
    for _ in range(n):
        city, st = rng.choice(cities)
        num = str(rng.randint(1, 999))
        if rng.random() < 0.35:
            num += rng.choice(["W", "S", "E", "N", "A", "a", "B"])
        p = [(str(rng.randint(1, 9999)), "AddressNumber"),
             (rng.choice(["Rte", "RTE", "Route", "ROUTE", "Hwy", "HWY", "SR"]), "StreetNamePreType"),
             (num, "StreetName"),
             (city, "PlaceName"), (st, "StateName"),
             (f"{rng.randint(10000, 99999)}", "ZipCode")]
        out.append(seq(p))
    return out


def gen_route_spelled_postdir(rng, n):
    """1285 Highway 7 East Hutchinson MN  ->  East is a post-directional.

    Ruling: round 6, #4 -- the human verdict keeps "East" after a numbered
    highway as StreetNamePostDirectional, not a city lead. The realtext
    corpus's direction-led city rows pull the other way; this frame is the
    counterweight. Spelled forms doubled: abbreviations already have cover."""
    cities = [("Hutchinson", "MN"), ("Willmar", "MN"), ("Glencoe", "MN"),
              ("KEARNEY", "NE"), ("MOULTRIE", "GA"), ("PARIS", "TX")]
    dirs_ = ["East", "West", "North", "South",
             "East", "West", "North", "South", "E", "W", "N", "S"]
    out = []
    for _ in range(n):
        city, st = rng.choice(cities)
        p = [(str(rng.randint(1, 9999)), "AddressNumber")]
        lead = rng.choice(["Highway", "Hwy", "HIGHWAY", "State Highway", "Route"])
        p += [(w, "StreetNamePreType") for w in lead.split()]
        p += [(str(rng.randint(1, 999)), "StreetName"),
              (rng.choice(dirs_), "StreetNamePostDirectional")]
        p += [(w, "PlaceName") for w in city.split()]
        p += [(st, "StateName"), (f"{rng.randint(10000, 99999)}", "ZipCode")]
        out.append(seq(p))
    return out


def gen_inner_directional_street(rng, n):
    """5670 Lawton Loop W Dr Lawrence IN  ->  Loop and W are the street name.

    Indianapolis's paired-drive idiom: "<Name> Loop East Drive" / "West Drive".
    A type-word or directional followed by ANOTHER type at the end belongs to
    the name; only the final Dr is the type. ~30 Indiana holdout failures."""
    mids = ["Loop", "Lane", "Boulevard", "Trail", "Bay", "Run"]
    dirs_ = ["E", "W", "East", "West", "N", "S"]
    cities = [("Lawrence", "IN"), ("Indianapolis", "IN"), ("Speedway", "IN")]
    out = []
    for _ in range(n):
        city, st = rng.choice(cities)
        p = [(str(rng.randint(1, 9999)), "AddressNumber"),
             (rng.choice(STREET_WORDS).split()[0].title(), "StreetName"),
             (rng.choice(mids), "StreetName"),
             (rng.choice(dirs_), "StreetName"),
             (rng.choice(["Dr", "Drive"]), "StreetNamePostType"),
             (city, "PlaceName"), (st, "StateName"),
             (f"{rng.randint(46000, 46999)}", "ZipCode")]
        out.append(seq(p))
    return out


def gen_postdir_before_confusable_city(rng, n):
    """10 Mariners Cv N New Orleans LA  ->  the N stays a directional.

    The national scan showed a residual leak: a genuine post-directional right
    before a confusable-start city gets absorbed into the city. The frame
    type + DIR + confusable-city teaches that the directional survives even
    when "New Orleans" follows."""
    vocab_path = Path(__file__).parent / "vocab_cities.json"
    if not vocab_path.exists():
        return []
    conf = [tuple(x) for x in json.loads(vocab_path.read_text(encoding="utf-8"))["confusable_start"]]
    # Direction-first cities are excluded: teaching "St N South Portland" with
    # the N as a directional pulled the South back into a directional too (all
    # 61 Maine holdout failures in v30). The leak this generator repairs was
    # "N New Orleans", and New/Lake/Saint/Mount cities carry no such conflict.
    DIRWORDS = {"north", "south", "east", "west"}
    conf = [(c, st) for c, st in conf if c.split()[0].lower() not in DIRWORDS]
    out = []
    for _ in range(n):
        city, st = conf[rng.randrange(len(conf))]
        p = [(str(rng.randint(1, 9999)), "AddressNumber"),
             (rng.choice(STREET_WORDS).split()[0].title(), "StreetName"),
             (rng.choice(["Cv", "Ct", "Dr", "Ln", "St", "Ave"]), "StreetNamePostType"),
             (rng.choice(["N", "S", "E", "W"]), "StreetNamePostDirectional")]
        p += [(w, "PlaceName") for w in city.split()]
        if rng.random() < 0.8:
            p.append((st, "StateName"))
        if rng.random() < 0.6:
            p.append((f"{rng.randint(10000, 99999)}", "ZipCode"))
        out.append(seq(p))
    return out


def gen_pike_and_xing(rng, n):
    """595 Two Mile Pike Goodlettsville TN  ->  Pike is the street type.

    Nashville's pikes and the Xing/Scn abbreviations were absorbed into city
    names in the Tennessee holdout county. Types per the upstream vocabulary;
    multi-word names kept so "Two Mile" stays street material."""
    names = ["Two Mile", "Granny White", "Old Hickory", "Lebanon", "Charlotte",
             "Nolensville", "Gallatin", "Swans", "Elm Hill"]
    cities = [("Goodlettsville", "TN"), ("Nashville", "TN"), ("Belle Meade", "TN"),
              ("Hendersonville", "TN"), ("Brentwood", "TN")]
    out = []
    for _ in range(n):
        city, st = rng.choice(cities)
        name = rng.choice(names)
        p = [(str(rng.randint(1, 9999)), "AddressNumber")]
        p += [(w, "StreetName") for w in name.split()]
        p += [(rng.choice(["Pike", "Xing", "Scn", "Pkwy"]), "StreetNamePostType"),
              (city, "PlaceName"), (st, "StateName"),
              (f"{rng.randint(37000, 38599)}", "ZipCode")]
        out.append(seq(p))
    return out


GENERATORS = [
    # abbrev_city carried weight 4.0 in v21, which flipped only some of the
    # target shapes while damaging neighbours. Halving it to 2.0 (v22) repaired
    # the damage but lost the fix entirely. With the counterweights now
    # present to absorb the collateral, the signal is raised past v21's level
    # so it flips the class consistently rather than sporadically.
    # Raised 5.0 -> 8.0 for the realtext era: the 558k-sequence corpus
    # dilutes this frame's share, and v37/v39 both regressed the round-6
    # FOX RVR GRV record with it at 5.0.
    ("abbrev_city", gen_abbrev_city, 8.0),
    # Raised 1.5 -> 2.5: the frame now also carries spelled forms (round-6
    # Franklin Road Southwest ruling), and the same weight would halve the
    # abbreviation exposure that won the original class.
    ("true_post_directional", gen_true_post_directional, 2.5),
    # Round-6 #4 (Highway 7 East, Hutchinson MN) -- see the generator.
    ("route_spelled_postdir", gen_route_spelled_postdir, 1.0),
    # Round-1 Lee Bird Fld ruling; realtext has zero LandmarkName rows.
    ("landmark_field", gen_landmark_field, 0.6),
    ("unit_abbrev", gen_unit_abbrev, 1.0),
    ("bare_street_no_number", gen_bare_street_no_number, 0.7),
    ("grid_predirectional", gen_grid_predirectional, 1.5),
    ("directional_multiword_street", gen_directional_multiword_street, 1.0),
    ("milepost_route", gen_milepost_route, 0.6),
    ("truncated_type", gen_truncated_type, 0.8),
    ("spelled_state", gen_spelled_state, 1.5),
    ("postdir_then_building", gen_postdir_then_building, 1.0),
    ("street_then_building", gen_street_then_building, 0.8),
    ("the_named_street", gen_the_named_street, 0.8),
    # National counterweight: real Census place names, doubled-weighted toward
    # the confusable-start class that the divergence scan showed breaking.
    ("national_cities", gen_national_cities, 6.0),
    # v24-scan counterweights: plain-city post-directionals (the KS/MO fix),
    # one-word spelled states, Wisconsin grid numbers.
    ("national_post_directional", gen_national_post_directional, 3.0),
    ("spelled_state_one_word", gen_spelled_state_one_word, 1.0),
    ("wisconsin_grid_number", gen_wisconsin_grid_number, 0.4),
    ("person_named_street", gen_person_named_street, 0.8),
    ("the_building", gen_the_building, 0.6),
    ("county_letter_road", gen_county_letter_road, 0.8),
    ("letter_avenue_grid", gen_letter_avenue_grid, 0.3),
    ("bare_route", gen_bare_route, 0.5),
    ("inner_directional_street", gen_inner_directional_street, 0.4),
    ("postdir_before_confusable_city", gen_postdir_before_confusable_city, 0.7),
    ("pike_and_xing", gen_pike_and_xing, 1.0),
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

    noised = []
    for r in rows:
        if rng.random() < 0.5:
            toks, labs = add_noise(rng, r["tokens"], r["labels"])
            if usaddress.tokenize(" ".join(toks)) == toks:
                noised.append({"tokens": toks, "labels": labs, "origin": r["origin"]})
                continue
        noised.append(r)
    rows = noised

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
