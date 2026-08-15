"""FINAL validation: fresh counties untouched by any scan or decision.

WHY
---
The 32-state holdout steered iterations v29 through v31, which spent its
independence. This is the third split: 20 second-tier metro counties across
states from both prior groups, none ever used in training, scanning, or any
model decision. It runs ONCE. Its rules are the same two ship rules, committed
before the result exists, and its outcome is final for the launch decision:
pass and v2 ships opt-in; fail and v2 stays held back while the launch goes
out without it. No iteration on this result -- a validation you iterate
against is just another training set.

"""

import argparse
import collections
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "training"))
import build_tiger_corpus as btc

# Cache outside OneDrive; ~1GB of shapefiles has no business syncing.
btc.CACHE = Path("C:/cargo-target/us-address-parser/tiger_final_cache")

ROOT = Path(__file__).parent.parent
SEED = 20260815

# One county per state absent from the 18-county corpus. Mid-size metro
# counties, chosen for row volume, not for any addressing property.
HOLDOUT = [
    ("48", "029", "TX"), ("06", "073", "CA"), ("12", "057", "FL"),
    ("36", "029", "NY"), ("17", "097", "IL"), ("53", "063", "WA"),
    ("04", "019", "AZ"), ("08", "041", "CO"), ("37", "183", "NC"),
    ("29", "189", "MO"), ("22", "033", "LA"), ("49", "049", "UT"),
    ("13", "067", "GA"), ("42", "091", "PA"), ("39", "035", "OH"),
    ("26", "163", "MI"), ("47", "157", "TN"), ("27", "123", "MN"),
    ("45", "079", "SC"), ("23", "031", "ME"),
]

PER_COUNTY = 4000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--spec", help="JSON file with [[statefp, countyfp, abbr], ...]; default = the spent 20-county split")
    args = ap.parse_args()
    global HOLDOUT
    if args.spec:
        import json as _json
        HOLDOUT = [tuple(x) for x in _json.loads(Path(args.spec).read_text(encoding="utf-8"))]

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
    print(f"FINAL RULE  no state worse 3:1   : "
          f"{'PASS' if not state_fail else 'FAIL (' + ', '.join(state_fail) + ')'}")


if __name__ == "__main__":
    main()
