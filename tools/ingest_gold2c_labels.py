"""Ingest gold-2c label approvals into reusable approved sequences.

Answers are absolute, not comparative: "ok" approves the proposed parse,
"TOKEN = Label; ..." corrects specific tokens, "skip" stores the record
unscoreable. The result is eval/gold2c/approved_labels.json, which scores
every future candidate without further human review.

Correction grammar, as the reviewer wrote it:
  TOKEN = Label                      apply to that token
  TOKEN [after OTHER] = Label        positional, when the token repeats
  TOKEN [before OTHER] = Label       positional, when the token repeats
Tokens are matched on the review doc's displayed form (trailing punctuation
stripped, case-insensitive). A correction that matches no token, or matches
several with no positional hint, is a hard error -- never a silent guess.

Usage: python tools/ingest_gold2c_labels.py [--verify]
"""

import argparse
import csv
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "benchmark"))
from binpath import bin_path  # noqa: E402

G2C = ROOT / "eval" / "gold2c"

ANSWERS = {
    1: "ok", 2: "ok", 3: "CO = StreetNamePreType; RD = StreetNamePreType; B = StreetName",
    4: "DRIVE = StreetNamePostType; PIKE = PlaceName; ROAD = PlaceName; AL = StateName",
    5: "NEW = PlaceName", 6: "ok", 7: "Bay = StreetName",
    8: "Spc = OccupancyType; 12 = OccupancyIdentifier", 9: "ok", 10: "ok",
    11: "Paisano = StreetName", 12: "Marcos = StreetName", 13: "ok",
    14: "W = StreetNamePostDirectional", 15: "ok", 16: "ok", 17: "ok",
    18: "ADDRESS = NotAddress; UNKNOWN = NotAddress", 19: "ok", 20: "ok", 21: "ok",
    22: "ok", 23: "LAKES = StreetName", 24: "ok", 25: "ok", 26: "ok", 27: "ok", 28: "ok",
    29: "100% = NotAddress", 30: "ok", 31: "11, = Recipient; 2005 = Recipient", 32: "ok",
    33: "ok", 34: "ok", 35: "AVE = StreetNamePreType; B = StreetName", 36: "ROCK = PlaceName",
    37: "ok", 38: "ROCK = PlaceName", 39: "ok", 40: "ok", 41: "ok", 42: "ok", 43: "ok",
    44: ("St [after Miami] = StreetNamePostType; c/o = Recipient; "
         "St [before Mattews] = Recipient; Mattews = Recipient; Cathedral = Recipient; "
         "South = PlaceName"),
    45: "ok", 46: "Knolls = StreetName", 47: "ok", 48: "ok", 49: "GLEN = StreetName",
    50: "JON = StreetName", 51: "ok", 52: "ok", 53: "ok", 54: "ok", 55: "ok", 56: "ok",
    57: ("NW = StreetNamePostDirectional; CONDO = OccupancyType; # = OccupancyIdentifier; "
         "1211 = OccupancyIdentifier"),
    58: "ok", 59: "LESTER = StreetName; B = StreetName", 60: "ok", 61: "ok", 62: "ok",
    63: "ok", 64: "LAKE = StreetName", 65: "SOUTH = StreetNamePostDirectional", 66: "ok",
    67: "LAKE = StreetName", 68: "ok",
    69: "FOREST = Recipient; HILL = Recipient; PROPERTIES = Recipient; INC = Recipient",
    70: "LA = StreetName", 71: "ok", 72: "ok", 73: "ok", 74: "ok", 75: "ok", 76: "ok",
    77: "ok", 78: "ok", 79: "ok", 80: "ok", 81: "ok", 82: "ok",
    83: "RT = StreetNamePreType; 17A = StreetName", 84: "ok", 85: "skip", 86: "ok",
    87: "ok", 88: "ok", 89: "VISTA = StreetName", 90: "YORK = StreetName", 91: "ok",
    92: "ok", 93: "Co = StreetNamePreType; Rt = StreetNamePreType; 23A = StreetName",
    94: "Co = StreetNamePreType; Rt = StreetNamePreType; 41A = StreetName", 95: "ok",
    96: "ok", 97: "ok", 98: "skip",
    99: ("PINE = StreetName; 9E = OccupancyIdentifier; L = OccupancyIdentifier; "
         "01 = OccupancyIdentifier; ST = StreetNamePostType"),
    100: "ok", 101: "ok", 102: "ok", 103: "ok", 104: "ok", 105: "ok", 106: "ok",
    107: "ok", 108: "MT = PlaceName", 109: "BUS = StreetNamePostModifier", 110: "ok",
    111: "ok", 112: "ok",
    113: "P = USPSBoxType; O = USPSBoxType; DRAWER = USPSBoxType; E = USPSBoxID",
    114: "CENTRE = StreetName", 115: "ok", 116: "ok", 117: "ok",
    118: "INTERSTATE = StreetNamePreType", 119: "ok",
    120: ("DO = NotAddress; NOT = NotAddress; SENT = NotAddress; TO = NotAddress; "
          "SEALS = NotAddress; RD = NotAddress; OR = NotAddress; MARILYN = NotAddress"),
    121: "ok", 122: "ok", 123: "ok", 124: "ok",
    125: "ST = StreetNamePostType; UN = OccupancyType; 306 = OccupancyIdentifier",
    126: "ST = StreetNamePostType; UN = OccupancyType; 701 = OccupancyIdentifier",
    127: "skip", 128: "ok",
    129: "UN = OccupancyType; 419 = OccupancyIdentifier",
}


def norm(tok):
    return tok.strip().strip(".,;:").upper()


def tag(raws, model=None):
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8", newline="") as tf:
        w = csv.writer(tf)
        w.writerow(["raw_address"])
        for r in raws:
            w.writerow([r])
        tmp = tf.name
    cmd = [bin_path("eval_tag"), tmp] + (["--model", model] if model else [])
    out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=True)
    return [json.loads(l) for l in out.stdout.splitlines() if l.strip()]


def apply_corrections(tokens, labels, answer, n):
    labels = list(labels)
    for part in [p.strip() for p in answer.split(";") if p.strip()]:
        m = re.match(r"^(.*?)\s*(?:\[(after|before)\s+(.+?)\])?\s*=\s*(\S+)$", part)
        if not m:
            raise SystemExit(f"#{n}: cannot parse correction {part!r}")
        tok, rel, anchor, label = m.group(1), m.group(2), m.group(3), m.group(4)
        idxs = [i for i, t in enumerate(tokens) if norm(t) == norm(tok)]
        if not idxs:
            raise SystemExit(f"#{n}: token {tok!r} not found in {tokens}")
        if len(idxs) > 1:
            if not rel:
                raise SystemExit(f"#{n}: token {tok!r} repeats and no position given: {tokens}")
            aidx = [i for i, t in enumerate(tokens) if norm(t) == norm(anchor)]
            if not aidx:
                raise SystemExit(f"#{n}: anchor {anchor!r} not found in {tokens}")
            a = aidx[0]
            cand = [i for i in idxs if (i > a if rel == "after" else i < a)]
            if not cand:
                raise SystemExit(f"#{n}: no {tok!r} {rel} {anchor!r} in {tokens}")
            idxs = [min(cand, key=lambda i: abs(i - a))]
        for i in idxs:
            labels[i] = label
    return labels


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()

    sel = json.loads((G2C / "review_selection.json").read_text(encoding="utf-8"))
    rows = [json.loads(l) for l in open(G2C / "candidates.jsonl", encoding="utf-8-sig") if l.strip()]
    picked = [rows[i] for i in sel["indices"]]
    assert len(picked) == len(ANSWERS) == 129, (len(picked), len(ANSWERS))
    v1 = tag([r["raw"] for r in picked])

    approved, skipped = {}, []
    for n, (r, pred) in enumerate(zip(picked, v1), 1):
        ans = ANSWERS[n]
        if ans == "skip":
            skipped.append(r["raw"])
            continue
        labels = pred["labels"] if ans == "ok" else apply_corrections(
            pred["tokens"], pred["labels"], ans, n)
        approved[r["raw"]] = {"tokens": pred["tokens"], "labels": labels,
                              "state": r["state"], "answer": ans,
                              "corrected": ans != "ok"}
    n_corr = sum(1 for v in approved.values() if v["corrected"])
    print(f"approved {len(approved)} ({len(approved) - n_corr} as proposed, {n_corr} corrected), "
          f"{len(skipped)} skipped")
    if args.verify:
        for raw, v in approved.items():
            if v["corrected"]:
                print(f"\n{raw[:70]}\n   {' | '.join(f'{t}={l}' for t, l in zip(v['tokens'], v['labels']))}")
        return
    (G2C / "approved_labels.json").write_text(json.dumps(approved, indent=1), encoding="utf-8")
    (G2C / "skipped.json").write_text(json.dumps(skipped, indent=1), encoding="utf-8")
    print(f"wrote {G2C / 'approved_labels.json'}")


if __name__ == "__main__":
    main()
