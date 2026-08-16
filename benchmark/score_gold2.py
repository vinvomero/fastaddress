"""Score a candidate against gold-2 under PROTOCOL2's frozen gates.

Gates (fixed 2026-08-15, before any scoring):
  1. Margin: net positive with 95% bootstrap CI excluding zero, full set.
  2. Division: no census division net-negative, min 10 divergents to bind.
  3. Language tier: CI-pass -> "measurably better" phrasing; stronger headline
     additionally requires net margin >= +1.5pp.
Human verdicts only; neither/skip contribute zero; agreeing records zero.

Usage: python benchmark/score_gold2.py --verdicts eval/gold2/verdicts_r7.json
"""

import argparse
import collections
import json
import random
from pathlib import Path

ROOT = Path(__file__).parent.parent
DIVISION = {  # census divisions
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verdicts", default="eval/gold2/verdicts_r7.json")
    ap.add_argument("--total", type=int, default=1394)
    ap.add_argument("--attempt", type=int, default=1)
    args = ap.parse_args()

    verd = json.loads((ROOT / args.verdicts).read_text(encoding="utf-8"))
    contrib, by_div = [], collections.defaultdict(list)
    for raw, v in verd.items():
        c = {"v2": 1, "v1": -1}.get(v["verdict"], 0)
        contrib.append(c)
        by_div[DIVISION.get(v.get("state", ""), "?")].append(c)

    n = args.total
    population = contrib + [0] * (n - len(contrib))
    net = sum(contrib)
    point = net / n * 100

    rng = random.Random(20260814)
    boots = sorted(sum(rng.choices(population, k=n)) / n * 100 for _ in range(10000))
    lo, hi = boots[250], boots[9750]

    wins = contrib.count(1)
    losses = contrib.count(-1)
    print(f"verdicts: {wins} candidate / {losses} incumbent / {len(contrib)-wins-losses} neither-skip")
    print(f"net margin: {net:+d} records = {point:+.3f} pp   95% CI [{lo:+.3f}, {hi:+.3f}]")

    g1 = net > 0 and lo > 0
    print(f"\nGATE 1  margin positive, CI excludes zero : {'PASS' if g1 else 'FAIL'}")

    g2 = True
    print("GATE 2  division gate (min 10 divergents to bind):")
    for d, cs in sorted(by_div.items()):
        net_d = sum(cs)
        binding = len(cs) >= 10
        status = "net-negative" if net_d < 0 else "ok"
        if binding and net_d < 0:
            g2 = False
        print(f"   {d:14} divergents {len(cs):3}  net {net_d:+3}  {'BINDING' if binding else 'reported only'} {status}")
    print(f"GATE 2 verdict: {'PASS' if g2 else 'FAIL'}")

    tier = None
    if g1 and g2:
        tier = "strong" if point >= 1.5 else "measurable"
    print(f"\nRESULT: {'PASS — language tier: ' + tier if tier else 'FAIL — claim tier not passed'}")
    print(f"Scoring attempt: {args.attempt} of 2 (disclose in any claim).")


if __name__ == "__main__":
    main()
