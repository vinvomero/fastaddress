"""Training-corpus builder (plan M-U3).

Assembles token/label training sequences from:
  1. Upstream usaddress training XMLs (MIT; fine-grained convention verified)
  2. Distant supervision: component-level county records composed into raw
     strings with deterministic labels and label-preserving noise transforms

Outputs training/corpus/corpus.jsonl ({tokens, labels, origin}) plus a
manifest. Enforces: no record whose normalized identity appears in the gold
candidates or clean eval set. Deterministic under SEED.

One-time build tooling — no retraining cadence is implied (see plan Scope
Boundaries and origin R12).
"""

import csv
import json
import random
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

import usaddress

ROOT = Path(__file__).parent.parent
OUT_DIR = Path(__file__).parent / "corpus"
SEED = 20260813

UPSTREAM = {
    "labeled.xml": None,  # all rows
    "openaddress_us_ia_linn.xml": 50000,
}
UPSTREAM_BASE = "https://raw.githubusercontent.com/datamade/usaddress/main/training/"

COUNTY_CAP = 20000  # per source

DIRECTIONS = usaddress.DIRECTIONS
STREET_NAMES = usaddress.STREET_NAMES


def norm_identity(s):
    return "".join(c for c in s.upper() if c.isalnum())


def load_exclusions():
    ids = set()
    for path in (ROOT / "eval" / "gold" / "candidates.jsonl", ROOT / "eval" / "clean" / "clean.jsonl"):
        with open(path, encoding="utf-8") as f:
            for line in f:
                ids.add(norm_identity(json.loads(line)["raw"]))
    return ids


# ---------- upstream XML ----------

def upstream_rows():
    rows = []
    for name, cap in UPSTREAM.items():
        with urllib.request.urlopen(UPSTREAM_BASE + name, timeout=300) as resp:
            root = ET.fromstring(resp.read().decode("utf-8"))
        file_rows = []
        for addr in root.iter("AddressString"):
            tokens, labels = [], []
            for el in addr:
                tok = (el.text or "").strip()
                if tok:
                    tokens.append(tok)
                    labels.append(el.tag)
            if tokens:
                file_rows.append({"tokens": tokens, "labels": labels, "origin": name})
        if cap:
            file_rows = file_rows[:cap]
        rows += file_rows
        print(f"upstream {name}: {len(file_rows)}")
    return rows


# ---------- distant supervision ----------

def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "corpus-builder/0.1"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.load(resp)


def label_street_phrase(tokens):
    """Deterministic labels for a street phrase from a structured street field.
    Conservative: returns None when unsure (row is dropped)."""
    if not tokens:
        return None
    if any(not t.replace("-", "").replace("'", "").isalnum() for t in tokens):
        return None
    labels = [None] * len(tokens)
    i = 0
    if len(tokens) > 1 and tokens[0].lower() in DIRECTIONS:
        labels[0] = "StreetNamePreDirectional"
        i = 1
    j = len(tokens)
    if j - i >= 2 and tokens[j - 1].lower() in DIRECTIONS and tokens[j - 2].lower() in STREET_NAMES:
        labels[j - 1] = "StreetNamePostDirectional"
        labels[j - 2] = "StreetNamePostType"
        j -= 2
    elif j - i >= 2 and tokens[j - 1].lower() in STREET_NAMES:
        labels[j - 1] = "StreetNamePostType"
        j -= 1
    if i >= j:
        return None  # nothing left to be the street name proper
    for k in range(i, j):
        labels[k] = "StreetName"
    return labels


def compose(parts):
    """parts: list of (text, label|list-of-labels-per-token). Tokenizes each
    part and assigns labels; returns tokens, labels."""
    tokens, labels = [], []
    for text, lab in parts:
        toks = text.split()
        if not toks:
            continue
        if isinstance(lab, list):
            if len(lab) != len(toks):
                return None
            tokens += toks
            labels += lab
        else:
            tokens += toks
            labels += [lab] * len(toks)
    return tokens, labels


def allegheny_rows(cap):
    url = (
        "https://data.wprdc.org/api/3/action/datastore_search"
        f"?resource_id=65855e14-549e-4992-b5be-d629afc676fa&limit={cap}&offset=6000"
    )
    out = []
    for r in get_json(url)["result"]["records"]:
        num = (r.get("PROPERTYHOUSENUM") or "").strip()
        street = (r.get("PROPERTYADDRESS") or "").strip()
        unit = (r.get("PROPERTYUNIT") or "").strip()
        city = (r.get("PROPERTYCITY") or "").strip()
        state = (r.get("PROPERTYSTATE") or "").strip()
        zipc = (r.get("PROPERTYZIP") or "").strip()
        if not (num.isdigit() and street and city and state and zipc):
            continue
        slabels = label_street_phrase(street.split())
        if not slabels:
            continue
        parts = [(num, "AddressNumber"), (street, slabels)]
        if unit and unit.isdigit():
            parts += [("UNIT", "OccupancyType"), (unit, "OccupancyIdentifier")]
        parts += [(city, "PlaceName"), (state, "StateName"), (zipc, "ZipCode")]
        row = compose(parts)
        if row:
            out.append({"tokens": row[0], "labels": row[1], "origin": "allegheny-ds"})
    print(f"allegheny distant: {len(out)}")
    return out


def cook_rows(cap):
    params = urllib.parse.quote(
        "$select=prop_address_full,prop_address_city_name,prop_address_state,prop_address_zipcode_1"
        f"&$where=year='2024' AND prop_address_full IS NOT NULL AND prop_address_zipcode_1 IS NOT NULL"
        f"&$limit={cap}&$order=pin DESC", safe="$=&,()' ").replace(" ", "%20")
    out = []
    for r in get_json(f"https://datacatalog.cookcountyil.gov/resource/3723-97qp.json?{params}"):
        full = (r.get("prop_address_full") or "").strip()
        city = (r.get("prop_address_city_name") or "").strip()
        state = (r.get("prop_address_state") or "IL").strip()
        zipc = (r.get("prop_address_zipcode_1") or "").strip()
        toks = full.split()
        if len(toks) < 2 or not toks[0].isdigit() or not (city and zipc):
            continue
        slabels = label_street_phrase(toks[1:])
        if not slabels:
            continue
        parts = [(toks[0], "AddressNumber"), (" ".join(toks[1:]), slabels),
                 (city, "PlaceName"), (state, "StateName"), (zipc, "ZipCode")]
        row = compose(parts)
        if row:
            out.append({"tokens": row[0], "labels": row[1], "origin": "cook-ds"})
    print(f"cook distant: {len(out)}")
    return out


# ---------- noise transforms (label-preserving) ----------

def add_noise(rng, tokens, labels):
    tokens = list(tokens)
    labels = list(labels)
    style = rng.random()
    if style < 0.3:
        tokens = [t.lower() for t in tokens]
    elif style < 0.5:
        tokens = [t.title() for t in tokens]
    # comma after the last street token and after the city block
    if rng.random() < 0.4:
        for i in range(len(tokens) - 1):
            if labels[i].startswith("StreetName") and not labels[i + 1].startswith("StreetName"):
                tokens[i] = tokens[i] + ","
                break
    if rng.random() < 0.4:
        for i in range(len(tokens) - 1):
            if labels[i] == "PlaceName" and labels[i + 1] != "PlaceName":
                tokens[i] = tokens[i] + ","
                break
    # component dropout: drop state, or zip, or city+state+zip tail
    p = rng.random()
    def drop(pred):
        keep = [(t, l) for t, l in zip(tokens, labels) if not pred(l)]
        return [t for t, _ in keep], [l for _, l in keep]
    if p < 0.15:
        tokens, labels = drop(lambda l: l == "StateName")
    elif p < 0.25:
        tokens, labels = drop(lambda l: l == "ZipCode")
    elif p < 0.32:
        tokens, labels = drop(lambda l: l in ("PlaceName", "StateName", "ZipCode"))
    return tokens, labels


def main():
    rng = random.Random(SEED)
    exclude = load_exclusions()
    rows = upstream_rows() + allegheny_rows(COUNTY_CAP) + cook_rows(COUNTY_CAP)

    out, dropped_excluded = [], 0
    for r in rows:
        if r["origin"].endswith("-ds"):
            toks, labs = add_noise(rng, r["tokens"], r["labels"])
        else:
            toks, labs = r["tokens"], r["labels"]
        raw = " ".join(toks)
        if norm_identity(raw) in exclude:
            dropped_excluded += 1
            continue
        out.append({"tokens": toks, "labels": labs, "origin": r["origin"]})

    rng.shuffle(out)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / "corpus.jsonl", "w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r) + "\n")

    from collections import Counter
    counts = Counter(r["origin"] for r in out)
    manifest = {
        "seed": SEED,
        "total": len(out),
        "by_origin": dict(counts),
        "excluded_gold_or_clean_overlaps": dropped_excluded,
    }
    (Path(__file__).parent / "MANIFEST.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print(json.dumps(manifest, indent=1))


if __name__ == "__main__":
    main()
