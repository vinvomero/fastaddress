"""U3: the national coverage-floor corpus, one generator family.

Composition:
- RETAINED frames import unchanged from synth_error_classes (each carries its
  adjudication citation there); their label distributions are pinned by the
  characterization snapshot in training/snapshots/errclass_pre_national.json.
- Three vocabulary-limited generators (national_cities, national_post_
  directional, postdir_before_confusable_city) are SUPERSEDED by inventory-
  driven versions below -- same frames, national vocabulary, guaranteed floor.
- Five NEW frames come one-for-one from the U1 taxonomy of the spent binding
  split (benchmark/results/final-split-taxonomy.md), with the U2 inventories
  saying which surface each form lives on: TIGER's canonical abbreviations
  (Cll/Cam/Via/Rue) sit in type position; the spelled vernacular forms
  (Calle/Camino/Paseo/Cmo) live INSIDE street names.

Coverage floor: every multi-word city appears at least FLOOR_CITY times;
every retained inventory form appears at least FLOOR_FORM times. Sampling
below the floor is the v28 lesson (1.5 exposures taught nothing).

Usage: python training/synth_national.py
Writes training/corpus/national.jsonl + NATIONAL_MANIFEST.json.
"""

import collections
import json
import random
from pathlib import Path

import usaddress

from build_corpus import add_noise, load_exclusions, norm_identity
from synth_error_classes import (  # retained frames + shared vocab, citations there
    DIRS, PLAIN_CITIES, STREET_WORDS, TYPES, GENERATORS as SEC_GENERATORS, seq,
)

OUT = Path(__file__).parent / "corpus" / "national.jsonl"
INV = json.loads((Path(__file__).parent / "vocab_inventories.json").read_text(encoding="utf-8"))
OLD_VOCAB = json.loads((Path(__file__).parent / "vocab_cities.json").read_text(encoding="utf-8"))
SEED = 20260816
FLOOR_CITY = 3  # 2 let 8 cities lose both copies to noise tail-drops
FLOOR_FORM = 60

SUPERSEDED = {"national_cities", "national_post_directional", "postdir_before_confusable_city"}
RETAINED = [(n, f, w) for n, f, w in SEC_GENERATORS if n not in SUPERSEDED]

STATE_OF = {}  # state fips -> abbr, for city entries
_FIPS_ABBR = {"01":"AL","02":"AK","04":"AZ","05":"AR","06":"CA","08":"CO","09":"CT","10":"DE",
              "11":"DC","12":"FL","13":"GA","15":"HI","16":"ID","17":"IL","18":"IN","19":"IA",
              "20":"KS","21":"KY","22":"LA","23":"ME","24":"MD","25":"MA","26":"MI","27":"MN",
              "28":"MS","29":"MO","30":"MT","31":"NE","32":"NV","33":"NH","34":"NJ","35":"NM",
              "36":"NY","37":"NC","38":"ND","39":"OH","40":"OK","41":"OR","42":"PA","44":"RI",
              "45":"SC","46":"SD","47":"TN","49":"UT","48":"TX","50":"VT","51":"VA","53":"WA",
              "54":"WV","55":"WI","56":"WY","72":"PR"}

CITIES = [(name, _FIPS_ABBR.get(fp, "XX")) for name, fp in INV["cities_multiword"]
          if _FIPS_ABBR.get(fp)]

DIRWORDS = {"north", "south", "east", "west"}
CONF_NONDIR = [(c, st) for c, st in CITIES
               if c.split()[0].lower() not in DIRWORDS
               and c.split()[0].lower() in {"new", "lake", "saint", "st", "mount", "mt",
                                            "port", "grand", "park", "fort", "ft"}]
PLAIN_SINGLE = [tuple(x) for x in OLD_VOCAB.get("plain", [])]  # contradiction-filtered

# Type-position forms: TIGER's canonical abbreviations, frequency >= 200 so
# junk never enters, verified to include Cll/Cam/Via/Rue/FM/Hwy/Rte.
PRE_FORMS = sorted([k for k, v in INV["street_type_pre"].items()
                    if v >= 200 and k.replace("-", "").replace(".", "").isalpha()],
                   key=lambda k: -INV["street_type_pre"][k])[:40]
SUF_FORMS = sorted([k for k, v in INV["street_type_suf"].items()
                    if v >= 200 and k.isalpha()],
                   key=lambda k: -INV["street_type_suf"][k])[:80]

# Name-internal spelled forms: verified present as name-lead words in the
# national inventory (Calle 1402 counties, Camino 2008, Paseo 1612, Cmo 17...).
# "Rancho" removed: it was an invention, not taxonomy -- in the U1 data
# Rancho leads CITY names (Rancho San Diego, Rancho Santa Fe), and teaching it
# as a street lead broke the clean record "PO Box 9580 Rancho Santa Fe" in
# every grid cell. Rancho-led cities get boosted coverage instead.
NAME_LEAD_SPANISH = [w for w in ("Calle", "Camino", "Paseo", "Avenida", "Vista",
                                 "Corte", "Cmo", "Via", "Vía")
                     if INV["name_lead_words"].get(w)]
SPANISH_SECOND = ["Hacienda", "Amistoso", "Sur", "Norte", "Grande", "Bonita", "Del Sol",
                  "Verde", "Linda", "Sereno", "Alegre", "Tortola", "Luna", "Feliz"]


def tail(rng, p, city, st):
    p += [(w, "PlaceName") for w in city.split()]
    shape = rng.random()
    if shape < 0.5:
        p += [(st, "StateName"), (f"{rng.randint(1000, 99999):05d}", "ZipCode")]
    elif shape < 0.75:
        p += [(st, "StateName")]
    elif shape < 0.9:
        p += [(f"{rng.randint(1000, 99999):05d}", "ZipCode")]
    return p


def gen_cities_coverage(rng, n):
    """Every multi-word city in the country, >= FLOOR_CITY times. Supersedes
    national_cities; same four tail shapes; conf-start cities weighted x2."""
    conf2 = [e for e in CITIES if e[0].split()[0].lower() in
             DIRWORDS | {"new", "lake", "saint", "st", "mount", "mt", "port",
                         "grand", "park", "fort", "ft", "box", "little", "cross",
                         "black", "fair", "sun", "bella", "sans", "rancho"}]
    schedule = CITIES * FLOOR_CITY + conf2 * 2
    rng.shuffle(schedule)
    out = []
    for i in range(max(n, len(schedule))):
        city, st = schedule[i % len(schedule)]
        p = [(str(rng.randint(1, 9999)), "AddressNumber"),
             (rng.choice(STREET_WORDS).split()[0].title(), "StreetName"),
             (rng.choice(TYPES), "StreetNamePostType")]
        out.append(seq(tail(rng, p, city, st)))
    return out


def gen_postdir_plain_city(rng, n):
    """type + DIR + plain single-word city: the directional survives.
    Supersedes national_post_directional (same frame, same contradiction-
    filtered pool); ordinal street names half the time (the Wichita shape)."""
    out = []
    for _ in range(n):
        city, st = PLAIN_SINGLE[rng.randrange(len(PLAIN_SINGLE))]
        if rng.random() < 0.5:
            k = rng.randint(1, 99)
            sufx = "th" if 10 <= k % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(k % 10, "th")
            name = f"{k}{sufx}"
        else:
            name = rng.choice(STREET_WORDS).split()[0]
        p = [(str(rng.randint(1, 9999)), "AddressNumber")]
        if rng.random() < 0.5:
            p.append((rng.choice(["N", "S", "E", "W"]), "StreetNamePreDirectional"))
        p += [(name, "StreetName"), (rng.choice(TYPES), "StreetNamePostType"),
              (rng.choice(DIRS), "StreetNamePostDirectional"), (city, "PlaceName")]
        if rng.random() < 0.8:
            p.append((st, "StateName"))
        if rng.random() < 0.7:
            p.append((f"{rng.randint(1000, 99999):05d}", "ZipCode"))
        out.append(seq(p))
    return out


def gen_postdir_before_confusable(rng, n):
    """type + DIR + non-directional confusable city (N New Orleans class).
    Supersedes the old version; direction-first cities still excluded (the
    v30 Maine lesson)."""
    out = []
    for _ in range(n):
        city, st = CONF_NONDIR[rng.randrange(len(CONF_NONDIR))]
        p = [(str(rng.randint(1, 9999)), "AddressNumber"),
             (rng.choice(STREET_WORDS).split()[0].title(), "StreetName"),
             (rng.choice(["Cv", "Ct", "Dr", "Ln", "St", "Ave"]), "StreetNamePostType"),
             (rng.choice(["N", "S", "E", "W"]), "StreetNamePostDirectional")]
        out.append(seq(tail(rng, p, city, st)))
    return out


def gen_pretype_forms(rng, n):
    """Every high-frequency TIGER pre-type abbreviation in type position:
    num + PRE(SNPreType) + name(SN). Covers Cll/Cam/Via/Rue/FM/Hwy/Byu/Arroyo.
    U1 both-wrong classes 1-2 (421+ records) are exactly this frame."""
    schedule = PRE_FORMS * max(FLOOR_FORM, n // max(len(PRE_FORMS), 1))
    rng.shuffle(schedule)
    out = []
    for i in range(min(n, len(schedule))):
        pre = schedule[i]
        name = (rng.choice(SPANISH_SECOND) if pre in ("Cll", "Cam", "Via", "Vía", "Avenida", "Cll ")
                else str(rng.randint(1, 999)) if pre in ("Hwy", "FM", "Rte", "SR", "I-")
                else rng.choice(STREET_WORDS).split()[0].title())
        p = [(str(rng.randint(1, 9999)), "AddressNumber")]
        if rng.random() < 0.3:
            p.append((rng.choice(["N", "S", "E", "W"]), "StreetNamePreDirectional"))
        p.append((pre, "StreetNamePreType"))
        p += [(w, "StreetName") for w in name.split()]
        if rng.random() < 0.3:
            p.append((rng.choice(["Rd", "Dr", "Ave"]), "StreetNamePostType"))
        city, st = PLAIN_SINGLE[rng.randrange(len(PLAIN_SINGLE))]
        out.append(seq(tail(rng, p, city, st)))
    return out


def gen_spanish_name_internal(rng, n):
    """Spelled Spanish forms INSIDE the name (empty type fields in TIGER):
    'Cmo Amistoso', 'Camino Del Sol' -- the whole phrase is StreetName.
    Verified present as name-lead words in the national inventory."""
    out = []
    for _ in range(n):
        lead = rng.choice(NAME_LEAD_SPANISH)
        second = rng.choice(SPANISH_SECOND)
        p = [(str(rng.randint(1, 9999)), "AddressNumber")]
        if rng.random() < 0.4:
            p.append((rng.choice(["N", "S", "E", "W"]), "StreetNamePreDirectional"))
        p += [(w, "StreetName") for w in (lead + " " + second).split()]
        city, st = rng.choice([("Tucson", "AZ"), ("Catalina Foothills", "AZ"),
                               ("Chula Vista", "CA"), ("Santa Fe", "NM"),
                               ("El Paso", "TX"), ("Jamul", "CA")])
        out.append(seq(tail(rng, p, city, st)))
    return out


def gen_ut_numeric_street(rng, n):
    """Utah grid where the street NAME is a number + direction word:
    '11044 S 5250 West St' -> 5250(SN) West(SN) St(PostType). 83 U1 records."""
    out = []
    for _ in range(n):
        p = [(str(rng.randint(1, 13999)), "AddressNumber"),
             (rng.choice(["N", "S", "E", "W"]), "StreetNamePreDirectional"),
             (str(rng.choice([250, 680, 1300, 2700, 4800, 5250, 8520, 11400])), "StreetName"),
             (rng.choice(["West", "North", "South", "East"]), "StreetName")]
        if rng.random() < 0.7:
            p.append((rng.choice(["St", "Dr", "Rd"]), "StreetNamePostType"))
        city, st = rng.choice([("Payson", "UT"), ("Pleasant Grove", "UT"), ("Magna", "UT"),
                               ("Provo", "UT"), ("Orem", "UT"), ("Lehi", "UT")])
        out.append(seq(tail(rng, p, city, st)))
    return out


def gen_county_letterdigit(rng, n):
    """'Cty A6' / 'Cty V63': the whole phrase is the street NAME per TIGER
    (empty type fields). 47 U1 records, Illinois."""
    out = []
    for _ in range(n):
        code = rng.choice("ABCEHJKMNVWX") + str(rng.randint(1, 99))
        p = [(str(rng.randint(1, 39999)), "AddressNumber"),
             (rng.choice(["Cty", "Co", "CTH"]), "StreetName"), (code, "StreetName")]
        city, st = rng.choice([("Zion", "IL"), ("Lake Villa", "IL"), ("Antioch", "IL"),
                               ("Waukesha", "WI"), ("Oshkosh", "WI")])
        out.append(seq(tail(rng, p, city, st)))
    return out


def gen_name_final_typeword(rng, n):
    """'Idler Grove' with NO suffix: the type-word is part of the name.
    16 U1 records. Modest weight -- this fights the true-suffix prior."""
    finals = ["Grove", "Point", "Ridge", "Vista", "Crossing", "Landing", "Bend", "Glen"]
    out = []
    for _ in range(n):
        p = [(str(rng.randint(1, 9999)), "AddressNumber"),
             (rng.choice(STREET_WORDS).split()[0].title(), "StreetName"),
             (rng.choice(finals), "StreetName")]
        city, st = PLAIN_SINGLE[rng.randrange(len(PLAIN_SINGLE))]
        out.append(seq(tail(rng, p, city, st)))
    return out


NATIONAL_GENERATORS = [
    ("cities_coverage", gen_cities_coverage, None),          # size set by floor
    ("postdir_plain_city", gen_postdir_plain_city, 9000),
    ("postdir_before_confusable", gen_postdir_before_confusable, 3000),
    ("pretype_forms", gen_pretype_forms, 6000),
    ("spanish_name_internal", gen_spanish_name_internal, 3000),
    ("ut_numeric_street", gen_ut_numeric_street, 2400),
    ("county_letterdigit", gen_county_letterdigit, 1500),
    ("name_final_typeword", gen_name_final_typeword, 1200),
]
RETAINED_SCALE = 2400  # per retained frame; distributions pinned by snapshot


def main():
    rng = random.Random(SEED)
    exclude = load_exclusions()
    rows, counts = [], {}
    for name, fn, size in NATIONAL_GENERATORS:
        got = fn(rng, size or 0)
        counts[name] = len(got)
        rows += [dict(r, origin=f"nat-{name}") for r in got]
    for name, fn, _w in RETAINED:
        got = fn(rng, RETAINED_SCALE)
        counts[f"retained:{name}"] = len(got)
        rows += [dict(r, origin=f"ret-{name}") for r in got]

    out, dropped_tok, dropped_ex = [], 0, 0
    for r in rows:
        toks, labs = r["tokens"], r["labels"]
        if rng.random() < 0.5:
            toks, labs = add_noise(rng, toks, labs)
        if usaddress.tokenize(" ".join(toks)) != toks:
            dropped_tok += 1
            continue
        if norm_identity(" ".join(toks)) in exclude:
            dropped_ex += 1
            continue
        out.append({"tokens": toks, "labels": labs, "origin": r["origin"]})
    rng.shuffle(out)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r) + "\n")
    manifest = {"seed": SEED, "total": len(out), "by_generator": counts,
                "dropped_tokenizer_mismatch": dropped_tok, "dropped_eval_overlap": dropped_ex,
                "floors": {"city": FLOOR_CITY, "form": FLOOR_FORM},
                "pre_forms": len(PRE_FORMS), "suf_forms": len(SUF_FORMS),
                "cities": len(CITIES), "plain_single": len(PLAIN_SINGLE)}
    (Path(__file__).parent / "NATIONAL_MANIFEST.json").write_text(
        json.dumps(manifest, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in manifest.items() if k != "by_generator"}, indent=1))


if __name__ == "__main__":
    main()
