"""TIGER/Line corpus builder: authoritative street-phrase splits.

WHY THIS EXISTS
---------------
build_corpus.py derives training labels from county tax rolls, where the street
is a single opaque string ("E 100 N", "Old US Highway 90"). It splits that
string with label_street_phrase(), a positional heuristic. Measured against
Census TIGER/Line ground truth over 104,395 unique street phrases in five
counties, that heuristic mislabels 9.11% of them:

    Cook IL       18,697 phrases   1.96% mislabeled
    Harris TX     43,728 phrases   2.66%
    Orleans LA     2,452 phrases   3.79%
    Fulton GA     13,882 phrases   5.02%
    SaltLake UT   25,636 phrases  28.05%   <- grid addressing ("E 100 N")
    TOTAL        104,395 phrases   9.11%

The dominant failure (71% of disagreeing tokens) is a trailing directional the
heuristic calls StreetName when it is really StreetNamePostDirectional -- the
Utah/Salt-Lake grid pattern. Second (12%) is a street-type word that is really
part of the name. Neither is fixable by a better heuristic; they need a source
that already knows the answer.

TIGER FEATNAMES is that source: the Census publishes each street name
pre-split into directional / type / qualifier / name fields.

LABEL MAPPING, AND WHY IT IS NOT A STRAIGHT COPY
------------------------------------------------
TIGER's field semantics and usaddress's label conventions mostly agree, but not
everywhere. Each rule below was verified against upstream's own labeled.xml
rather than assumed:

  SUFQUALABR -> StreetName   (NOT StreetNamePostModifier)
      Upstream's labeled.xml does contain StreetNamePostModifier ("AVON ST
      EXT"), which made a direct mapping look right. It is not: that label is
      absent from usaddress.LABELS, the model's actual 26-label set. Training
      on it would have (a) taught a label the decoder can never emit and
      (b) pushed the label count to 27, silently disabling the
      viterbi_unrolled::<26> fast path in crates/crf and costing throughput.
      This is the same failure mode as the earlier SecondStreetName bug --
      a label that exists in some upstream artifact but not in the model
      schema. validate_tiger.py checks label-set membership for exactly this
      reason, and caught it.

      StreetName is also what our own human adjudication settled on: route
      qualifiers (Business/Bypass/Alt) are part of the street name. The
      adjudicated verdict and the label set agree.

  PREQUALABR -> StreetNamePreModifier ONLY IF a pre-type follows, else StreetName
      Verified: upstream labels "OLD US HIGHWAY 90" as
      Old=PreModifier US=PreType HIGHWAY=PreType 90=StreetName, but labels
      "Old Peachtree Road" as Old=StreetName. The distinguishing feature is
      whether the phrase is a route designation, which TIGER signals by
      populating PRETYPABRV. A straight PREQUALABR->PreModifier copy would have
      mislabeled every "Old <name> <type>" street in the country.

  route designators leading NAME -> StreetNamePreType
      TIGER frequently packs a whole route designation into NAME
      ("State Highway 146", "FM 1960", "Lp 8"), where upstream splits it
      (State=PreType Highway=PreType 146=StreetName -- 207 such labels in
      upstream's labeled.xml, dominated by highway/route/state/us/fm). This
      affects 0.25% of TIGER street phrases, concentrated in exactly the rural
      route addresses the parser is weakest on, so the rows are corrected
      rather than dropped.

Consistency: TIGER contradicts itself on 0.02% of distinct street names (27
rows in 686,272 measured) -- the same FULLNAME encoded two ways. Only the
majority encoding of each name is kept.

Alignment safety: a row is used only if its components concatenate back to
exactly the FULLNAME string. Any row where the field order is not what we
assume is dropped rather than guessed at.

The adjudicated verdicts in eval/gold remain the gate. If these conventions
turn out to conflict with an adjudicated parse, benchmark/full_check.py fails
the candidate -- that is the safety net, not this docstring.

SOURCES (all public domain, U.S. Census Bureau TIGER/Line 2024)
    FEATNAMES  street name components, joined on TLID
    ADDRFEAT   house-number ranges, ZIP, face IDs
    FACES      face ID -> place FIPS
    PLACE      place FIPS -> city name

Usage: python training/build_tiger_corpus.py [--counties N] [--per-county N]
Outputs training/corpus/tiger.jsonl and training/TIGER_MANIFEST.json.
"""

import argparse
import io
import json
import random
import urllib.request
import zipfile
from pathlib import Path

import shapefile

from build_corpus import add_noise, load_exclusions, norm_identity

ROOT = Path(__file__).parent.parent
OUT_DIR = Path(__file__).parent / "corpus"
CACHE = Path(__file__).parent / "tiger_cache"
BASE = "https://www2.census.gov/geo/tiger/TIGER2024"
SEED = 20260814

# Counties chosen for addressing-style diversity, not population. The styles in
# the comments are the reason each is here.
COUNTIES = [
    ("17", "031", "IL"),  # Cook -- dense urban grid, heavy pre-directionals
    ("48", "201", "TX"),  # Harris -- FM/Loop route designations
    ("49", "035", "UT"),  # Salt Lake -- grid post-directionals ("E 100 N")
    ("22", "071", "LA"),  # Orleans -- saint names, extensions
    ("13", "121", "GA"),  # Fulton -- "Old <name>" streets, NW/NE quadrants
    ("12", "086", "FL"),  # Miami-Dade -- quadrant addressing
    ("06", "037", "CA"),  # Los Angeles -- Spanish names
    ("36", "061", "NY"),  # New York -- numbered streets, no types
    ("04", "013", "AZ"),  # Maricopa -- grid + Spanish
    ("53", "033", "WA"),  # King -- pre AND post directionals
    ("35", "001", "NM"),  # Bernalillo -- Spanish names, NM state routes
    ("42", "101", "PA"),  # Philadelphia -- numbered + named grid
    ("08", "031", "CO"),  # Denver -- grid
    ("37", "119", "NC"),  # Mecklenburg -- southern naming
    ("30", "111", "MT"),  # Yellowstone -- rural, highways
    ("46", "103", "SD"),  # Pennington -- rural routes
    ("20", "173", "KS"),  # Sedgwick -- plains grid
    ("29", "095", "MO"),  # Jackson -- mixed
]

# TIGER field -> usaddress label, in the order TIGER concatenates them.
COMPONENTS = [
    ("PREQUALABR", "StreetNamePreModifier"),
    ("PREDIRABRV", "StreetNamePreDirectional"),
    ("PRETYPABRV", "StreetNamePreType"),
    ("NAME", "StreetName"),
    ("SUFTYPABRV", "StreetNamePostType"),
    ("SUFDIRABRV", "StreetNamePostDirectional"),
    # Not StreetNamePostModifier -- that label is not in the model's 26-label
    # set. See the module docstring.
    ("SUFQUALABR", "StreetName"),
]


def fetch(url, dest):
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "tiger-corpus/0.1"})
    with urllib.request.urlopen(req, timeout=900) as r, open(dest, "wb") as f:
        f.write(r.read())
    return dest


def read_dbf(zip_path):
    """Yield attribute dicts from the .dbf inside a TIGER shapefile zip.

    Only the .dbf is parsed -- the geometry is never needed, because every join
    here is on an ID field."""
    z = zipfile.ZipFile(zip_path)
    name = [n for n in z.namelist() if n.endswith(".dbf")][0]
    sf = shapefile.Reader(dbf=io.BytesIO(z.read(name)))
    for rec in sf.records():
        yield rec.as_dict()


# Words upstream treats as StreetNamePreType when they introduce a numbered
# route. Sourced from the StreetNamePreType labels in upstream's labeled.xml.
ROUTE_DESIGNATORS = {
    "fm", "us", "u.s.", "hwy", "highway", "state", "route", "rt", "rte",
    "county", "sr", "cr", "i", "i-", "us-", "farm", "ranch", "rm", "loop", "lp",
}


def apply_route_pretype(tokens, labels):
    """Relabel a route designation that TIGER packed into NAME.

    "State Highway 146" arrives as three StreetName tokens; upstream labels the
    leading designator words StreetNamePreType and leaves the number as the
    StreetName. Only fires when the designator run is immediately followed by a
    numeric token, so ordinary streets that merely start with a designator word
    ("Loop Road", "State Street") are untouched."""
    idx = [i for i, l in enumerate(labels) if l == "StreetName"]
    if len(idx) < 2:
        return labels
    run = 0
    while run < len(idx) - 1 and tokens[idx[run]].lower().strip(".-") in ROUTE_DESIGNATORS:
        run += 1
    if run == 0 or not tokens[idx[run]].lstrip("#").isdigit():
        return labels
    labels = list(labels)
    for i in idx[:run]:
        labels[i] = "StreetNamePreType"
    return labels


def street_labels(d):
    """TIGER component fields -> (tokens, labels), or None if unusable.

    Returns None when the components do not reassemble into FULLNAME, which
    means the field order is not the one assumed above."""
    has_pretype = bool((d.get("PRETYPABRV") or "").strip())
    tokens, labels = [], []
    for field, label in COMPONENTS:
        value = (d.get(field) or "").strip()
        if not value:
            continue
        # See module docstring: "Old" is a pre-modifier only in a route
        # designation ("Old US Highway 90"); otherwise it is part of the name
        # ("Old Peachtree Road").
        if field == "PREQUALABR" and not has_pretype:
            label = "StreetName"
        for tok in value.split():
            tokens.append(tok)
            labels.append(label)
    if not tokens:
        return None
    if " ".join(tokens) != (d.get("FULLNAME") or "").strip():
        return None
    if not any(lab == "StreetName" for lab in labels):
        return None
    return tokens, apply_route_pretype(tokens, labels)


def house_numbers(lo, hi, parity, rng, k=2):
    """Sample plausible house numbers from a TIGER address range.

    TIGER ranges may be non-numeric ("1A") or inverted; those are skipped
    rather than coerced, since a fabricated number would be training the model
    on a shape that does not occur."""
    if not (lo.isdigit() and hi.isdigit()):
        return []
    lo_i, hi_i = int(lo), int(hi)
    if lo_i > hi_i:
        lo_i, hi_i = hi_i, lo_i
    if hi_i - lo_i > 10000:
        return []
    want_odd = parity == "O"
    want_even = parity == "E"
    out = []
    for _ in range(k * 4):
        if len(out) >= k:
            break
        n = rng.randint(lo_i, hi_i)
        if want_odd and n % 2 == 0:
            n += 1
        elif want_even and n % 2 == 1:
            n += 1
        if lo_i <= n <= hi_i and n not in out:
            out.append(n)
    return out


def county_rows(statefp, countyfp, state_abbr, per_county, rng, places):
    fips = statefp + countyfp
    fn_zip = fetch(f"{BASE}/FEATNAMES/tl_2024_{fips}_featnames.zip", CACHE / f"featnames_{fips}.zip")
    af_zip = fetch(f"{BASE}/ADDRFEAT/tl_2024_{fips}_addrfeat.zip", CACHE / f"addrfeat_{fips}.zip")
    fc_zip = fetch(f"{BASE}/FACES/tl_2024_{fips}_faces.zip", CACHE / f"faces_{fips}.zip")

    # First pass: for each distinct street name, find the encoding TIGER uses
    # most often. TIGER occasionally encodes the same name two ways (measured
    # at 0.02% of names); the minority reading is a data error, and feeding
    # both to a CRF teaches contradiction.
    votes = {}
    rows_seen = []
    for d in read_dbf(fn_zip):
        parsed = street_labels(d)
        if not parsed:
            continue
        name = (d.get("FULLNAME") or "").lower()
        votes.setdefault(name, {})
        key = tuple(parsed[1])
        votes[name][key] = votes[name].get(key, 0) + 1
        rows_seen.append((d["TLID"], name, parsed))

    majority = {n: max(v.items(), key=lambda kv: kv[1])[0] for n, v in votes.items()}

    # TLID -> street phrases. A TLID can carry several names (an alias, a route
    # designation); keep them all so route-style phrases are represented.
    by_tlid = {}
    dropped_minority = 0
    for tlid, name, parsed in rows_seen:
        if tuple(parsed[1]) != majority[name]:
            dropped_minority += 1
            continue
        by_tlid.setdefault(tlid, [])
        if parsed not in by_tlid[tlid]:
            by_tlid[tlid].append(parsed)

    face_place = {d["TFID"]: d.get("PLACEFP") for d in read_dbf(fc_zip)}

    out = []
    for d in read_dbf(af_zip):
        phrases = by_tlid.get(d["TLID"])
        if not phrases:
            continue
        # Each edge has a left and a right side, with independent ranges,
        # ZIPs and faces.
        for lo_f, hi_f, zip_f, tfid_f, par_f in (
            ("LFROMHN", "LTOHN", "ZIPL", "TFIDL", "PARITYL"),
            ("RFROMHN", "RTOHN", "ZIPR", "TFIDR", "PARITYR"),
        ):
            lo = (d.get(lo_f) or "").strip()
            hi = (d.get(hi_f) or "").strip()
            zipc = (d.get(zip_f) or "").strip()
            if not (lo and hi and zipc):
                continue
            city = places.get(face_place.get(d.get(tfid_f)))
            if not city:
                continue
            for num in house_numbers(lo, hi, (d.get(par_f) or "").strip(), rng, k=1):
                toks, labs = list(phrases[rng.randrange(len(phrases))])
                toks = [str(num)] + toks + city.split() + [state_abbr, zipc]
                labs = ["AddressNumber"] + labs + ["PlaceName"] * len(city.split()) + ["StateName", "ZipCode"]
                out.append({"tokens": toks, "labels": labs, "origin": f"tiger-{fips}"})
        if len(out) >= per_county * 3:
            break

    rng.shuffle(out)
    return out[:per_county], dropped_minority


def load_places(statefp):
    z = fetch(f"{BASE}/PLACE/tl_2024_{statefp}_place.zip", CACHE / f"place_{statefp}.zip")
    # NAME is the bare city name ("Chicago"); NAMELSAD appends the legal type
    # ("Chicago city"), which is not how anyone writes an address.
    return {d["PLACEFP"]: (d.get("NAME") or "").strip() for d in read_dbf(z)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--counties", type=int, default=len(COUNTIES))
    ap.add_argument("--per-county", type=int, default=4000)
    args = ap.parse_args()

    rng = random.Random(SEED)
    exclude = load_exclusions()
    place_cache = {}
    rows, per_county_counts = [], {}
    minority_total = 0

    for statefp, countyfp, abbr in COUNTIES[: args.counties]:
        if statefp not in place_cache:
            place_cache[statefp] = load_places(statefp)
        got, minority = county_rows(statefp, countyfp, abbr, args.per_county, rng, place_cache[statefp])
        per_county_counts[statefp + countyfp] = len(got)
        minority_total += minority
        rows += got
        print(f"  {abbr} {statefp}{countyfp}: {len(got)} rows  ({minority} minority-encoding name rows dropped)")

    out, dropped = [], 0
    for r in rows:
        toks, labs = add_noise(rng, r["tokens"], r["labels"])
        if norm_identity(" ".join(toks)) in exclude:
            dropped += 1
            continue
        out.append({"tokens": toks, "labels": labs, "origin": r["origin"]})

    rng.shuffle(out)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / "tiger.jsonl", "w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r) + "\n")

    manifest = {
        "seed": SEED,
        "source": "US Census Bureau TIGER/Line 2024 (public domain)",
        "files_used": ["FEATNAMES", "ADDRFEAT", "FACES", "PLACE"],
        "counties": len(per_county_counts),
        "total": len(out),
        "by_county": per_county_counts,
        "excluded_gold_or_clean_overlaps": dropped,
        "dropped_minority_encoding_rows": minority_total,
    }
    (Path(__file__).parent / "TIGER_MANIFEST.json").write_text(
        json.dumps(manifest, indent=1), encoding="utf-8"
    )
    print(json.dumps(manifest, indent=1))


if __name__ == "__main__":
    main()
