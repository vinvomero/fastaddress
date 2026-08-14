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


def gen_bare_type_tail(rng):
    """'2350 WASHINGTON NE PL' — street type in final position with no city
    tail; the type must stay a post-type, not become a BuildingName."""
    pairs = [(str(rng.randint(100, 9999)), "AddressNumber"),
             (rng.choice(STREETS).upper(), "StreetName")]
    if rng.random() < 0.7:
        pairs.append((rng.choice(["NE", "NW", "SE", "SW", "N", "S", "E", "W"]),
                      "StreetNamePostDirectional"))
    pairs.append((rng.choice(TYPES).upper(), "StreetNamePostType"))
    return seq(pairs)


def gen_directional_placename(rng):
    """'... crt n east moline il 61244' — a directional word that begins a
    two-word city name stays PlaceName."""
    pairs = [(str(rng.randint(100, 9999)), "AddressNumber"),
             (rng.choice(STREETS).lower(), "StreetName"),
             (rng.choice(TYPES).lower(), "StreetNamePostType")]
    if rng.random() < 0.5:
        pairs.append((rng.choice(["n", "s", "e", "w"]), "StreetNamePostDirectional"))
    city_word = rng.choice(["east", "west", "north", "south"])
    second = rng.choice(["moline", "chicago", "haven", "point", "bend", "salem"])
    pairs += [(city_word, "PlaceName"), (second, "PlaceName"),
              (rng.choice(STATE_ABBR).lower(), "StateName"),
              (str(rng.randint(10000, 99999)), "ZipCode")]
    return seq(pairs)


def gen_pobox_dept(rng):
    """'po box 33701 dept 33701 sn francisco ca 94139' — abbreviated/misspelled
    city tokens stay PlaceName even when they look like subaddress types."""
    num = str(rng.randint(100, 99999))
    pairs = [("po", "USPSBoxType"), ("box", "USPSBoxType"), (num, "USPSBoxID")]
    if rng.random() < 0.6:
        pairs += [("dept", "SubaddressType"), (str(rng.randint(100, 99999)), "SubaddressIdentifier")]
    city = rng.choice([["sn", "francisco"], ["st", "louis"], ["ft", "worth"],
                       ["mt", "vernon"], ["n", "olmsted"]])
    pairs += [(c, "PlaceName") for c in city]
    pairs += [(rng.choice(STATE_ABBR).lower(), "StateName"),
              (str(rng.randint(10000, 99999)), "ZipCode")]
    return seq(pairs)


SAINT_NAMES = ["MARKS", "JAMES", "JOHNS", "PAULS", "CLAIR", "CHARLES", "NICHOLAS",
               "ANDREWS", "LOUIS", "ANNS", "MARYS", "PETERS"]
SAINT_TYPES = ["PLACE", "STREET", "AVENUE", "ROAD", "COURT", "TERRACE", "DRIVE"]
SAINT_CITIES = [["NEW", "YORK"], ["ST", "LOUIS"], ["BROOKLYN"], ["BALTIMORE"],
                ["NEW", "ORLEANS"], ["SAN", "FRANCISCO"]]


def gen_saint_street(rng):
    """'113 ST MARKS PLACE NEW YORK NY 10009' — the class v1 gets wrong and
    crashes on. Adjudicated correct labeling: the leading number is the address
    number, 'ST <Name>' is the street name, the thoroughfare word is the post
    type, and the city that follows is a PlaceName.
    """
    pairs = [(str(rng.randint(1, 999)), "AddressNumber"),
             ("ST", "StreetName"),
             (rng.choice(SAINT_NAMES), "StreetName"),
             (rng.choice(SAINT_TYPES), "StreetNamePostType")]
    city = rng.choice(SAINT_CITIES)
    pairs += [(c, "PlaceName") for c in city]
    pairs += [(rng.choice(STATE_ABBR), "StateName"),
              (str(rng.randint(10000, 99999)), "ZipCode")]
    if rng.random() < 0.3:  # lowercase and comma variants
        pairs = [(t.title(), l) for t, l in pairs]
    return seq(pairs)


def gen_saint_street_bare(rng):
    """Same class without the city tail: '92 ST MARKS PLACE'."""
    pairs = [(str(rng.randint(1, 999)), "AddressNumber"),
             ("ST", "StreetName"),
             (rng.choice(SAINT_NAMES), "StreetName"),
             (rng.choice(SAINT_TYPES), "StreetNamePostType")]
    return seq(pairs)


# The discriminator for this class is the TAIL word, not the head: "Valley West
# Mall" is a landmark while "Little River" is a city, and both open with nature
# words. So heads may be city-like, but the phrase must always close with an
# institutional tail — that is the signal the model needs to learn.
LM_HEADS = ["Municipal", "Regional", "Memorial", "International", "Metropolitan",
            "Executive", "Okemo", "Dothan", "Gulfport", "Logan", "Valley", "Highland",
            "Riverside", "Summit", "Heritage", "Gateway", "Northside", "Pioneer",
            "West", "East", "North", "South"]
LM_MIDS = ["Business", "Market", "County", "Metro", "Bird", "Blx", "Civic",
           "West", "East", "North", "South"]
LM_TAILS = ["Airport", "Mall", "Terminal", "Arena", "Depot", "Complex", "Concourse",
            "Aerodrome", "Fairgrounds", "Coliseum", "Center"]
# Vowel-dropped abbreviations are a distinctive orthographic signal for this class
# (the feature pipeline exposes has.vowels), and real tax rolls are full of them.
LM_ABBR = {"Airport": "Arprt", "Regional": "Rgnl", "Terminal": "Trmnl", "Field": "Fld",
           "Municipal": "Muncpl", "Center": "Cntr", "Station": "Statn", "Gulfport": "Glfprt",
           "Dothan": "Dthn", "Park": "Prk", "Highway": "Hghwy", "Junction": "Jct",
           "Memorial": "Mmrl", "Heights": "Hts", "Village": "Vlg"}


def gen_landmark(rng):
    """'Municipal Airport, Lincoln, NE 68524' / 'Valley West Mall, ...' — every
    token of the landmark phrase is LandmarkName, including the tail word."""
    words = [rng.choice(LM_HEADS)]
    if rng.random() < 0.55:
        words.append(rng.choice(LM_MIDS))
    words.append(rng.choice(LM_TAILS))
    pairs = []
    for i, w in enumerate(words):
        last = i == len(words) - 1
        pairs.append((w + ("," if last and rng.random() < 0.8 else ""), "LandmarkName"))
    if rng.random() < 0.85:
        pairs += city_tail(rng)
    return seq(pairs)


def gen_landmark_abbrev(rng):
    """'Glfprt Blx Rgnl Arpr, Gulfport, MS 39501' — vowel-dropped landmark
    tokens still label LandmarkName."""
    pool = list(LM_ABBR.values()) + ["Blx", "Arpr", "Trmnl", "Rgnl", "Fld", "Muni"]
    words = [rng.choice(pool) for _ in range(rng.randint(2, 4))]
    pairs = []
    for i, w in enumerate(words):
        last = i == len(words) - 1
        pairs.append((w + ("," if last and rng.random() < 0.8 else ""), "LandmarkName"))
    if rng.random() < 0.85:
        pairs += city_tail(rng)
    return seq(pairs)


def gen_intersection(rng):
    """'Alvy Prk And Hghwy # 54, Owensboro, KY 42301' — 'And' separates two
    named ways; the second way follows the separator."""
    # The model has no "Second*" labels — usaddress.tag() adds that prefix at
    # grouping time. Both ways carry ordinary street labels here. Shape taken
    # from the adjudicated parse of "Alvy Prk And Hghwy # 54": the route word
    # after the separator is a pre-type and the '# NN' route number that follows
    # is part of the street name.
    pairs = [(rng.choice(STREETS), "StreetName"),
             (rng.choice(["Prk", "Rd", "St", "Ave", "Ln"]), "StreetNamePostType"),
             ("And", "IntersectionSeparator")]
    if rng.random() < 0.55:
        pairs.append((rng.choice(["Hghwy", "Hwy", "Rte", "Route"]), "StreetNamePreType"))
        pairs.append(("#", "StreetName"))
        pairs.append((str(rng.randint(1, 99)) + ",", "StreetName"))
    else:
        pairs.append((rng.choice(["Main", "Broadway", "Market"]), "StreetName"))
        if rng.random() < 0.5:
            pairs.append((rng.choice(["Rd", "St", "Ave"]), "StreetNamePostType"))
    pairs += city_tail(rng)
    return seq(pairs)


# Split deliberately: most of these words are ALSO street types in usaddress's
# vocabulary (Flats, Commons, Manor, Estates, Terrace, Park, Square, Court...).
# Flooding building position with street-type words teaches the model that a
# street type can be a building name, which weakens "Blvd -> StreetNamePostType".
# Real addresses do use them ("Overlook Park Flats"), so keep them as a minority.
BLD_TAILS_SAFE = ["Lofts", "Towers", "Apartments", "Residences", "Villas", "House", "Suites"]
BLD_TAILS_AMBIG = ["Flats", "Commons", "Manor", "Estates", "Terrace"]
BLD_MIDS_SAFE = ["Vista", "Landing", "Crossing", "Pointe", "Annex"]
BLD_MIDS_AMBIG = ["Park", "Square", "Court", "Garden", "Station"]


def gen_street_then_building(rng):
    """'3705 N Overlook Blvd Overlook Park Flats, Portland, OR 97227' — a
    COMPLETE street address followed by a building name. The building labels
    must not bleed backward over the street portion.

    This is the contextual opposite of the landmark generators: a landmark
    phrase stands alone, while a BuildingName phrase trails a full street
    address. That context is the discriminator the model has to learn.
    """
    street_word = rng.choice(STREETS)
    pairs = [(str(rng.randint(100, 9999)), "AddressNumber")]
    if rng.random() < 0.6:
        pairs.append((rng.choice(["N", "S", "E", "W"]), "StreetNamePreDirectional"))
    pairs += [(street_word, "StreetName"),
              (rng.choice(["Blvd", "Ave", "St", "Rd", "Dr"]), "StreetNamePostType")]
    # The hard case is the ECHO: the building phrase repeats the street name
    # ("Overlook Blvd Overlook Park Flats"), which is what makes the labels
    # bleed together. Make it the default, not a coin flip — the street type
    # token is the boundary the model has to learn.
    bld = [street_word] if rng.random() < 0.8 else [rng.choice(STREETS)]
    if rng.random() < 0.75:
        pool = BLD_MIDS_AMBIG if rng.random() < 0.3 else BLD_MIDS_SAFE
        bld.append(rng.choice(pool))
    bld.append(rng.choice(BLD_TAILS_AMBIG if rng.random() < 0.25 else BLD_TAILS_SAFE))
    for i, w in enumerate(bld):
        last = i == len(bld) - 1
        pairs.append((w + ("," if last and rng.random() < 0.8 else ""), "BuildingName"))
    pairs += city_tail(rng)
    return seq(pairs)


TWO_WORD_CITIES = [["Little", "River"], ["Round", "Pond"], ["Miles", "City"],
                   ["Des", "Moines"], ["Grand", "Rapids"], ["Palm", "Beach"],
                   ["Cedar", "Falls"], ["Green", "Bay"], ["Bay", "City"],
                   ["Fort", "Wayne"], ["Long", "Beach"], ["Santa", "Rosa"]]


def gen_street_then_twoword_city(rng):
    """'150 Citizens Circle Little River, South Carolina 29566' — the CONTRAST
    case for gen_street_then_building: here the words after the street type are
    a two-word CITY, not a building.

    Without this pair the model learns "anything after the street type is a
    BuildingName" and mislabels cities. The discriminator is what follows: a
    building phrase is followed by a city, while a city is followed by the
    state. Both shapes must be present for either to be learned correctly.
    """
    pairs = [(str(rng.randint(100, 9999)), "AddressNumber")]
    if rng.random() < 0.4:
        pairs.append((rng.choice(["N", "S", "E", "W"]), "StreetNamePreDirectional"))
    pairs += [(rng.choice(STREETS), "StreetName"),
              (rng.choice(["Circle", "Blvd", "Ave", "St", "Rd", "Dr", "Way"]), "StreetNamePostType")]
    city = rng.choice(TWO_WORD_CITIES)
    for i, w in enumerate(city):
        last = i == len(city) - 1
        pairs.append((w + ("," if last and rng.random() < 0.8 else ""), "PlaceName"))
    if rng.random() < 0.5:
        st = rng.choice(STATE_FULL)
        pairs += [(t, "StateName") for t in st.split()]
    else:
        pairs.append((rng.choice(STATE_ABBR), "StateName"))
    pairs.append((str(rng.randint(10000, 99999)), "ZipCode"))
    return seq(pairs)


def gen_dc_state(rng):
    """'99 s spruce road apt. #4b, D.C. 20500' — 'D.C.' immediately before a ZIP
    is the state-equivalent (USPS standardizes District of Columbia to DC), not
    a city name. Adjudicated round 2."""
    pairs = [(str(rng.randint(1, 9999)), "AddressNumber")]
    if rng.random() < 0.5:
        pairs.append((rng.choice(["n", "s", "e", "w"]), "StreetNamePreDirectional"))
    pairs += [(rng.choice(STREETS).lower(), "StreetName"),
              (rng.choice(["road", "street", "ave", "place"]), "StreetNamePostType")]
    if rng.random() < 0.5:
        pairs += [("apt.", "OccupancyType"), ("#" + str(rng.randint(1, 99)) + rng.choice(["a", "b", "c"]), "OccupancyIdentifier")]
    if rng.random() < 0.5:
        pairs.append(("Washington,", "PlaceName"))
    pairs += [(rng.choice(["D.C.", "DC", "D.C.,"]), "StateName"),
              (str(rng.randint(20001, 20599)), "ZipCode")]
    return seq(pairs)


def gen_rural_route_truncated(rng):
    """'RR 422 Box, Douglassville, PA 19518' — the TRUNCATED rural-route form,
    where 'Box' has no number after it.

    The complete form ('HC 284 Box 27') labels the route as a GROUP
    (USPSBoxGroupType/ID) with the box number as USPSBoxType/ID — that shape is
    generated by gen_hc_rr_box. When the box number is missing, the adjudicated
    reading treats the route itself as the box. Collapsing the two shapes into
    one generator taught the wrong labels for complete forms, so they stay
    separate deliberately.
    """
    pairs = [(rng.choice(["RR", "R.R.", "RTE"]), "USPSBoxType"),
             (str(rng.randint(1, 999)), "USPSBoxID"),
             ("Box" + ("," if rng.random() < 0.5 else ""), "USPSBoxType")]
    pairs += city_tail(rng)
    return seq(pairs)


def gen_fractional_street(rng):
    """'33 1/2 AVE' — fractional street NAMES are real (33 1/2 Ave S, Fargo).
    With the leading number as the address number and AVE as the type, the
    fraction is the street name. Adjudicated round 2."""
    pairs = [(str(rng.randint(1, 199)), "AddressNumber"),
             (rng.choice(["1/2", "3/4", "1/4", "2/3"]), "StreetName"),
             (rng.choice(["AVE", "ST", "AVENUE", "STREET"]), "StreetNamePostType")]
    if rng.random() < 0.45:
        pairs.append((rng.choice(["N", "S", "E", "W"]), "StreetNamePostDirectional"))
    if rng.random() < 0.6:
        pairs += city_tail(rng)
    return seq(pairs)


def gen_abbrev_directional_city(rng):
    """'977 PLEASANT STREET, N. ORANGE, NJ 07052' — an abbreviated directional
    that opens a city name is part of the PlaceName, not a street directional."""
    pairs = [(str(rng.randint(100, 9999)), "AddressNumber"),
             (rng.choice(STREETS).upper(), "StreetName"),
             (rng.choice(["STREET", "AVENUE", "ROAD", "DRIVE"]), "StreetNamePostType")]
    pairs[-1] = (pairs[-1][0] + ",", pairs[-1][1])
    d = rng.choice(["N.", "S.", "E.", "W.", "NO.", "SO."])
    city = rng.choice(["ORANGE", "PLAINFIELD", "BRUNSWICK", "BERGEN", "HAVEN", "CHICAGO"])
    pairs += [(d, "PlaceName"), (city + ",", "PlaceName"),
              (rng.choice(STATE_ABBR), "StateName"),
              (str(rng.randint(10000, 99999)), "ZipCode")]
    return seq(pairs)


GENERATORS = [
    (gen_landmark, 1800),
    (gen_landmark_abbrev, 1500),
    (gen_street_then_building, 2200),
    (gen_street_then_twoword_city, 1800),
    (gen_abbrev_directional_city, 1000),
    (gen_dc_state, 1200),
    (gen_rural_route_truncated, 900),
    (gen_fractional_street, 1000),
    (gen_intersection, 900),
    (gen_saint_street, 2500),
    (gen_saint_street_bare, 800),
    (gen_bare_type_tail, 1200),
    (gen_directional_placename, 1200),
    (gen_pobox_dept, 1200),
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
