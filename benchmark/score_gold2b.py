"""Score a candidate against gold-2b under PROTOCOL2's frozen gates.

Gates carry over from gold-2 unchanged (margin CI; division gate with min-10;
coverage-floor language rules; two-attempt budget; human verdicts only). The
analysis structure is the owner's ruling of 2026-08-16:

  PRIMARY        strict-disjoint cohort (32 states, 2,912 records)
  SENSITIVITY-A  + the six same-lineage states
  SENSITIVITY-B  + the WI/WV/MN statewide aggregates
  ROBUSTNESS     PRIMARY without Wyoming

All four are reported together; only PRIMARY gates. Because the strict cohort
sits below the 40-state coverage floor, any claim from it uses the
pre-drafted enumerated-coverage phrasing, never the word "national".

Usage: python benchmark/score_gold2b.py --verdicts eval/gold2b/verdicts_r9.json
"""

import argparse
import collections
import json
import random
from pathlib import Path

ROOT = Path(__file__).parent.parent

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


def analyse(name, contribs, n_records, gate=False):
    """contribs: list of +1/-1/0 for adjudicated records in this cohort."""
    net = sum(c for c, _ in contribs)
    point = net / n_records * 100
    population = [c for c, _ in contribs] + [0] * (n_records - len(contribs))
    rng = random.Random(20260818)
    boots = sorted(sum(rng.choices(population, k=n_records)) / n_records * 100 for _ in range(10000))
    lo, hi = boots[250], boots[9750]
    wins = sum(1 for c, _ in contribs if c == 1)
    losses = sum(1 for c, _ in contribs if c == -1)
    neither = len(contribs) - wins - losses
    print(f"\n--- {name} ---")
    print(f"records {n_records}   adjudicated divergents {len(contribs)}"
          f"   ({wins} candidate / {losses} incumbent / {neither} neither)")
    print(f"net {net:+d} = {point:+.3f} pp   95% CI [{lo:+.3f}, {hi:+.3f}]")
    if gate:
        g1 = net > 0 and lo > 0
        print(f"GATE 1  margin positive, CI excludes zero : {'PASS' if g1 else 'FAIL'}")
        by_div = collections.defaultdict(list)
        for c, st in contribs:
            by_div[DIVISION.get(st, "?")].append(c)
        g2 = True
        print("GATE 2  division gate (min 10 divergents to bind):")
        for d, cs in sorted(by_div.items()):
            binding = len(cs) >= 10
            if binding and sum(cs) < 0:
                g2 = False
            print(f"   {d:14} divergents {len(cs):3}  net {sum(cs):+3}"
                  f"  {'BINDING' if binding else 'reported only'}"
                  f"{'  net-negative' if sum(cs) < 0 else ''}")
        print(f"GATE 2 verdict: {'PASS' if g2 else 'FAIL'}")
        return g1 and g2
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verdicts", default="eval/gold2b/verdicts_r9.json")
    ap.add_argument("--attempt", type=int, default=1)
    args = ap.parse_args()

    verd = json.loads((ROOT / args.verdicts).read_text(encoding="utf-8"))
    cohorts = json.loads((ROOT / "eval" / "gold2b" / "COHORTS.json").read_text(encoding="utf-8"))
    rows = [json.loads(l) for l in open(ROOT / "eval" / "gold2b" / "candidates.jsonl",
                                        encoding="utf-8-sig") if l.strip()]
    per_state = collections.Counter(r["state"] for r in rows)
    strict = set(cohorts["strict"])
    lineage = set(cohorts["lineage_sensitivity"])
    aggregate = set(cohorts["aggregate_sensitivity"])

    def contribs(states):
        return [({"v2": 1, "v1": -1}.get(v["verdict"], 0), v["state"])
                for v in verd.values() if v["state"] in states]

    def size(states):
        return sum(per_state[s] for s in states)

    print(f"Gold-2b scoring attempt {args.attempt} of 2 — human verdicts only")
    primary = analyse("PRIMARY (strict-disjoint, gating)", contribs(strict), size(strict), gate=True)
    sa = strict | lineage
    analyse("SENSITIVITY-A (+ same-lineage states)", contribs(sa), size(sa))
    sb = sa | aggregate
    analyse("SENSITIVITY-B (+ statewide aggregates)", contribs(sb), size(sb))
    nowy = strict - {"WY"}
    analyse("ROBUSTNESS (primary without WY)", contribs(nowy), size(nowy))

    print(f"\nRESULT: {'PASS' if primary else 'FAIL'} — the PRIMARY cohort gates; "
          f"sensitivity and robustness lines are reported, never substituted.")
    print(f"Scoring attempt: {args.attempt} of 2 (disclose in any claim).")


if __name__ == "__main__":
    main()
