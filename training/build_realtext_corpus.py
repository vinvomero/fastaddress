#!/usr/bin/env python3
"""Real-text alignment corpus builder (plan 2026-08-16-001, unit U1).

WHY THIS EXISTS
---------------
Training distribution != evaluation distribution: composed/synthetic training
text produced composed-tier dominance and only free-text parity on gold-2.
This builder turns millions of reachable REAL owner-mailing lines (the same
government sources behind eval/gold2) into labeled training rows -- with
labels recovered by ALIGNMENT, never by heuristic splitting.

ALIGNMENT LADDER (conservative; no heuristic interior splits)
-------------------------------------------------------------
Per fetched row (free-text LINE + the source's own separate city/state/zip):
 1. Tail labels come from the source's own fields: city tokens -> PlaceName,
    state -> StateName, zip -> ZipCode. Insane tails (non-alpha city, bad
    state code, malformed zip) drop the row.
 2. From the LINE: leading house number (digits, or digits+letter) ->
    AddressNumber. Pure PO Box lines ("PO BOX 123", "P O BOX", "POB") ->
    USPSBoxType/USPSBoxID per the clean-set convention (every type token is
    USPSBoxType; '#' and the id are USPSBoxID). "RR 1 BOX 116" ->
    USPSBoxGroupType/USPSBoxGroupID/USPSBoxType/USPSBoxID. One trailing unit
    ("APT 4B", "STE 200", "# 5") -> OccupancyType+OccupancyIdentifier; '#'
    carries the identifier label (validate_synth rule).
 3. The remaining interior street phrase must EXACTLY match a TIGER FEATNAMES
    street record for the row's mail state (modulo case and punctuation).
    On match, the record's pre-split components label the AS-WRITTEN tokens
    (via build_tiger_corpus.street_labels, which carries the verified
    conventions: SUFQUALABR->StreetName, PREQUALABR conditional,
    apply_route_pretype). Street rows whose mail state differs from the
    source state are dropped (their geography index is not loaded).
 4. No match -> DROP the row. Yield reported per source.
 5. Dedupe: normalized identity (uppercase alnum collapse) must not collide
    with gold-1, gold-2, clean, or earlier corpus rows. Tokens must
    round-trip usaddress.tokenize.

The corpus is real text as fetched -- abbreviations, casing, quirks survive;
only labels are added. No noise transforms.

GEOGRAPHY INDEX
---------------
FULLNAME (lowercased, punctuation-stripped, per-token) -> majority component
split, built from the national FEATNAMES cache
(C:/cargo-target/us-address-parser/tiger_national_cache). The whole mail
state is indexed (superset of the source county -- owners mail from anywhere
in the state), majority-vote across counties like build_tiger_corpus does
within one.

All cache/checkpoints live under C:/cargo-target/us-address-parser/
realtext_cache -- NEVER under the OneDrive repo.

Usage:
  python training/build_realtext_corpus.py --list
  python training/build_realtext_corpus.py --fetch ST | --fetch-all
  python training/build_realtext_corpus.py --align ST | --align-all
  python training/build_realtext_corpus.py --assemble
  python training/build_realtext_corpus.py --all          # fetch+align+assemble
Resumable: delete a checkpoint/aligned/index file to redo that piece.
"""

import argparse
import gzip
import json
import random
import re
import sys
import time
import zlib
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "benchmark"))
sys.path.insert(0, str(ROOT / "training"))

import usaddress  # noqa: E402

import fetch_gold2 as fg  # noqa: E402  (source configs + HTTP machinery)
from build_tiger_corpus import read_dbf, street_labels  # noqa: E402

CACHE = Path("C:/cargo-target/us-address-parser/realtext_cache")
CKPT_DIR = CACHE / "checkpoints"
ALIGNED_DIR = CACHE / "aligned"
INDEX_DIR = CACHE / "state_index"
FEATNAMES_DIR = Path(
    "C:/cargo-target/us-address-parser/tiger_national_cache/featnames"
)
OUT_JSONL = ROOT / "training" / "corpus" / "realtext.jsonl"
MANIFEST_OUT = ROOT / "training" / "REALTEXT_MANIFEST.json"

SEED = 20260816
PAGE = 2000
VALID_LABELS = set(usaddress.LABELS)

STATE_FIPS = {
    "AL": "01", "AK": "02", "AZ": "04", "AR": "05", "CA": "06", "CO": "08",
    "CT": "09", "DE": "10", "DC": "11", "FL": "12", "GA": "13", "HI": "15",
    "ID": "16", "IL": "17", "IN": "18", "IA": "19", "KS": "20", "KY": "21",
    "LA": "22", "ME": "23", "MD": "24", "MA": "25", "MI": "26", "MN": "27",
    "MS": "28", "MO": "29", "MT": "30", "NE": "31", "NV": "32", "NH": "33",
    "NJ": "34", "NM": "35", "NY": "36", "NC": "37", "ND": "38", "OH": "39",
    "OK": "40", "OR": "41", "PA": "42", "RI": "44", "SC": "45", "SD": "46",
    "TN": "47", "TX": "48", "UT": "49", "VT": "50", "VA": "51", "WA": "53",
    "WV": "54", "WI": "55",
}
VALID_STATES = set(STATE_FIPS)

# ---------------------------------------------------------------------------
# Sources. Each references fetch_gold2.CONFIG[st] for endpoint/type/where and
# adds: sampling target, how the LINE is chosen, and how the tail is read.
#   tail "fields"   : cfg's separate city/st/zip fields
#   tail "csz_st"   : dedicated combined "CITY ST" field + separate zip field
#   tail "csz_full" : dedicated combined "CITY ST ZIP" field
# Only sources whose tail is carried in the source's own fields are eligible;
# single-blob sources (WI PSTLADRESS, WV FullOwnerAddress, MN own_add_l*,
# MD MAILTOADD, GA/LA/NY/RI/PA/DC/NV) are excluded -- their tails would need
# heuristic splitting of the address line itself.
# ---------------------------------------------------------------------------
SOURCES = {
    "CT": {"want": 12000},
    "MI": {"want": 10000},
    "FL": {"want": 22000},
    "MA": {"want": 15000},
    "VT": {"want": 12000},
    "NC": {"want": 22000},
    "MT": {"want": 10000},
    "ME": {"want": 12000},
    "IN": {"want": 10000},
    "TX": {"want": 10000},
    "AZ": {"want": 10000},
    "OH": {"want": 10000},
    "TN": {"want": 10000},
    "VA": {"want": 8000},
    "ND": {"want": 8000},
    "AL": {"want": 8000},
    "OK": {"want": 8000},
    "SD": {"want": 8000},
    "CO": {"want": 6000},
    "SC": {"want": 8000, "line_mode": "join"},  # MailApt is a unit field
    "IL": {"want": 8000},
    "MO": {"want": 8000},
    "NM": {"want": 8000},
    "IA": {"want": 8000},
    "AK": {"want": 8000},
    "KS": {"want": 5000},   # small jurisdiction (~6k rows)
    "NE": {"want": 8000},
    "WA": {"want": 10000, "tail": "csz_st", "csz_field": "KCTP_CTYST"},
    "NJ": {"want": 12000, "tail": "csz_st", "csz_field": "CITY_STATE"},
    "OR": {"want": 8000, "tail": "csz_full", "csz_field": "M_CITYSTZIP"},
}

AGG_PICKS = 12  # counties sampled per statewide-aggregate source


def log(msg):
    print(msg, flush=True)


def src_cfg(st):
    return fg.CONFIG[st]


def line_fields(st):
    cfg, src = src_cfg(st), SOURCES[st]
    csz = src.get("csz_field")
    return [f for f in cfg["addr_fields"] if f != csz]


def out_fields(st):
    cfg, src = src_cfg(st), SOURCES[st]
    fields = list(cfg["addr_fields"])
    for key in ("city", "st", "zip", "county_field"):
        if cfg.get(key):
            fields.append(cfg[key])
    csz = src.get("csz_field")
    if csz and csz not in fields:
        fields.append(csz)
    return fields


def state_rng(st):
    return random.Random(SEED ^ zlib.crc32(st.encode()))


# ---------------------------------------------------------------------------
# Fetch phase: bulk sampling, checkpointed. Reuses fetch_gold2's HTTP helpers.
# ---------------------------------------------------------------------------

def paged_arcgis(cfg, rng, want, fields, extra_where=None):
    where = cfg.get("where", "1=1")
    if extra_where:
        where = f"({where}) AND ({extra_where})"
    d = fg.arcgis_query(cfg["endpoint"], {"where": where, "returnCountOnly": "true"})
    n = d.get("count", 0)
    rows = []
    if not n:
        return rows, 0
    if cfg.get("objectid_sampling"):
        window = 6000
        tries = 0
        while len(rows) < want and tries < want // 500 + 25:
            tries += 1
            r = rng.randrange(1, max(2, n))
            d = fg.arcgis_query(cfg["endpoint"], {
                "where": f"OBJECTID >= {r} AND OBJECTID < {r + window}",
                "outFields": ",".join(fields), "returnGeometry": "false",
                "resultRecordCount": str(PAGE),
            })
            rows.extend(f["attributes"] for f in d.get("features", []))
            time.sleep(0.25)
        return rows[:want], n
    chunks = 4
    per_chunk = want // chunks + 1
    max_off = max(1, n - per_chunk)
    offsets = sorted(rng.randrange(max_off) for _ in range(chunks))
    for off in offsets:
        got = 0
        while got < per_chunk:
            d = fg.arcgis_query(cfg["endpoint"], {
                "where": where, "outFields": ",".join(fields),
                "returnGeometry": "false",
                "resultOffset": str(off + got),
                "resultRecordCount": str(min(PAGE, per_chunk - got)),
            })
            feats = d.get("features", [])
            if not feats:
                break
            rows.extend(f["attributes"] for f in feats)
            got += len(feats)
            time.sleep(0.25)
        if len(rows) >= want:
            break
    return rows[:want], n


def paged_socrata(cfg, rng, want, fields):
    base_where = cfg.get("where")
    p = {"$select": "count(*) as n"}
    if base_where:
        p["$where"] = base_where
    n = int(fg.get_json(fg.soc_url(cfg, p))[0]["n"])
    rows = []
    chunks = 3
    per_chunk = want // chunks + 1
    max_off = max(1, n - per_chunk)
    offsets = sorted(rng.randrange(max_off) for _ in range(chunks))
    for off in offsets:
        got = 0
        while got < per_chunk:
            limit = min(5000, per_chunk - got)
            p = {"$select": ",".join(fields), "$limit": str(limit),
                 "$offset": str(off + got), "$order": ":id"}
            if base_where:
                p["$where"] = base_where
            batch = fg.get_json(fg.soc_url(cfg, p))
            if not batch:
                break
            rows.extend(batch)
            got += len(batch)
            time.sleep(0.4)
            if len(batch) < limit:
                break
    return rows[:want], n


def paged_aggregate(cfg, rng, want, fields):
    counties = fg.agg_counties(cfg)
    picks = rng.sample(counties, min(AGG_PICKS, len(counties)))
    per = want // len(picks) + 1
    rows, total = [], 0
    for c in picks:
        cval = str(c).replace("'", "''")
        cw = f"{cfg['county_field']} = '{cval}'"
        try:
            sub, n = paged_arcgis(cfg, rng, per, fields, extra_where=cw)
        except Exception as e:  # noqa: BLE001 -- keep the other counties
            log(f"    county {c!r} failed: {str(e)[:120]}")
            continue
        rows.extend(sub)
        total += n
    return rows, total


def extract_row(st, attrs):
    """Reduce a fetched attribute dict to the fields alignment needs."""
    cfg, src = src_cfg(st), SOURCES[st]
    lines = []
    for f in line_fields(st):
        v = fg.clean_part(attrs.get(f))
        v = re.sub(r"\s+", " ", v).strip()
        if not v:
            continue
        if lines and v.upper() == lines[-1].upper():
            continue  # data-entry duplication (seen in ME ADB)
        lines.append(v)
    if not lines:
        return None
    sp = cfg.get("skip_pattern")
    if sp and re.search(sp, " ".join(lines)):
        return None
    out = {"lines": lines}
    tail = src.get("tail", "fields")
    if tail == "fields":
        out["city"] = fg.clean_part(attrs.get(cfg["city"]))
        out["st"] = fg.clean_part(attrs.get(cfg["st"]))
        out["zip"] = fg.clean_part(attrs.get(cfg["zip"]))
    else:
        out["csz"] = re.sub(r"\s+", " ", fg.clean_part(attrs.get(src["csz_field"]))).strip()
        out["zip"] = fg.clean_part(attrs.get(cfg["zip"])) if cfg.get("zip") else ""
    return out


def fetch_state(st, force=False):
    ck = CKPT_DIR / f"{st}.json.gz"
    if ck.exists() and not force:
        log(f"[{st}] fetch checkpoint exists, skipping")
        return
    cfg, src = src_cfg(st), SOURCES[st]
    rng = state_rng(st)
    want = src["want"]
    fields = out_fields(st)
    log(f"[{st}] fetching up to {want} rows from {cfg['dataset']}")
    t0 = time.time()
    status = "fetched"
    try:
        if cfg["type"] == "socrata":
            raw, total = paged_socrata(cfg, rng, want, fields)
        elif cfg.get("aggregate"):
            raw, total = paged_aggregate(cfg, rng, want, fields)
        else:
            raw, total = paged_arcgis(cfg, rng, want, fields)
    except Exception as e:  # noqa: BLE001
        log(f"[{st}] FETCH FAILED: {str(e)[:200]}")
        raw, total, status = [], 0, f"error: {str(e)[:200]}"
    rows = []
    for attrs in raw:
        r = extract_row(st, attrs)
        if r:
            rows.append(r)
    CKPT_DIR.mkdir(parents=True, exist_ok=True)
    with gzip.open(ck, "wt", encoding="utf-8") as f:
        json.dump({"state": st, "status": status, "dataset": cfg["dataset"],
                   "dataset_total": total, "raw_fetched": len(raw),
                   "rows": rows}, f)
    log(f"[{st}] {status}: {len(rows)} usable rows of {len(raw)} fetched "
        f"(dataset={total}) in {time.time() - t0:.0f}s")


# ---------------------------------------------------------------------------
# TIGER state index: normalized FULLNAME -> majority component-split labels.
# ---------------------------------------------------------------------------

def norm_tok(t):
    return re.sub(r"[^a-z0-9]", "", t.lower())


def build_state_index(st):
    idx_file = INDEX_DIR / f"{st}.json.gz"
    if idx_file.exists():
        with gzip.open(idx_file, "rt", encoding="utf-8") as f:
            return json.load(f)
    fips = STATE_FIPS[st]
    zips = sorted(FEATNAMES_DIR.glob(f"tl_2024_{fips}*_featnames.zip"))
    if not zips:
        raise RuntimeError(f"no FEATNAMES files for state {st} ({fips}) in cache")
    log(f"[{st}] building TIGER index from {len(zips)} county files ...")
    t0 = time.time()
    votes = {}
    for z in zips:
        try:
            records = read_dbf(z)
            for d in records:
                parsed = street_labels(d)
                if not parsed:
                    continue
                toks, labs = parsed
                normed = [norm_tok(t) for t in toks]
                if any(not t for t in normed):
                    continue
                key = " ".join(normed)
                votes.setdefault(key, Counter())[tuple(labs)] += 1
        except Exception as e:  # noqa: BLE001 -- one bad county zip
            log(f"    skipping {z.name}: {str(e)[:120]}")
    index = {k: list(max(v.items(), key=lambda kv: kv[1])[0])
             for k, v in votes.items()}
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    with gzip.open(idx_file, "wt", encoding="utf-8") as f:
        json.dump(index, f)
    log(f"[{st}] index: {len(index)} distinct street names "
        f"({time.time() - t0:.0f}s)")
    return index


# ---------------------------------------------------------------------------
# Alignment
# ---------------------------------------------------------------------------

UNIT_TYPES = {
    "APT", "APARTMENT", "STE", "SUITE", "UNIT", "BLDG", "BUILDING", "FL",
    "FLR", "FLOOR", "RM", "ROOM", "LOT", "TRLR", "TRAILER", "DEPT", "SPC",
    "SPACE", "PMB", "OFC", "OFFICE", "SLIP", "HANGAR", "BSMT",
}
NUM_RE = re.compile(r"^\d+[A-Za-z]?$")
CITY_RE = re.compile(r"^[A-Za-z][A-Za-z .'\-]*$")
ST_TOK_RE = re.compile(r"^[A-Za-z]{2}[.,]?$")


def tok_key(t):
    return re.sub(r"[^A-Z0-9#]", "", t.upper())


def ident_ok(tok):
    k = re.sub(r"[^A-Za-z0-9/\-]", "", tok)
    if not k or not re.fullmatch(r"[A-Za-z0-9/\-]+", k):
        return False
    return any(c.isdigit() for c in k) or len(k) <= 2


def sane_zip(z):
    z = z.strip()
    if re.fullmatch(r"\d{5}(-\d{4})?", z) or re.fullmatch(r"\d{9}", z):
        return z
    m = re.fullmatch(r"(\d{5})[-. ]*", z)
    if m:
        return m.group(1)
    m = re.fullmatch(r"(\d{5})\.0", z)
    if m:
        return m.group(1)
    return None


def label_box(toks):
    """Whole-line PO Box / RR / HC forms -> labels, else None.

    Clean-set convention: every type token is USPSBoxType ("PO" "Box" both);
    '#' and the id carry USPSBoxID. RR/HC: group type/id then box type/id.
    """
    keys = [tok_key(t) for t in toks]
    if any(not k for k in keys):
        return None
    # RR 1 BOX 116 / HC 65 BOX 21
    if (len(keys) == 4 and keys[0] in ("RR", "HC")
            and keys[1].isdigit() and keys[2] == "BOX" and ident_ok(toks[3])):
        return ["USPSBoxGroupType", "USPSBoxGroupID", "USPSBoxType", "USPSBoxID"]
    # leading box-type run: PO BOX / P O BOX / POB / POBOX / BOX
    i = 0
    while i < len(keys) and keys[i] in ("PO", "P", "O", "POB", "POBOX", "BOX"):
        i += 1
    if i == 0 or keys[i - 1] not in ("BOX", "POB", "POBOX"):
        return None
    labels = ["USPSBoxType"] * i
    rest = toks[i:]
    if not rest:
        return None
    if tok_key(rest[0]) == "#" or rest[0] == "#":
        labels.append("USPSBoxID")
        rest = rest[1:]
    if len(rest) != 1 or not ident_ok(rest[0]):
        return None
    labels.append("USPSBoxID")
    return labels


def strip_unit(toks):
    """One trailing unit group -> (street_toks, unit_toks, unit_labels)."""
    n = len(toks)
    k = [tok_key(t) for t in toks]
    if n >= 4 and k[-2] == "#" and k[-3] in UNIT_TYPES and ident_ok(toks[-1]):
        return toks[:-3], toks[-3:], [
            "OccupancyType", "OccupancyIdentifier", "OccupancyIdentifier"]
    if n >= 3 and k[-2] in UNIT_TYPES and ident_ok(toks[-1]):
        return toks[:-2], toks[-2:], ["OccupancyType", "OccupancyIdentifier"]
    if n >= 3 and k[-2] == "#" and ident_ok(toks[-1]):
        return toks[:-2], toks[-2:], ["OccupancyIdentifier", "OccupancyIdentifier"]
    return toks, [], []


def pick_line(lines):
    """Choose the delivery line: the LAST line that starts with a house
    number or a box form. If the immediately following (final) line is a pure
    unit line, append it. Returns (line, kind) or (None, None)."""
    idx, kind = None, None
    for i, l in enumerate(lines):
        toks = l.split()
        if not toks:
            continue
        if NUM_RE.match(toks[0]) and len(toks) >= 2:
            idx, kind = i, "street"
        elif tok_key(toks[0]) in ("PO", "P", "POB", "POBOX", "BOX", "RR", "HC"):
            idx, kind = i, "box"
    if idx is None:
        return None, None
    line = lines[idx]
    if (kind == "street" and idx + 1 == len(lines) - 1):
        nxt = lines[idx + 1].split()
        if nxt and (tok_key(nxt[0]) in UNIT_TYPES or nxt[0] == "#"):
            line = line + " " + lines[idx + 1]
    return line, kind


def parse_tail(row, st, src):
    """-> (city_tokens, state_token, mail_state, zip_token) or None."""
    tail = src.get("tail", "fields")
    if tail == "fields":
        city, stf, zf = row.get("city", ""), row.get("st", ""), row.get("zip", "")
        city = re.sub(r"\s+", " ", city).strip()
        stf = stf.strip()
        if not (city and CITY_RE.fullmatch(city) and 1 <= len(city.split()) <= 4):
            return None
        if not re.fullmatch(r"[A-Za-z]{2}", stf) or stf.upper() not in VALID_STATES:
            return None
        z = sane_zip(zf)
        if not z:
            return None
        return usaddress.tokenize(city), stf, stf.upper(), z
    csz = row.get("csz", "")
    toks = usaddress.tokenize(csz) if csz else []
    if tail == "csz_full":
        if len(toks) < 3:
            return None
        z = sane_zip(toks[-1])
        st_tok, city_toks = toks[-2], toks[:-2]
    else:  # csz_st: combined "CITY ST" + separate zip field
        if len(toks) < 2:
            return None
        z = sane_zip(row.get("zip", ""))
        st_tok, city_toks = toks[-1], toks[:-1]
    if not z:
        return None
    if not ST_TOK_RE.fullmatch(st_tok):
        return None
    mail_state = re.sub(r"[^A-Za-z]", "", st_tok).upper()
    if mail_state not in VALID_STATES:
        return None
    city = " ".join(t.strip(",.") for t in city_toks)
    if not (city and CITY_RE.fullmatch(city) and 1 <= len(city_toks) <= 4):
        return None
    return city_toks, st_tok, mail_state, z


def align_row(row, st, src, index, drops):
    tail = parse_tail(row, st, src)
    if tail is None:
        drops["bad_tail"] += 1
        return None
    city_toks, st_tok, mail_state, zip_tok = tail

    line, kind = pick_line(row["lines"])
    if line is None:
        drops["no_line_start"] += 1
        return None
    line_toks = usaddress.tokenize(line)
    if not line_toks:
        drops["no_line_start"] += 1
        return None

    if kind == "box":
        labels = label_box(line_toks)
        if labels is None:
            drops["box_malformed"] += 1
            return None
        toks = list(line_toks)
        labs = list(labels)
    else:
        if mail_state != st:
            drops["out_of_state"] += 1
            return None
        num = line_toks[0]
        if not NUM_RE.fullmatch(num):
            drops["no_line_start"] += 1
            return None
        street_toks, unit_toks, unit_labels = strip_unit(line_toks[1:])
        if not street_toks:
            drops["interior_empty"] += 1
            return None
        normed = [norm_tok(t) for t in street_toks]
        if any(not t for t in normed):
            drops["interior_punct"] += 1
            return None
        key = " ".join(normed)
        street_labs = index.get(key)
        if street_labs is None:
            drops["interior_unmatched"] += 1
            return None
        toks = [num] + list(street_toks) + list(unit_toks)
        labs = ["AddressNumber"] + list(street_labs) + list(unit_labels)

    toks = toks + list(city_toks) + [st_tok, zip_tok]
    labs = labs + ["PlaceName"] * len(city_toks) + ["StateName", "ZipCode"]

    if usaddress.tokenize(" ".join(toks)) != toks:
        drops["tokenize_mismatch"] += 1
        return None
    if any(l not in VALID_LABELS for l in labs):
        drops["invalid_label"] += 1
        return None
    return {"tokens": toks, "labels": labs, "origin": f"rt-{st}",
            "source": src_cfg(st)["dataset"], "kind": kind}


def align_state(st, force=False):
    out_file = ALIGNED_DIR / f"{st}.jsonl"
    stats_file = ALIGNED_DIR / f"{st}.stats.json"
    if out_file.exists() and stats_file.exists() and not force:
        log(f"[{st}] aligned output exists, skipping")
        return
    ck = CKPT_DIR / f"{st}.json.gz"
    if not ck.exists():
        log(f"[{st}] no fetch checkpoint -- fetch first")
        return
    with gzip.open(ck, "rt", encoding="utf-8") as f:
        payload = json.load(f)
    rows = payload["rows"]
    if not rows:
        log(f"[{st}] checkpoint has 0 rows ({payload['status']})")
        ALIGNED_DIR.mkdir(parents=True, exist_ok=True)
        out_file.write_text("", encoding="utf-8")
        stats_file.write_text(json.dumps({
            "state": st, "dataset": payload["dataset"], "raw": 0, "aligned": 0,
            "drops": {}, "status": payload["status"]}), encoding="utf-8")
        return
    index = build_state_index(st)
    src = SOURCES[st]
    drops = Counter()
    aligned, seen = [], set()
    for row in rows:
        rec = align_row(row, st, src, index, drops)
        if rec is None:
            continue
        nid = fg.norm_identity(" ".join(rec["tokens"]))
        if nid in seen:
            drops["dup_in_state"] += 1
            continue
        seen.add(nid)
        aligned.append(rec)
    ALIGNED_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        for rec in aligned:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    n_box = sum(1 for r in aligned if r["kind"] == "box")
    stats = {"state": st, "dataset": payload["dataset"], "raw": len(rows),
             "aligned": len(aligned), "aligned_box": n_box,
             "aligned_street": len(aligned) - n_box,
             "yield_pct": round(100.0 * len(aligned) / len(rows), 1),
             "drops": dict(drops), "status": payload["status"]}
    stats_file.write_text(json.dumps(stats, indent=1), encoding="utf-8")
    log(f"[{st}] aligned {len(aligned)}/{len(rows)} "
        f"({stats['yield_pct']}%; street={stats['aligned_street']} "
        f"box={n_box}) drops={dict(drops)}")


# ---------------------------------------------------------------------------
# Assembly: global dedupe, assertions, corpus + manifest
# ---------------------------------------------------------------------------

def load_exclusions():
    files = [ROOT / "eval" / "gold" / "candidates.jsonl",
             ROOT / "eval" / "gold2" / "candidates.jsonl",
             ROOT / "eval" / "clean" / "clean.jsonl"]
    ids = set()
    for p in files:
        if not p.exists():
            raise RuntimeError(f"exclusion file missing: {p}")
        with open(p, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    ids.add(fg.norm_identity(json.loads(line)["raw"]))
    return ids


def assemble():
    excl = load_exclusions()
    log(f"exclusion set: {len(excl)} identities (gold-1 + gold-2 + clean)")
    per_state, rows = {}, []
    seen = set()
    dup_global = eval_overlap = 0
    for stats_file in sorted(ALIGNED_DIR.glob("*.stats.json")):
        st = stats_file.stem.split(".")[0]
        stats = json.loads(stats_file.read_text(encoding="utf-8"))
        kept = 0
        with open(ALIGNED_DIR / f"{st}.jsonl", encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                nid = fg.norm_identity(" ".join(rec["tokens"]))
                if nid in excl:
                    eval_overlap += 1
                    continue
                if nid in seen:
                    dup_global += 1
                    continue
                seen.add(nid)
                rec.pop("kind", None)
                rows.append(rec)
                kept += 1
        stats["kept_after_global_dedupe"] = kept
        per_state[st] = stats

    rng = random.Random(SEED)
    rng.shuffle(rows)

    # ---- build-time assertions -------------------------------------------
    problems = []
    states = {r["origin"][3:] for r in rows}
    for r in rows:
        for t, l in zip(r["tokens"], r["labels"]):
            if l not in VALID_LABELS:
                problems.append(f"invalid label {l!r} in {' '.join(r['tokens'])[:60]}")
            if t == "#" and l not in ("USPSBoxID", "OccupancyIdentifier", "AddressNumber"):
                problems.append(f"'#' not identifier-labeled in {' '.join(r['tokens'])[:60]}")
        if len(r["tokens"]) != len(r["labels"]):
            problems.append(f"token/label length mismatch: {' '.join(r['tokens'])[:60]}")
    # tokenize round-trip, re-verified on final rows
    bad_rt = sum(1 for r in rows if usaddress.tokenize(" ".join(r["tokens"])) != r["tokens"])
    if bad_rt:
        problems.append(f"{bad_rt} rows fail tokenize round-trip")
    overlap_now = sum(1 for r in rows if fg.norm_identity(" ".join(r["tokens"])) in excl)
    if overlap_now:
        problems.append(f"{overlap_now} rows overlap eval sets")
    if len(states) < 25:
        problems.append(f"only {len(states)} states (< 25)")
    if len(rows) < 50000:
        problems.append(f"only {len(rows)} rows (< 50000)")
    if problems:
        for p in problems[:20]:
            log(f"ASSERTION FAILED: {p}")
        log(f"{len(problems)} assertion failures -- corpus NOT written")
        sys.exit(1)

    OUT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSONL, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    label_counts = Counter(l for r in rows for l in r["labels"])
    manifest = {
        "seed": SEED,
        "built": time.strftime("%Y-%m-%d"),
        "method": "alignment (tail from source fields; interior exact-match "
                  "vs TIGER FEATNAMES; box/unit by adjudicated conventions; "
                  "no heuristic interior splits; unmatched rows dropped)",
        "tiger": "US Census Bureau TIGER/Line 2024 FEATNAMES (public domain)",
        "total_rows": len(rows),
        "states": sorted(states),
        "n_states": len(states),
        "dropped_global_dup": dup_global,
        "dropped_eval_overlap": eval_overlap,
        "label_counts": dict(label_counts.most_common()),
        "per_source": per_state,
    }
    MANIFEST_OUT.write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    log(f"\nWrote {len(rows)} rows from {len(states)} states -> {OUT_JSONL}")
    log(f"Manifest -> {MANIFEST_OUT}")
    log(f"Global dedupe: {dup_global} cross-source dups, "
        f"{eval_overlap} eval overlaps removed")

    # sample rows for the report: a box row, a unit row, and plain streets
    def show(r):
        pairs = " ".join(f"{t}/{l}" for t, l in zip(r["tokens"], r["labels"]))
        log(f"  [{r['origin']}] {pairs}")
    log("\nSample rows (as fetched, labels aligned):")
    shown, kinds_shown = 0, set()
    for want_kind in ("box", "unit", "plain", "plain2", "plain3"):
        for r in rows:
            is_box = "USPSBoxID" in r["labels"]
            has_unit = "OccupancyIdentifier" in r["labels"]
            k = "box" if is_box else ("unit" if has_unit else "plain")
            if want_kind.startswith("plain"):
                k = "plain" if k == "plain" else k
            if (want_kind == k or (want_kind.startswith("plain") and k == "plain")) \
                    and r["origin"] not in kinds_shown:
                show(r)
                kinds_shown.add(r["origin"])
                shown += 1
                break
        if shown >= 5:
            break


# ---------------------------------------------------------------------------

def status():
    for st in sorted(SOURCES):
        ck = CKPT_DIR / f"{st}.json.gz"
        sf = ALIGNED_DIR / f"{st}.stats.json"
        fetched = "ckpt" if ck.exists() else "-"
        if sf.exists():
            s = json.loads(sf.read_text(encoding="utf-8"))
            log(f"{st}: {fetched}  aligned {s['aligned']}/{s['raw']} "
                f"({s.get('yield_pct', 0)}%)")
        else:
            log(f"{st}: {fetched}  (not aligned)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--fetch", metavar="STATE")
    ap.add_argument("--fetch-all", action="store_true")
    ap.add_argument("--align", metavar="STATE")
    ap.add_argument("--align-all", action="store_true")
    ap.add_argument("--assemble", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if args.list:
        for st in sorted(SOURCES):
            cfg = src_cfg(st)
            log(f"{st}: want={SOURCES[st]['want']:6d}  "
                f"tail={SOURCES[st].get('tail', 'fields'):8s}  {cfg['dataset']}")
        return
    if args.status:
        status()
        return
    if args.fetch:
        fetch_state(args.fetch.upper(), force=args.force)
        return
    if args.align:
        align_state(args.align.upper(), force=args.force)
        return
    if args.fetch_all or args.all:
        for st in sorted(SOURCES):
            try:
                fetch_state(st, force=args.force)
            except Exception as e:  # noqa: BLE001
                log(f"[{st}] fetch crashed: {str(e)[:200]}")
    if args.align_all or args.all:
        for st in sorted(SOURCES):
            try:
                align_state(st, force=args.force)
            except Exception as e:  # noqa: BLE001
                log(f"[{st}] align crashed: {str(e)[:200]}")
    if args.assemble or args.all:
        assemble()
    if not any(vars(args).values()):
        ap.print_help()


if __name__ == "__main__":
    main()
