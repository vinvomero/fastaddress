"""Real-text dev tier: score a candidate vs v1 on the held-out real-text set.

The holdout (eval/realtext_dev.jsonl, 2,000 aligned rows, 30 states, seed
20260818) was physically removed from the training corpus before any v37+
model existed. Labels come from alignment against source fields + TIGER —
not human adjudication — so this is a DEV surface: iterate here freely.
Gold-2 is touched only under PROTOCOL2's frozen spend rule, which requires
this tier's bar first: net positive divergent-record margin vs v1 with a
95% bootstrap CI excluding zero.

Scoring: on records where the two models disagree, a model scores a win if
its labels exactly match the aligned gold labels and the other's do not.
Both-wrong or both-right contribute zero. Net margin is computed over the
full 2,000 rows (agreeing records are zeros), CI by seeded bootstrap.

Usage: python benchmark/realtext_dev.py --candidate model/candidates/v37.crfsuite
"""

import argparse
import collections
import csv
import json
import random
import subprocess
import tempfile
from pathlib import Path

import sys as _sys
from pathlib import Path as _P
_sys.path.insert(0, str(_P(__file__).resolve().parent))
from binpath import bin_path

ROOT = Path(__file__).parent.parent
HOLDOUT = ROOT / "eval" / "realtext_dev.jsonl"
EVAL_BIN = bin_path("eval_tag")
BOOT_SEED = 20260818

DIVISION = {
    "CT": "NewEngland", "ME": "NewEngland", "MA": "NewEngland", "NH": "NewEngland",
    "RI": "NewEngland", "VT": "NewEngland",
    "NJ": "MidAtlantic", "NY": "MidAtlantic", "PA": "MidAtlantic",
    "IL": "ENCentral", "IN": "ENCentral", "MI": "ENCentral", "OH": "ENCentral", "WI": "ENCentral",
    "IA": "WNCentral", "KS": "WNCentral", "MN": "WNCentral", "MO": "WNCentral",
    "NE": "WNCentral", "ND": "WNCentral", "SD": "WNCentral",
    "DE": "SouthAtlantic", "DC": "SouthAtlantic", "FL": "SouthAtlantic", "GA": "SouthAtlantic",
    "MD": "SouthAtlantic", "NC": "SouthAtlantic", "SC": "SouthAtlantic", "VA": "SouthAtlantic",
    "WV": "SouthAtlantic",
    "AL": "ESCentral", "KY": "ESCentral", "MS": "ESCentral", "TN": "ESCentral",
    "AR": "WSCentral", "LA": "WSCentral", "OK": "WSCentral", "TX": "WSCentral",
    "AZ": "Mountain", "CO": "Mountain", "ID": "Mountain", "MT": "Mountain",
    "NV": "Mountain", "NM": "Mountain", "UT": "Mountain", "WY": "Mountain",
    "AK": "Pacific", "CA": "Pacific", "HI": "Pacific", "OR": "Pacific", "WA": "Pacific",
}


def tag(raws, model=None):
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8", newline="") as tf:
        w = csv.writer(tf)
        w.writerow(["raw_address"])
        for r in raws:
            w.writerow([r])
        tmp = tf.name
    cmd = [EVAL_BIN, tmp] + (["--model", model] if model else [])
    out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=True)
    return [json.loads(l) for l in out.stdout.splitlines() if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    args = ap.parse_args()

    rows = [json.loads(l) for l in open(HOLDOUT, encoding="utf-8") if l.strip()]
    raws = [r["raw"] for r in rows]
    v1 = tag(raws)
    cand = tag(raws, args.candidate)

    contrib, by_div = [], collections.defaultdict(list)
    v1_exact = cand_exact = 0
    for r, a, b in zip(rows, v1, cand):
        assert a["tokens"] == r["tokens"] and b["tokens"] == r["tokens"], r["raw"]
        gold = r["labels"]
        v1_ok, cand_ok = a["labels"] == gold, b["labels"] == gold
        v1_exact += v1_ok
        cand_exact += cand_ok
        if a["labels"] == b["labels"]:
            continue
        c = 1 if (cand_ok and not v1_ok) else (-1 if (v1_ok and not cand_ok) else 0)
        contrib.append(c)
        st = r["origin"].removeprefix("rt-")
        by_div[DIVISION.get(st, "?")].append(c)

    n = len(rows)
    population = contrib + [0] * (n - len(contrib))
    net = sum(contrib)
    point = net / n * 100
    rng = random.Random(BOOT_SEED)
    boots = sorted(sum(rng.choices(population, k=n)) / n * 100 for _ in range(10000))
    lo, hi = boots[250], boots[9750]

    wins = contrib.count(1)
    losses = contrib.count(-1)
    print(f"holdout: {n} rows   exact-match  v1 {v1_exact/n*100:.2f}%   candidate {cand_exact/n*100:.2f}%")
    print(f"divergents: {len(contrib)}  ({wins} candidate right / {losses} v1 right / "
          f"{len(contrib)-wins-losses} both wrong)")
    print(f"net margin: {net:+d} records = {point:+.3f} pp   95% CI [{lo:+.3f}, {hi:+.3f}]")
    print("\nby division (reported; dev tier has no division gate):")
    for d, cs in sorted(by_div.items()):
        print(f"   {d:14} divergents {len(cs):4}  net {sum(cs):+4}")
    ok = net > 0 and lo > 0
    print(f"\nREALTEXT DEV TIER  net positive, CI excludes zero : {'PASS' if ok else 'FAIL'}")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
