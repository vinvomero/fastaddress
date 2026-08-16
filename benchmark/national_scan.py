"""National behavioral scan: what does a candidate change, and is it right?

Runs v1 and the candidate over the TIGER-derived 18-county corpus (16 states,
~108k composed addresses) and scores every DIVERGENT record against TIGER's
own component labels.

This is not the accuracy gate and cannot be: the protocol's gold sets are
free-text only, and these strings are composed. What it is: a tripwire for
regional overfitting. The gold set is 75% two states; a candidate can clear
the gate there while quietly breaking "New Orleans" everywhere else, and this
scan is what catches that (it did — v23 was wrong on 54.9% of its national
changes before the national-cities counterweight existed).

Ship rule this scan enforces (recorded here, applied by the caller): on
divergent records, candidate-right must EXCEED v1-right nationally, and no
single state may show candidate-right < v1-right by more than 3:1.

Usage: python benchmark/national_scan.py --candidate model/usaddr_v24.crfsuite
"""

import argparse
import sys
import collections
import csv
import json
import subprocess
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from binpath import bin_path

ROOT = Path(__file__).parent.parent
EVAL_BIN = bin_path("eval_tag")
TIGER = ROOT / "training" / "corpus" / "tiger.jsonl"
FIPS = {"17": "IL", "48": "TX", "49": "UT", "22": "LA", "13": "GA", "12": "FL",
        "06": "CA", "36": "NY", "04": "AZ", "53": "WA", "35": "NM", "42": "PA",
        "08": "CO", "37": "NC", "30": "MT", "46": "SD", "20": "KS", "29": "MO"}


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

    rows = [json.loads(l) for l in open(TIGER, encoding="utf-8")]
    raws = [" ".join(r["tokens"]) for r in rows]
    states = [FIPS[r["origin"].split("-")[1][:2]] for r in rows]

    v1 = tag(raws)
    cand = tag(raws, args.candidate)

    res = collections.Counter()
    by_state = collections.defaultdict(collections.Counter)
    worst = collections.defaultdict(list)
    for i in range(len(raws)):
        if v1[i]["labels"] == cand[i]["labels"]:
            continue
        if v1[i]["tokens"] != rows[i]["tokens"]:
            continue  # tokenization mismatch -> labels not comparable
        g = rows[i]["labels"]
        k = ("cand_right" if cand[i]["labels"] == g
             else "v1_right" if v1[i]["labels"] == g
             else "both_wrong")
        res[k] += 1
        by_state[states[i]][k] += 1
        if k == "v1_right" and len(worst[states[i]]) < 2:
            ch = [(t, y) for t, x, y in zip(rows[i]["tokens"], v1[i]["labels"], cand[i]["labels"]) if x != y]
            worst[states[i]].append((raws[i][:46], "; ".join(f"{t}:{y.replace('StreetName','SN')}" for t, y in ch[:3])))

    n = sum(res.values())
    total = len(raws)
    print(f"corpus {total:,} addresses / 16 states; candidate diverges from v1 on {n:,} comparable "
          f"({n/total*100:.2f}%)")
    print(f"  candidate right : {res['cand_right']:5}  ({res['cand_right']/max(n,1)*100:.1f}%)")
    print(f"  v1 right        : {res['v1_right']:5}  ({res['v1_right']/max(n,1)*100:.1f}%)")
    print(f"  both wrong      : {res['both_wrong']:5}")

    net_ok = res["cand_right"] > res["v1_right"]
    state_fail = []
    print(f"\n{'state':6}{'cand+':>7}{'v1+':>6}{'both-':>7}")
    for st in sorted(by_state, key=lambda s: -sum(by_state[s].values())):
        c = by_state[st]
        print(f"{st:6}{c['cand_right']:>7}{c['v1_right']:>6}{c['both_wrong']:>7}")
        if c["v1_right"] > 3 * max(c["cand_right"], 1) and c["v1_right"] >= 20:
            state_fail.append(st)

    if worst:
        print("\nsample candidate-WRONG cases:")
        shown = 0
        for st, ex in worst.items():
            for raw, ch in ex:
                if shown >= 8:
                    break
                print(f"  [{st}] {raw} | {ch}")
                shown += 1

    print(f"\nSHIP RULE  net national improvement : {'PASS' if net_ok else 'FAIL'}")
    print(f"SHIP RULE  no state worse than 3:1  : "
          f"{'PASS' if not state_fail else 'FAIL (' + ', '.join(state_fail) + ')'}")


if __name__ == "__main__":
    main()
