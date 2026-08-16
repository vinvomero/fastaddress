"""Geographic holdout: states no iteration decision ever touched.

WHY
---
The 16-state national scan steered six rounds of model iteration, which makes
it training-adjacent in the way that matters: every v24-v28 fix was chosen by
looking at its failures. A model can be shaped to a benchmark by exactly that
loop. Before claiming v2 behaves better outside the gold set's home turf, it
has to be measured somewhere no decision ever saw.

This scan composes addresses from one county in each of ~32 states that appear
in NEITHER the 18-county training/scan corpus NOR any iteration decision, and
scores v1 vs the candidate on the records where they disagree, against the
Census's own component labels. Same scoring and the same two ship rules as
national_scan.py.

The same honesty caveat applies, stated rather than hidden: the ground truth
is composed from Census components, and the candidate's counterweight
generators draw on the same Census vocabularies. Free-text is what the
planned national gold set is for. What THIS scan uniquely tests is geographic
generalization: street patterns, city names, and route styles that never
influenced any training or selection decision.

Usage: python benchmark/holdout_scan.py --candidate model/usaddr_v2.crfsuite
"""

import argparse
import collections
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "training"))
import build_tiger_corpus as btc
import os as _os
_legacy = Path("C:/cargo-target/us-address-parser")
_cache_root = Path(_os.environ.get("FASTADDRESS_CACHE_DIR",
    str(_legacy if _legacy.exists() else Path.home() / ".cache" / "fastaddress")))

# Cache outside OneDrive; ~1GB of shapefiles has no business syncing.
btc.CACHE = _cache_root / "tiger_holdout_cache"

ROOT = Path(__file__).parent.parent
SEED = 20260815

# One county per state absent from the 18-county corpus. Mid-size metro
# counties, chosen for row volume, not for any addressing property.
HOLDOUT = [
    ("39", "049", "OH"), ("26", "081", "MI"), ("51", "059", "VA"),
    ("25", "027", "MA"), ("47", "037", "TN"), ("18", "097", "IN"),
    ("27", "053", "MN"), ("55", "025", "WI"), ("41", "051", "OR"),
    ("40", "143", "OK"), ("01", "073", "AL"), ("05", "119", "AR"),
    ("09", "110", "CT"), ("10", "003", "DE"), ("15", "003", "HI"),
    ("19", "153", "IA"), ("16", "001", "ID"), ("21", "111", "KY"),
    ("23", "005", "ME"), ("24", "005", "MD"), ("28", "049", "MS"),
    ("31", "055", "NE"), ("33", "011", "NH"), ("34", "003", "NJ"),
    ("38", "017", "ND"), ("32", "031", "NV"), ("44", "007", "RI"),
    ("45", "045", "SC"), ("50", "007", "VT"), ("54", "039", "WV"),
    ("56", "021", "WY"), ("02", "020", "AK"),
]

PER_COUNTY = 4000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    args = ap.parse_args()

    rng = random.Random(SEED)
    rows = []
    place_cache = {}
    for statefp, countyfp, abbr in HOLDOUT:
        try:
            if statefp not in place_cache:
                place_cache[statefp] = btc.load_places(statefp)
            got, _ = btc.county_rows(statefp, countyfp, abbr, PER_COUNTY, rng, place_cache[statefp])
        except Exception as e:
            print(f"  {abbr} {statefp}{countyfp}: SKIPPED ({type(e).__name__}: {str(e)[:60]})", flush=True)
            continue
        # No noise transform: this is evaluation text, not training text.
        # Drop rows whose city text is a Census bookkeeping label (hyphens,
        # slashes, parentheses): "Nashville-Davidson metropolitan government
        # (balance)" is a filing name, not an address anyone writes; the first
        # run of this scan showed 11,335 such rows masquerading as failures.
        for r in got:
            city = [t for t, l in zip(r["tokens"], r["labels"]) if l == "PlaceName"]
            if city and all(t.isalpha() for t in city):
                rows.append({"tokens": r["tokens"], "labels": r["labels"], "state": abbr})
        print(f"  {abbr}: {len(got)} rows", flush=True)

    raws = [" ".join(r["tokens"]) for r in rows]
    from national_scan import tag  # same eval binary path and CSV protocol
    v1 = tag(raws)
    cand = tag(raws, args.candidate)

    res = collections.Counter()
    by_state = collections.defaultdict(collections.Counter)
    worst = collections.defaultdict(list)
    for i, r in enumerate(rows):
        if v1[i]["labels"] == cand[i]["labels"]:
            continue
        if v1[i]["tokens"] != r["tokens"]:
            continue
        g = r["labels"]
        k = ("cand_right" if cand[i]["labels"] == g
             else "v1_right" if v1[i]["labels"] == g
             else "both_wrong")
        res[k] += 1
        by_state[r["state"]][k] += 1
        if k == "v1_right" and len(worst[r["state"]]) < 1:
            ch = [(t, y) for t, x, y in zip(r["tokens"], v1[i]["labels"], cand[i]["labels"]) if x != y]
            worst[r["state"]].append((raws[i][:46], "; ".join(f"{t}:{y.replace('StreetName','SN')}" for t, y in ch[:3])))

    n = sum(res.values())
    print(f"\nHOLDOUT: {len(rows):,} addresses / {len(by_state)} states never used in any "
          f"training or iteration decision")
    print(f"candidate diverges from v1 on {n:,} comparable ({n/max(len(rows),1)*100:.2f}%)")
    print(f"  candidate right : {res['cand_right']:5}  ({res['cand_right']/max(n,1)*100:.1f}%)")
    print(f"  v1 right        : {res['v1_right']:5}  ({res['v1_right']/max(n,1)*100:.1f}%)")
    print(f"  both wrong      : {res['both_wrong']:5}")

    state_fail = []
    print(f"\n{'state':6}{'cand+':>7}{'v1+':>6}{'both-':>7}")
    for st in sorted(by_state, key=lambda s: -sum(by_state[s].values())):
        c = by_state[st]
        print(f"{st:6}{c['cand_right']:>7}{c['v1_right']:>6}{c['both_wrong']:>7}")
        if c["v1_right"] > 3 * max(c["cand_right"], 1) and c["v1_right"] >= 20:
            state_fail.append(st)

    print("\nsample candidate-WRONG cases (one per state where any exist):")
    shown = 0
    for st, ex in worst.items():
        for raw, ch in ex:
            if shown >= 10:
                break
            print(f"  [{st}] {raw} | {ch}")
            shown += 1

    net_ok = res["cand_right"] > res["v1_right"]
    print(f"\nHOLDOUT RULE  net improvement      : {'PASS' if net_ok else 'FAIL'}")
    print(f"HOLDOUT RULE  no state worse 3:1   : "
          f"{'PASS' if not state_fail else 'FAIL (' + ', '.join(state_fail) + ')'}")


if __name__ == "__main__":
    main()
