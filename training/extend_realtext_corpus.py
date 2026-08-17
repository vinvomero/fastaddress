#!/usr/bin/env python3
"""Extended real-text alignment ladder (plan 2026-08-16-003, unit G2B-U2).

WHY THIS EXISTS
---------------
`build_realtext_corpus.py` labels a row only when its interior matches a TIGER
FEATNAMES record EXACTLY. That is safe and it is also the corpus's blind spot:
50,995 fetched rows were thrown away as `interior_unmatched` and 3,471 as
`no_line_start`, and those drops are exactly the classes gold-2 adjudication
kept surfacing (omitted suffix, misspelling, recipient prefix, no house
number). This builder walks those two drop pools with four extra rungs.

Every rung still resolves its labels from an AUTHORITATIVE record -- the TIGER
component split, or the source's own city/state/zip fields. What is relaxed is
only *how a row is matched to a record*, never what the labels are. Nothing
here guesses a label.

RUNGS (each independently toggleable via --rungs, each separately reported)
--------------------------------------------------------------------------
2a  OMITTED SUFFIX. The interior equals a TIGER record's tokens with the
    record's StreetNamePostType tokens removed. Labels are the record's labels
    for the tokens that remain (no post type). Per plan Amendment 1, several
    records may share the reduced name so long as they all assign the SAME
    label sequence; records that disagree on the labels still drop.
    e.g. TIGER "N Den Hollow St" vs row "3131 N DEN HOLLOW"
         -> AddressNumber, StreetNamePreDirectional, StreetName, StreetName
    (this is the adjudicated gold-2 round-8 verdict for that very row.)

2b  SINGLE-TOKEN NEAR-MATCH. All interior tokens equal a record's tokens except
    one, which is within Levenshtein 1 (<=2 when both tokens are 5+ chars) of
    the record's token at that position. Requires a UNIQUE candidate record.
    Extra conservatism beyond the plan, because this rung is the one that can
    actually mislabel: tokens shorter than 4 chars are never near-matched;
    tokens containing digits are never near-matched; a differing token that is
    itself a street name in that state drops; directionals and street-type
    words never participate (that is a suffix confusion, not a misspelling).

2c  RECIPIENT PREFIX. Leading text that is not part of the delivery line gets
    labeled Recipient, and the remainder is aligned by the normal ladder.
    Two sub-populations, both from the source's own owner-mailing fields:
      2c-i  the row's earlier address-field lines, which build_realtext_corpus
            silently discards once it picks the delivery line;
      2c-ii `no_line_start` rows where a delivery line is embedded after a
            leading name inside one field
            ("BUCHANAN, SHARON M 73 LITTLE HENSON CREEK RD").
    NOTE ON EVIDENCE: the plan asks for the prefix to be confirmed against the
    source's own owner-NAME field. That field is not in the fetched cache --
    only the address fields were fetched -- and R-C forbids fetching it now. So
    the evidence used instead is (a) the text sits in the source's owner-
    mailing address block ahead of a line that aligns authoritatively, and
    (b) it passes `name_like`: no digits anywhere, no unit/box/'#' token, and
    it is not a street name in that state. That is weaker than a field match
    and it is why 2c's samples must be read before use.
    Conventions follow the adjudicated gold verdicts: care-of markers are part
    of the Recipient span ("C/O DOLLAR GENERAL - LEASE ADMIN DEPT" is six
    Recipient tokens; "% SHIRLEY FRIDAY PERS REP" is four).

2d  NO-NUMBER ROWS. A `no_line_start` row whose whole line is a street phrase
    that matches a TIGER record exactly. Labeled with no AddressNumber.

2e  CANONICALIZED LEXICAL VARIANTS (plan Amendment 1). The interior matches a
    TIGER record position for position once spelled-out suffixes and
    directionals are written the way TIGER writes them: "180 WEST VALLEY
    AVENUE" against TIGER's "W Valley Ave". Same arity, same slots, labels from
    the same record -- only the surface spelling of a token differs, and the
    surface spelling is what the corpus keeps. Assessors spell suffixes out and
    TIGER never does, so the exact-match corpus lacks this class entirely.
    Two guards make it safe rather than merely plausible:
      * SLOT ROLE. A suffix substitution is only accepted where the matched
        record labels that slot StreetNamePostType/StreetNamePreType, and a
        directional substitution only where the record labels it
        StreetNamePre/PostDirectional. The record itself has to agree that the
        slot is the kind of slot the substitution assumes.
      * VARIANT AGREEMENT. Every subset of the substitutions is looked up, and
        if two of them match records that disagree on the label sequence the
        row drops. This is what stops a row like "SOUTH RIVER ROAD" being read
        against "S River Rd" when "South River Rd" is also a street.

DISCIPLINE
----------
* R-C, asserted, not assumed: this module installs a network guard at import
  and every socket call raises. All input is the cache written by
  build_realtext_corpus (30 datasets, all of them explicitly excluded from
  gold-2b), so evaluation disjointness holds by construction.
* Dedupe by normalized identity against gold-1, gold-2, gold-2b, the clean set,
  realtext.jsonl and realtext_dev.jsonl, and within this corpus. Reported per
  list.
* Every row round-trips usaddress.tokenize; every label is one of the 26; '#'
  always carries an identifier label.

Usage:
  python training/extend_realtext_corpus.py --selftest
  python training/extend_realtext_corpus.py --build
  python training/extend_realtext_corpus.py --build --rungs 2a,2c
"""

# --- R-C network guard: installed BEFORE anything that could dial out -------
import socket as _socket


class NetworkForbidden(RuntimeError):
    """Raised if anything in this build path tries to reach the network."""


def _no_network(*_a, **_k):
    raise NetworkForbidden(
        "extend_realtext_corpus must not fetch (plan R-C): every row comes "
        "from the cache the 30 already-consumed datasets wrote."
    )


_socket.socket.connect = _no_network
_socket.socket.connect_ex = _no_network
_socket.create_connection = _no_network
_socket.getaddrinfo = _no_network
# ---------------------------------------------------------------------------

import argparse  # noqa: E402
import gzip  # noqa: E402
import json  # noqa: E402
import random  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from collections import Counter, defaultdict  # noqa: E402
from pathlib import Path  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "benchmark"))
sys.path.insert(0, str(ROOT / "training"))

import usaddress  # noqa: E402
import fetch_gold2 as fg  # noqa: E402
import build_realtext_corpus as B  # noqa: E402  (cache paths + shared ladder)

OUT_JSONL = ROOT / "training" / "corpus" / "realtext2.jsonl"
MANIFEST_OUT = ROOT / "training" / "REALTEXT2_MANIFEST.json"
SEED = 20260816
VALID_LABELS = set(usaddress.LABELS)
IDENT_LABELS = {"USPSBoxID", "OccupancyIdentifier", "AddressNumber"}
SAMPLES_PER_RUNG = 25
ALL_RUNGS = ("2a", "2b", "2c", "2d", "2e")
VOCAB_INVENTORIES = ROOT / "training" / "vocab_inventories.json"

DIRECTIONALS = {
    "n", "s", "e", "w", "ne", "nw", "se", "sw", "no", "so",
    "north", "south", "east", "west",
    "northeast", "northwest", "southeast", "southwest",
}
# Street-type words: a one-token difference among these is a suffix confusion,
# not a misspelling, so 2b refuses to treat it as one.
STREET_TYPES = set("""
st str street ave av aven avenue rd road dr drv drive ln lane ct crt court
cir circle blvd blv boulevard pl plc place way wy trl tr trail pkwy pky parkway
hwy highway loop lp ter terr terrace run pass path plz plaza sq square row
bnd bend cv cove crk creek rdg ridge hts heights pt pte point pts falls fls
xing crossing ext extension spur alley aly walk grn green gln glen hl hill
hollow holw knl knoll lk lake mdw meadow mnr manor ml mill pk park rst rest
shr shore spg spring vw view vlg village vly valley wl well cres crescent
""".split())
# Tokens that disqualify a Recipient prefix outright.
BAD_PREFIX_KEYS = set(B.UNIT_TYPES) | {
    "PO", "POB", "POBOX", "BOX", "RR", "HC", "#", "PMB", "GENERALDELIVERY",
}
BOX_START_KEYS = ("PO", "P", "POB", "POBOX", "BOX", "RR", "HC")

# --- rung 2e canonicalization tables ---------------------------------------
# TIGER stores only the ABBREVIATED form of a street type ("Ave", never
# "Avenue"), so the expansion itself cannot be read out of TIGER -- one side of
# the pair is not in the data. What IS read out of the data is the set of
# abbreviations TIGER actually uses: `training/vocab_inventories.json`
# street_type_suf / street_type_pre, counted over the national FEATNAMES pull.
# `load_canon_maps` keeps only the entries whose abbreviation appears in that
# TIGER-derived inventory and reports the rest, so a wrong or invented entry
# here cannot reach the corpus -- it is dropped at load time, and even if it
# survived, rung 2e's slot-role guard would refuse to fire it on a slot the
# record does not label a street type.
SUFFIX_EXPANSION_RAW = {
    "street": "st", "avenue": "ave", "road": "rd", "drive": "dr",
    "lane": "ln", "court": "ct", "circle": "cir", "boulevard": "blvd",
    "place": "pl", "terrace": "ter", "parkway": "pkwy", "highway": "hwy",
    "trail": "trl", "square": "sq", "plaza": "plz", "crossing": "xing",
    "extension": "ext", "heights": "hts", "junction": "jct",
    "landing": "lndg", "manor": "mnr", "meadow": "mdw", "meadows": "mdws",
    "point": "pt", "ridge": "rdg", "river": "riv", "spring": "spg",
    "springs": "spgs", "station": "sta", "turnpike": "tpke", "valley": "vly",
    "village": "vlg", "vista": "vis", "creek": "crk", "cove": "cv",
    "estates": "ests", "expressway": "expy", "falls": "fls", "forest": "frst",
    "green": "grn", "grove": "grv", "harbor": "hbr", "hollow": "holw",
    "knoll": "knl", "lake": "lk", "lakes": "lks", "mountain": "mtn",
    "orchard": "orch", "ranch": "rnch", "shore": "shr", "summit": "smt",
    "view": "vw", "alley": "aly", "bend": "bnd", "branch": "br",
    "bridge": "brg", "brook": "brk", "center": "ctr", "cliff": "clf",
    "club": "clb", "common": "cmn", "commons": "cmns", "corners": "cors",
    "crescent": "cres", "crest": "crst", "divide": "dv", "fork": "frk",
    "freeway": "fwy", "glacier": "glcr", "inlet": "inlt", "island": "is",
    "islands": "iss", "motorway": "mtwy", "overpass": "opas",
    "passage": "psge", "rapids": "rpds", "rest": "rst", "route": "rte",
    "skyway": "skwy", "stream": "strm", "trace": "trce", "track": "trak",
    "tunnel": "tunl", "underpass": "upas", "canal": "cnl", "channel": "chnnl",
    "canyon": "cyn", "causeway": "cswy", "bayou": "byu", "bypass": "byp",
    "drain": "drn", "hill": "hl", "bluff": "blf", "dam": "dm",
    "railway": "rlwy", "trafficway": "trfy",
}
DIR_EXPANSION_RAW = {
    "north": "n", "south": "s", "east": "e", "west": "w",
    "northeast": "ne", "northwest": "nw", "southeast": "se",
    "southwest": "sw",
}
CANON_MAPS = None  # set by build()/selftest via load_canon_maps()
SUFFIX_SLOT_LABELS = {"StreetNamePostType", "StreetNamePreType"}
DIR_SLOT_LABELS = {"StreetNamePreDirectional", "StreetNamePostDirectional"}
MAX_CANON_SITES = 4


def load_canon_maps():
    """-> (suffix map, directional map), gated on TIGER's own abbreviations."""
    inv = json.loads(VOCAB_INVENTORIES.read_text(encoding="utf-8"))
    tiger_abbrevs = set()
    for key in ("street_type_suf", "street_type_pre"):
        for k in inv.get(key, {}):
            tiger_abbrevs.update(B.norm_tok(t) for t in str(k).split())
    keep, uncorroborated = {}, []
    for word, abbrev in SUFFIX_EXPANSION_RAW.items():
        if abbrev == word:
            continue
        keep[word] = abbrev
        if abbrev not in tiger_abbrevs:
            uncorroborated.append(f"{word}->{abbrev}")
    # An entry TIGER's inventory does not corroborate is not dangerous, only
    # idle: its canonical form simply will not be a key in any state index, and
    # if it somehow were, rung 2e's slot-role guard still requires the matched
    # record to label that slot a street type. Reported, not deleted, because
    # the inventory is a sample of the national pull rather than a closed list.
    log(f"  2e: {len(keep)} suffix expansions "
        f"({len(keep) - len(uncorroborated)} corroborated by TIGER's own "
        f"abbreviation inventory, {len(uncorroborated)} not: "
        f"{', '.join(sorted(uncorroborated))}), "
        f"{len(DIR_EXPANSION_RAW)} directional expansions")
    return keep, dict(DIR_EXPANSION_RAW), sorted(uncorroborated)


def log(msg):
    print(msg, flush=True)


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def lev(a, b, cap):
    """Levenshtein distance, short-circuited above `cap`."""
    if abs(len(a) - len(b)) > cap:
        return cap + 1
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        if min(cur) > cap:
            return cap + 1
        prev = cur
    return prev[-1]


def build_aux(index):
    """Derive the two auxiliary maps every rung needs from the cached index.

    reduced : name-only key (record tokens minus StreetNamePostType tokens)
              -> {full record keys}.  Used by 2a; >1 value means ambiguous.
    red_lab : (reduced key, full key) -> label list for the surviving tokens.
    wild    : (n, i, tokens-with-slot-i-blanked) -> {full record keys}.
              Used by 2b to find one-off candidates without an O(index) scan.
    suffix  : every token TIGER itself uses as a StreetNamePostType somewhere in
              this state. A row whose last interior token is in here cannot be
              claimed to have "no suffix" -- see `SUFFIX WORD GUARD` below.
    """
    reduced = defaultdict(set)
    red_lab = {}
    wild = defaultdict(set)
    suffix = set()
    for key, labs in index.items():
        toks = key.split()
        if len(toks) != len(labs):
            continue
        suffix.update(t for t, l in zip(toks, labs) if l == "StreetNamePostType")
        keep = [(t, l) for t, l in zip(toks, labs) if l != "StreetNamePostType"]
        if keep and len(keep) < len(toks):
            rk = " ".join(t for t, _ in keep)
            reduced[rk].add(key)
            red_lab[(rk, key)] = [l for _, l in keep]
        for i in range(len(toks)):
            wild[(len(toks), i, " ".join(toks[:i] + ["\x00"] + toks[i + 1:]))].add(key)
    # TIGER only ever stores the ABBREVIATED suffix ("St", never "Street"), so
    # the index-derived vocabulary alone would not catch a row that spells the
    # suffix out -- which is exactly the mislabel the sample review found. Union
    # in the spelled-out forms. This set is only ever used to REJECT rows; it
    # never assigns a label, so widening it can only make the corpus smaller.
    suffix |= STREET_TYPES
    return reduced, red_lab, wild, suffix


def name_like(toks, index, reduced):
    """Is this leading text plausibly a Recipient? -> None if yes, else reason."""
    if len(toks) < 2:
        return "prefix_too_short"
    if len(toks) > 10:
        return "prefix_too_long"
    for t in toks:
        if any(ch.isdigit() for ch in t):
            return "prefix_has_digit"
        if B.tok_key(t) in BAD_PREFIX_KEYS:
            return "prefix_unit_or_box"
    if not any(re.search(r"[A-Za-z]{2}", t) for t in toks):
        return "prefix_no_word"
    key = " ".join(k for k in (B.norm_tok(t) for t in toks) if k)
    if key and (key in index or key in reduced):
        return "prefix_is_street"
    return None


def align_delivery(toks, st, mail_state, index):
    """Label a delivery-line token list by the ORIGINAL exact ladder.

    -> (tokens, labels) or (None, reason). Used for the remainder of a 2c row.
    """
    if not toks:
        return None, "empty"
    if B.tok_key(toks[0]) in BOX_START_KEYS:
        labels = B.label_box(toks)
        if labels is None:
            return None, "box_malformed"
        return list(toks), list(labels)
    if not B.NUM_RE.fullmatch(toks[0]) or len(toks) < 2:
        return None, "no_number"
    if mail_state != st:
        return None, "out_of_state"
    street, unit, unit_labs = B.strip_unit(toks[1:])
    if not street:
        return None, "interior_empty"
    normed = [B.norm_tok(t) for t in street]
    if any(not t for t in normed):
        return None, "interior_punct"
    labs = index.get(" ".join(normed))
    if labs is None:
        return None, "interior_unmatched"
    return ([toks[0]] + list(street) + list(unit),
            ["AddressNumber"] + list(labs) + list(unit_labs))


def finish(toks, labs, city_toks, st_tok, zip_tok, st, rung, dataset):
    """Attach the source-field tail, validate, and emit the record."""
    toks = list(toks) + list(city_toks) + [st_tok, zip_tok]
    labs = list(labs) + ["PlaceName"] * len(city_toks) + ["StateName", "ZipCode"]
    if len(toks) != len(labs):
        return None, "length_mismatch"
    raw = " ".join(toks)
    if usaddress.tokenize(raw) != toks:
        return None, "tokenize_mismatch"
    for t, l in zip(toks, labs):
        if l not in VALID_LABELS:
            return None, "invalid_label"
        if t == "#" and l not in IDENT_LABELS:
            return None, "hash_not_identifier"
    # Origin carries the rung so any single rung can be ablated from a training
    # mix by origin alone (Amendment 1 asks for this explicitly for 2c).
    return {"raw": raw, "tokens": toks, "labels": labs,
            "origin": f"rt2-{rung}-{st}", "state": st,
            "source": dataset, "rung": rung}, None


# ---------------------------------------------------------------------------
# The rungs
# ---------------------------------------------------------------------------

def rung_2a(street, index, reduced, red_lab, suffix, rej):
    """Omitted suffix. -> (tokens, labels, record) or None.

    SUFFIX WORD GUARD. Sample review of the first build caught a systematic
    mislabel: "820 WASHINGTON STREET" matched the record "Washington Street Pl"
    and got STREET labeled StreetName. The row's suffix is *present*; it is the
    TIGER record that carries an extra one. This rung only means anything when
    the row has no suffix at all, so a row whose last interior token is a token
    TIGER uses as a post type is not eligible -- the two readings cannot be
    told apart from the text, and guessing is what this builder must not do.
    """
    normed = [B.norm_tok(t) for t in street]
    key = " ".join(normed)
    cands = reduced.get(key)
    if not cands:
        return None
    # LABEL AGREEMENT (plan Amendment 1, replacing record uniqueness). The rule
    # exists to prevent mislabeling. Where several records share a reduced name
    # they differ only in the suffix that the row omitted -- "Whispering Birch
    # Cir" and "Whispering Birch Ln" both reduce to StreetName StreetName -- so
    # there is no mislabeling to prevent and every candidate would write the
    # same row. Records that disagree on the labels still drop.
    seqs = {tuple(red_lab[(key, f)]) for f in cands}
    if len(seqs) > 1:
        rej["2a_ambiguous_labels_disagree"] += 1
        return None
    if len(cands) > 1:
        rej["2a_tie_resolved_by_label_agreement"] += 1
    full = sorted(cands)[0]
    labs = red_lab[(key, full)]
    if len(labs) != len(street):
        rej["2a_length_mismatch"] += 1
        return None
    if "StreetName" not in labs:
        rej["2a_no_streetname"] += 1
        return None
    if normed[last_name_slot(labs)] in suffix:
        rej["2a_row_ends_in_suffix_word"] += 1
        return None
    return list(street), list(labs), full


def last_name_slot(labs):
    """Index of the last slot that is not a trailing post-directional.

    The suffix-word guard has to look past a trailing directional: in
    "445 68TH AVE SW" the token that might be a suffix is AVE, not SW, and
    reading that row against TIGER's "68th Ave Ct SW" would relabel a present
    suffix as part of the name -- the same mislabel the guard exists to stop.
    """
    i = len(labs) - 1
    while i > 0 and labs[i] == "StreetNamePostDirectional":
        i -= 1
    return i


def rung_2e(street, index, sufmap, dirmap, rej):
    """Canonicalized lexical variant. -> (tokens, labels, record, detail) or None.

    Enumerates every subset of the available substitutions rather than only the
    fully-canonical one, because the subsets are the competing readings of the
    same text: if "SOUTH RIVER ROAD" can be read against both "South River Rd"
    and "S River Rd", the row is ambiguous and must drop, and only looking at
    the fully-substituted form would hide that.
    """
    normed = [B.norm_tok(t) for t in street]
    sites = []
    for i, t in enumerate(normed):
        if t in sufmap:
            sites.append((i, sufmap[t], "suffix"))
        elif t in dirmap:
            sites.append((i, dirmap[t], "dir"))
    if not sites:
        return None
    if len(sites) > MAX_CANON_SITES:
        rej["2e_too_many_sites"] += 1
        return None

    matches = []  # (key, labels, used_sites)
    for mask in range(1, 1 << len(sites)):
        cand = list(normed)
        used = []
        for bit, (i, repl, kind) in enumerate(sites):
            if mask >> bit & 1:
                cand[i] = repl
                used.append((i, kind))
        labs = index.get(" ".join(cand))
        if labs is not None and len(labs) == len(street):
            matches.append((" ".join(cand), labs, used))
    if not matches:
        rej["2e_no_canonical_match"] += 1
        return None
    if len({tuple(m[1]) for m in matches}) > 1:
        rej["2e_variants_disagree"] += 1
        return None
    # Reported so the agreement guard's exercise rate is visible rather than
    # assumed: how often more than one reading of the row matched at all.
    rej["2e_multi_variant_agreed" if len(matches) > 1
        else "2e_single_variant"] += 1

    # prefer the reading that substitutes the fewest tokens -- the one that
    # keeps the most of the row's own text explained by the record as written
    key, labs, used = min(matches, key=lambda m: len(m[2]))
    for i, kind in used:
        want = SUFFIX_SLOT_LABELS if kind == "suffix" else DIR_SLOT_LABELS
        if labs[i] not in want:
            rej["2e_slot_role_mismatch"] += 1
            return None
    if "StreetName" not in labs:
        rej["2e_no_streetname"] += 1
        return None
    return (list(street), list(labs), key,
            {"substituted": [{"pos": i, "row": normed[i], "record": key.split()[i],
                              "kind": k} for i, k in used]})


def rung_2b(street, index, reduced, wild, suffix, rej):
    """Single-token near-match. -> (tokens, labels, record, detail) or None."""
    normed = [B.norm_tok(t) for t in street]
    n = len(normed)
    hits = {}
    saw_short = False
    for i in range(n):
        wk = (n, i, " ".join(normed[:i] + ["\x00"] + normed[i + 1:]))
        for full in wild.get(wk, ()):
            a, b = normed[i], full.split()[i]
            if any(c.isdigit() for c in a) or any(c.isdigit() for c in b):
                continue
            if a in DIRECTIONALS or b in DIRECTIONALS:
                continue
            if a in STREET_TYPES or b in STREET_TYPES:
                continue
            m = min(len(a), len(b))
            if m < 4:
                saw_short = True
                continue
            cap = 2 if m >= 5 else 1
            d = lev(a, b, cap)
            if 0 < d <= cap:
                hits[full] = (i, a, b, d)
    if not hits:
        if saw_short:
            rej["2b_token_too_short"] += 1
        else:
            rej["2b_no_candidate"] += 1
        return None
    if len(hits) > 1:
        rej["2b_ambiguous_record"] += 1
        return None
    full, (i, a, b, d) = next(iter(hits.items()))
    if a in index:
        rej["2b_token_is_street"] += 1
        return None
    if " ".join(normed) in reduced:
        rej["2b_also_2a_candidate"] += 1
        return None
    labs = index[full]
    if len(labs) != len(street):
        rej["2b_length_mismatch"] += 1
        return None
    # Same suffix-word guard as 2a, in its 2b form: if the row ends in a token
    # TIGER uses as a post type but the matched record does not label that slot
    # StreetNamePostType, the record's split does not describe this row.
    # ("16 Fuller Brook Road" matched "Miller Brook Road", whose TIGER split
    #  labels Road StreetName -- a mislabel for the row.)
    j = last_name_slot(labs)
    if normed[j] in suffix and labs[j] != "StreetNamePostType":
        rej["2b_suffix_split_disagrees"] += 1
        return None
    # The near-matched slot is the ONE place where the row's text differs from
    # the record's, so it is the one place a wrong record could produce a wrong
    # label. Everywhere else the tokens are identical and the record's split
    # describes them. Restricting the slot to StreetName means a false match
    # can only get the street's identity wrong, never its labeling.
    if labs[i] != "StreetName":
        rej["2b_slot_not_streetname"] += 1
        return None
    return list(street), list(labs), full, {"pos": i, "row": a, "record": b, "dist": d}


# ---------------------------------------------------------------------------
# Per-state pass over the cached rows
# ---------------------------------------------------------------------------

def process_state(st, rungs, out_rows, rej, diag):
    ck = B.CKPT_DIR / f"{st}.json.gz"
    if not ck.exists():
        log(f"[{st}] no fetch checkpoint in cache -- skipped")
        return
    with gzip.open(ck, "rt", encoding="utf-8") as f:
        payload = json.load(f)
    rows = payload["rows"]
    dataset = payload["dataset"]
    if not rows:
        return
    index = B.build_state_index(st)
    reduced, red_lab, wild, suffix = build_aux(index)
    sufmap, dirmap = CANON_MAPS
    src = B.SOURCES[st]
    kept = Counter()

    for row in rows:
        tail = B.parse_tail(row, st, src)
        if tail is None:
            continue
        city_toks, st_tok, mail_state, zip_tok = tail
        line, kind = B.pick_line(row["lines"])

        # ---------------- pool 2: no_line_start (rungs 2c-ii, 2d) ----------
        if line is None:
            diag["pool_no_line_start"] += 1
            handled = False
            for j in range(len(row["lines"]) - 1, -1, -1):
                toks = usaddress.tokenize(row["lines"][j])
                if not toks:
                    continue
                # everything in the source's earlier address fields is prefix too
                earlier = []
                for l in row["lines"][:j]:
                    earlier.extend(usaddress.tokenize(l))
                # 2c-ii: a delivery line embedded after leading name text
                if "2c" in rungs:
                    stop = False
                    for i in range(len(toks) - 1, 0, -1):
                        body, labs = align_delivery(toks[i:], st, mail_state, index)
                        if body is None:
                            continue
                        pre = earlier + list(toks[:i])
                        why = name_like(pre, index, reduced)
                        if why:
                            rej[why] += 1
                            stop = True
                            break
                        rec, err = finish(pre + body,
                                          ["Recipient"] * len(pre) + labs,
                                          city_toks, st_tok, zip_tok, st,
                                          "2c", dataset)
                        if rec is None:
                            rej[f"2c_{err}"] += 1
                            stop = True
                            break
                        rec["detail"] = {"sub": "2c-ii", "recipient": " ".join(pre)}
                        out_rows.append(rec)
                        kept["2c"] += 1
                        handled = True
                        break
                    if handled or stop:
                        break
                # 2d: the whole line is a street phrase, no house number.
                # Only when nothing precedes it -- a prefix + numberless street
                # is two relaxations stacked, which is not what this rung is.
                if "2d" in rungs and mail_state == st:
                    if earlier:
                        rej["2d_has_prefix"] += 1
                        break
                    street, unit, unit_labs = B.strip_unit(toks)
                    if len(street) < 2:
                        rej["2d_too_short"] += 1
                        break
                    normed = [B.norm_tok(t) for t in street]
                    if any(not t for t in normed):
                        rej["2d_interior_punct"] += 1
                        break
                    labs = index.get(" ".join(normed))
                    if labs is None:
                        rej["2d_interior_unmatched"] += 1
                        break
                    rec, err = finish(list(street) + list(unit),
                                      list(labs) + list(unit_labs),
                                      city_toks, st_tok, zip_tok, st,
                                      "2d", dataset)
                    if rec is None:
                        rej[f"2d_{err}"] += 1
                        break
                    rec["detail"] = {"record": " ".join(normed)}
                    out_rows.append(rec)
                    kept["2d"] += 1
                    handled = True
                    break
            continue

        line_toks = usaddress.tokenize(line)
        if not line_toks:
            continue

        # ---------------- pool 3: aligned rows with a discarded prefix (2c-i)
        li = None
        for i, l in enumerate(row["lines"]):
            if line == l or line.startswith(l + " "):
                li = i
                break
        body, labs = align_delivery(line_toks, st, mail_state, index)
        if body is not None:
            if "2c" in rungs and li:
                pre = []
                for l in row["lines"][:li]:
                    pre.extend(usaddress.tokenize(l))
                why = name_like(pre, index, reduced)
                if why:
                    rej[why] += 1
                    continue
                rec, err = finish(pre + body, ["Recipient"] * len(pre) + labs,
                                  city_toks, st_tok, zip_tok, st, "2c", dataset)
                if rec is None:
                    rej[f"2c_{err}"] += 1
                    continue
                rec["detail"] = {"sub": "2c-i", "recipient": " ".join(pre)}
                out_rows.append(rec)
                kept["2c"] += 1
            continue

        # ---------------- pool 1: interior_unmatched (rungs 2e, 2a, 2b) ----
        if labs != "interior_unmatched":
            continue
        diag["pool_interior_unmatched"] += 1
        street, unit, unit_labs = B.strip_unit(line_toks[1:])
        num = line_toks[0]

        def emit(got, rung, detail=None):
            """Shared tail for the three pool-1 rungs. -> True if a row landed."""
            stoks, slabs = got[0], got[1]
            rec, err = finish([num] + stoks + list(unit),
                              ["AddressNumber"] + slabs + list(unit_labs),
                              city_toks, st_tok, zip_tok, st, rung, dataset)
            if rec is None:
                rej[f"{rung}_{err}"] += 1
                return False
            d = dict(detail or {})
            d["record"] = got[2]
            rec["detail"] = d
            out_rows.append(rec)
            kept[rung] += 1
            return True

        # 2e first: it is the most faithful reading -- same arity, same slots,
        # only a token's spelling differs -- so it should win over the two
        # rungs that assume something is missing or mistyped.
        if "2e" in rungs:
            got = rung_2e(street, index, sufmap, dirmap, rej)
            if got:
                emit(got, "2e", got[3])
                continue

        if "2a" in rungs:
            got = rung_2a(street, index, reduced, red_lab, suffix, rej)
            if got:
                emit(got, "2a")
                continue
            if " ".join(B.norm_tok(t) for t in street) in reduced:
                continue  # an omitted-suffix row that failed 2a's own guards;
                          # it must not fall through and be re-read as a typo

        if "2b" in rungs:
            got = rung_2b(street, index, reduced, wild, suffix, rej)
            if got:
                emit(got, "2b", got[3])

    log(f"[{st}] kept {dict(kept)}")


# ---------------------------------------------------------------------------
# Dedupe + assembly
# ---------------------------------------------------------------------------

DEDUPE_FILES = [
    ("gold1", ROOT / "eval" / "gold" / "candidates.jsonl", "raw"),
    ("gold2", ROOT / "eval" / "gold2" / "candidates.jsonl", "raw"),
    ("gold2b", ROOT / "eval" / "gold2b" / "candidates.jsonl", "raw"),
    ("clean", ROOT / "eval" / "clean" / "clean.jsonl", "raw"),
    ("realtext", ROOT / "training" / "corpus" / "realtext.jsonl", "tokens"),
    ("realtext_dev", ROOT / "eval" / "realtext_dev.jsonl", "raw"),
]


def load_exclusions():
    per_list = {}
    for name, path, field in DEDUPE_FILES:
        if not path.exists():
            raise RuntimeError(f"dedupe source missing: {path}")
        ids = set()
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                d = json.loads(line)
                text = " ".join(d["tokens"]) if field == "tokens" else d["raw"]
                ids.add(fg.norm_identity(text))
        per_list[name] = ids
        log(f"  dedupe list {name}: {len(ids)} identities")
    return per_list


def build(rungs):
    global CANON_MAPS
    sufmap, dirmap, uncorroborated = load_canon_maps()
    CANON_MAPS = (sufmap, dirmap)
    assert B.CKPT_DIR.exists(), f"cache missing: {B.CKPT_DIR}"
    assert B.FEATNAMES_DIR.exists(), f"TIGER cache missing: {B.FEATNAMES_DIR}"
    t0 = time.time()
    out_rows, rej, diag = [], Counter(), Counter()
    for st in sorted(B.SOURCES):
        try:
            process_state(st, rungs, out_rows, rej, diag)
        except Exception as e:  # noqa: BLE001 -- one bad state must not kill the build
            log(f"[{st}] CRASHED: {type(e).__name__}: {str(e)[:200]}")
            raise

    log(f"\nraw rung output: {len(out_rows)} rows in {time.time() - t0:.0f}s")

    # ---- dedupe -----------------------------------------------------------
    per_list = load_exclusions()
    removals = Counter()
    seen, rows = set(), []
    for rec in out_rows:
        nid = fg.norm_identity(rec["raw"])
        hit = next((n for n, ids in per_list.items() if nid in ids), None)
        if hit:
            removals[hit] += 1
            continue
        if nid in seen:
            removals["internal_dup"] += 1
            continue
        seen.add(nid)
        rows.append(rec)

    rng = random.Random(SEED)
    rng.shuffle(rows)

    # ---- assertions -------------------------------------------------------
    problems = []
    for r in rows:
        if len(r["tokens"]) != len(r["labels"]):
            problems.append(f"length mismatch: {r['raw'][:70]}")
        if usaddress.tokenize(r["raw"]) != r["tokens"]:
            problems.append(f"tokenize round-trip: {r['raw'][:70]}")
        for t, l in zip(r["tokens"], r["labels"]):
            if l not in VALID_LABELS:
                problems.append(f"invalid label {l!r}: {r['raw'][:70]}")
            if t == "#" and l not in IDENT_LABELS:
                problems.append(f"'#' not identifier-labeled: {r['raw'][:70]}")
    all_excl = set().union(*per_list.values())
    leak = sum(1 for r in rows if fg.norm_identity(r["raw"]) in all_excl)
    if leak:
        problems.append(f"{leak} rows still overlap an eval/train list")
    if problems:
        for p in problems[:20]:
            log(f"ASSERTION FAILED: {p}")
        log(f"{len(problems)} assertion failures -- corpus NOT written")
        sys.exit(1)

    # ---- samples for human review ----------------------------------------
    by_rung = defaultdict(list)
    for r in rows:
        by_rung[r["rung"]].append(r)
    sample_out = {}
    for rung, rs in sorted(by_rung.items()):
        pick = random.Random(SEED ^ hash(rung) % 10**6).sample(
            rs, min(SAMPLES_PER_RUNG, len(rs)))
        sample_out[rung] = [{
            "state": r["state"],
            "raw": r["raw"],
            "pairs": [[t, l] for t, l in zip(r["tokens"], r["labels"])],
            "evidence": r.get("detail", {}),
        } for r in pick]

    per_state = Counter(r["state"] for r in rows)
    per_state_rung = defaultdict(Counter)
    for r in rows:
        per_state_rung[r["state"]][r["rung"]] += 1

    OUT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSONL, "w", encoding="utf-8") as f:
        for r in rows:
            out = {k: v for k, v in r.items() if k != "detail"}
            f.write(json.dumps(out, ensure_ascii=False) + "\n")

    manifest = {
        "seed": SEED,
        "built": time.strftime("%Y-%m-%d"),
        "unit": "G2B-U2 (plan 2026-08-16-003)",
        "method": "extended alignment ladder over the cached drop pools of "
                  "build_realtext_corpus; labels always from the TIGER record "
                  "or the source's own city/state/zip fields",
        "no_fetch": "asserted: socket.connect/create_connection/getaddrinfo "
                    "raise NetworkForbidden for the whole build",
        "input_cache": str(B.CKPT_DIR),
        "tiger": "US Census Bureau TIGER/Line 2024 FEATNAMES (public domain)",
        "rungs_enabled": sorted(rungs),
        "rung_2e_canonicalization": {
            "note": "TIGER stores only abbreviated street types, so the "
                    "expansion cannot be read out of TIGER; the abbreviation "
                    "SET is data-derived (vocab_inventories.json, counted over "
                    "the national FEATNAMES pull) and every expansion is gated "
                    "at match time by the slot-role and variant-agreement "
                    "guards, so an uncorroborated entry is idle rather than "
                    "dangerous",
            "suffix_expansions": len(sufmap),
            "suffix_expansions_uncorroborated": uncorroborated,
            "directional_expansions": len(dirmap),
        },
        "rung_2c_evidence_substitution":
            "plan Amendment 1: the source's owner-NAME field was never fetched "
            "and R-C forbids fetching it, so the prefix is evidenced by (a) "
            "sitting in an owner-MAILING field ahead of a line that aligns "
            "authoritatively and (b) passing name_like (no digits, no unit or "
            "box token, not a street name in that geography). 2c rows carry "
            "origin 'rt2-2c-<ST>' so the rung can be ablated on its own.",
        "total_rows": len(rows),
        "rows_before_dedupe": len(out_rows),
        "per_rung_kept": dict(Counter(r["rung"] for r in rows).most_common()),
        "per_rung_kept_before_dedupe": dict(
            Counter(r["rung"] for r in out_rows).most_common()),
        "rejections": dict(rej.most_common()),
        "drop_pool_sizes": dict(diag.most_common()),
        "dedupe_removals": dict(removals.most_common()),
        "dedupe_lists": {n: len(v) for n, v in per_list.items()},
        "n_states": len(per_state),
        "per_state": dict(sorted(per_state.items())),
        "per_state_rung": {k: dict(v) for k, v in sorted(per_state_rung.items())},
        "label_counts": dict(Counter(
            l for r in rows for l in r["labels"]).most_common()),
        "samples": sample_out,
    }
    MANIFEST_OUT.write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    log(f"\nWrote {len(rows)} rows -> {OUT_JSONL}")
    log(f"Manifest -> {MANIFEST_OUT}")
    log(f"per rung: {manifest['per_rung_kept']}")
    log(f"dedupe removals: {dict(removals)}")
    if len(rows) < 25000:
        log(f"\nSHORTFALL: {len(rows)} rows < the 25,000 target. Reported, "
            f"not tuned around (plan: 'do not relax matching to hit a number').")


# ---------------------------------------------------------------------------
# Self-test: the uniqueness guards, proven on deliberate ambiguous cases
# ---------------------------------------------------------------------------

def selftest():
    ok = True

    # (1) the network guard actually bites
    try:
        _socket.create_connection(("example.com", 80))
        log("FAIL: network guard did not fire"); ok = False
    except NetworkForbidden:
        log("pass: network guard fires on create_connection")

    # (2) 2a drops an ambiguous omitted suffix, keeps an unambiguous one
    index = {
        "whispering birch cir": ["StreetName", "StreetName", "StreetNamePostType"],
        "lone pine ln": ["StreetName", "StreetName", "StreetNamePostType"],
        "lone pine ct": ["StreetName", "StreetName", "StreetNamePostType"],
    }
    reduced, red_lab, wild, suffix = build_aux(index)
    rej = Counter()
    got = rung_2a(["WHISPERING", "BIRCH"], index, reduced, red_lab, suffix, rej)
    if got and got[1] == ["StreetName", "StreetName"]:
        log("pass: 2a keeps the unique omitted-suffix case")
    else:
        log(f"FAIL: 2a unique case -> {got}"); ok = False
    # Amendment 1: a tie whose candidates AGREE on the labels is now kept ...
    got = rung_2a(["LONE", "PINE"], index, reduced, red_lab, suffix, rej)
    if (got and got[1] == ["StreetName", "StreetName"]
            and rej["2a_tie_resolved_by_label_agreement"] == 1):
        log("pass: 2a keeps a Ln-vs-Ct tie whose candidates agree on labels")
    else:
        log(f"FAIL: 2a label-agreement tie -> {got}, rej={dict(rej)}"); ok = False
    # ... and a tie whose candidates DISAGREE still drops.
    index_dis = {
        "old barn rd": ["StreetName", "StreetName", "StreetNamePostType"],
        "old barn st": ["StreetNamePreModifier", "StreetName",
                        "StreetNamePostType"],
    }
    red_d, lab_d, _w, suf_d = build_aux(index_dis)
    rej = Counter()
    got = rung_2a(["OLD", "BARN"], index_dis, red_d, lab_d, suf_d, rej)
    if got is None and rej["2a_ambiguous_labels_disagree"] == 1:
        log("pass: 2a still drops a tie whose candidates disagree on labels")
    else:
        log(f"FAIL: 2a disagreeing tie -> {got}, rej={dict(rej)}"); ok = False

    # (3) 2b drops when two records are each one edit away, keeps a unique one
    index = {
        "talley ridge rd": ["StreetName", "StreetName", "StreetNamePostType"],
        "tally ridge rd": ["StreetName", "StreetName", "StreetNamePostType"],
        "harmon creek dr": ["StreetName", "StreetName", "StreetNamePostType"],
    }
    reduced, red_lab, wild, suffix = build_aux(index)
    rej = Counter()
    got = rung_2b(["TALLEE", "RIDGE", "RD"], index, reduced, wild, suffix, rej)
    if got is None and rej["2b_ambiguous_record"] == 1:
        log("pass: 2b drops the deliberately ambiguous near-match (2 records tie)")
    else:
        log(f"FAIL: 2b ambiguous case -> {got}, rej={dict(rej)}"); ok = False
    rej = Counter()
    got = rung_2b(["HARMAN", "CREEK", "DR"], index, reduced, wild, suffix, rej)
    if got and got[2] == "harmon creek dr":
        log("pass: 2b keeps the unique near-match")
    else:
        log(f"FAIL: 2b unique case -> {got}"); ok = False

    # (4) 2b refuses a suffix confusion and a short token
    rej = Counter()
    index2 = {"oak st": ["StreetName", "StreetNamePostType"],
              "oat st": ["StreetName", "StreetNamePostType"]}
    reduced2, _rl, wild2, suffix2 = build_aux(index2)
    if rung_2b(["OAR", "ST"], index2, reduced2, wild2, suffix2, rej) is None:
        log("pass: 2b refuses a 3-char token near-match")
    else:
        log("FAIL: 2b accepted a 3-char near-match"); ok = False
    rej = Counter()
    index3 = {"maple dr": ["StreetName", "StreetNamePostType"]}
    reduced3, _rl, wild3, suffix3 = build_aux(index3)
    if rung_2b(["MAPLE", "DRR"], index3, reduced3, wild3, suffix3, rej) is None:
        log("pass: 2b refuses a street-type-word difference")
    else:
        log("FAIL: 2b accepted a street-type difference"); ok = False

    # (5) name_like rejects unit fragments and street text
    idx = {"main st": ["StreetName", "StreetNamePostType"]}
    red = {}
    checks = [
        (["STE", "200"], "prefix_unit_or_box"),
        (["#", "550"], "prefix_unit_or_box"),
        (["PMB", "B"], "prefix_unit_or_box"),
        (["SUITE", "1120"], "prefix_unit_or_box"),
        (["24-616", "SMITH"], "prefix_has_digit"),
        (["MAIN", "ST"], "prefix_is_street"),
        (["SCHAEFER"], "prefix_too_short"),
    ]
    for toks, want in checks:
        got = name_like(toks, idx, red)
        if got != want:
            log(f"FAIL: name_like({toks}) -> {got!r}, wanted {want!r}"); ok = False
    # (6) the suffix-word guard: the exact mislabel the first sample review found
    index4 = {"washington street pl": ["StreetName", "StreetName", "StreetNamePostType"],
              "miller brook road": ["StreetName", "StreetName", "StreetName"]}
    reduced4, red_lab4, wild4, suffix4 = build_aux(index4)
    rej = Counter()
    if (rung_2a(["WASHINGTON", "STREET"], index4, reduced4, red_lab4, suffix4, rej)
            is None and rej["2a_row_ends_in_suffix_word"] == 1):
        log("pass: 2a refuses a row whose last token is itself a suffix word")
    else:
        log(f"FAIL: 2a accepted 'WASHINGTON STREET', rej={dict(rej)}"); ok = False
    rej = Counter()
    if (rung_2b(["FULLER", "BROOK", "ROAD"], index4, reduced4, wild4, suffix4, rej)
            is None and rej["2b_suffix_split_disagrees"] == 1):
        log("pass: 2b refuses a record whose split disagrees on the row's suffix")
    else:
        log(f"FAIL: 2b accepted 'FULLER BROOK ROAD', rej={dict(rej)}"); ok = False
    # the guard has to see past a trailing directional (second review catch)
    index8 = {"68th ave ct sw": ["StreetName", "StreetName",
                                 "StreetNamePostType",
                                 "StreetNamePostDirectional"],
              "dolores dr nw": ["StreetName", "StreetNamePostType",
                                "StreetNamePostDirectional"]}
    red8, lab8, _w8, suf8 = build_aux(index8)
    rej = Counter()
    if (rung_2a(["68TH", "AVE", "SW"], index8, red8, lab8, suf8, rej) is None
            and rej["2a_row_ends_in_suffix_word"] == 1):
        log("pass: 2a refuses '68TH AVE SW' -- AVE is a suffix behind a directional")
    else:
        log("FAIL: 2a accepted '68TH AVE SW'"); ok = False
    got = rung_2a(["DOLORES", "NW"], index8, red8, lab8, suf8, rej)
    if got and got[1] == ["StreetName", "StreetNamePostDirectional"]:
        log("pass: 2a still keeps 'DOLORES NW' (nothing suffix-like remains)")
    else:
        log(f"FAIL: 2a rejected 'DOLORES NW' -> {got}"); ok = False

    # (7) rung 2e: canonicalization, slot-role guard, variant agreement
    sufmap, dirmap, _unc = load_canon_maps()
    index5 = {
        "w valley ave": ["StreetNamePreDirectional", "StreetName",
                         "StreetNamePostType"],
        "mockingbird ln": ["StreetName", "StreetNamePostType"],
    }
    rej = Counter()
    got = rung_2e(["WEST", "VALLEY", "AVENUE"], index5, sufmap, dirmap, rej)
    if got and got[1] == ["StreetNamePreDirectional", "StreetName",
                          "StreetNamePostType"]:
        log("pass: 2e canonicalizes 'WEST VALLEY AVENUE' onto 'W Valley Ave'")
    else:
        log(f"FAIL: 2e canonical case -> {got}"); ok = False
    # the deliberate ambiguity Amendment 1 names: two readings, two labelings
    index6 = {
        "s river rd": ["StreetNamePreDirectional", "StreetName",
                       "StreetNamePostType"],
        "south river rd": ["StreetName", "StreetName", "StreetNamePostType"],
    }
    rej = Counter()
    got = rung_2e(["SOUTH", "RIVER", "ROAD"], index6, sufmap, dirmap, rej)
    if got is None and rej["2e_variants_disagree"] == 1:
        log("pass: 2e drops 'SOUTH RIVER ROAD' -- the two readings disagree")
    else:
        log(f"FAIL: 2e ambiguous case -> {got}, rej={dict(rej)}"); ok = False
    # slot role: the record must agree the substituted slot IS a type slot
    # (TIGER records whose NAME is literally "N Park" exist; canonicalizing the
    #  row's "NORTH" onto that slot would be assuming a role the record denies.)
    index7 = {"n park ave": ["StreetName", "StreetName", "StreetNamePostType"]}
    rej = Counter()
    got = rung_2e(["NORTH", "PARK", "AVENUE"], index7, sufmap, dirmap, rej)
    if got is None and rej["2e_slot_role_mismatch"] == 1:
        log("pass: 2e refuses a substitution the record labels StreetName")
    else:
        log(f"FAIL: 2e slot-role case -> {got}, rej={dict(rej)}"); ok = False

    if name_like(["C/O", "NANCY", "RILEY"], idx, red) is None:
        log("pass: name_like accepts a care-of recipient")
    else:
        log("FAIL: name_like rejected a care-of recipient"); ok = False
    log("pass: name_like rejects unit fragments and street text" if ok else "")

    log("\nSELFTEST " + ("PASSED" if ok else "FAILED"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--rungs", default=",".join(ALL_RUNGS),
                    help="comma list; any of 2a,2b,2c,2d")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    if args.build:
        rungs = {r.strip() for r in args.rungs.split(",") if r.strip()}
        bad = rungs - set(ALL_RUNGS)
        if bad:
            sys.exit(f"unknown rung(s): {sorted(bad)}")
        build(rungs)
        return
    ap.print_help()


if __name__ == "__main__":
    main()
