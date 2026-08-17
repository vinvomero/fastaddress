"""Gold-2 as a DEV surface: human-labeled free text, independent of training.

Gold-2 is spent for claims -- both of its scoring attempts are used. Its 116
approved label sequences (rounds 7 and 8, human-adjudicated) remain the most
valuable steering signal this project owns, and the protocol has always
permitted a spent surface to serve as a dev tier: three of the gauntlet's six
checks already do.

Why this exists: the hard-class dev tier (realtext_hard_dev) was carved from
the same alignment rungs that built the training corpus, so it measured fit to
that generative process and called it transfer. It reported +5.333 pp for v50,
which then scored NEGATIVE on gold-2b. This surface cannot make that mistake:
its labels come from human adjudication, not from any process the corpus
shares.

Scoring: over records carrying an approved label sequence, a model is right
when its parse matches that sequence exactly. Reports each model's absolute
accuracy and the head-to-head net, with a bootstrap CI over the adjudicated
records. This is a DEV number. It is not a claim, it may not be published as
one, and gold-2's spent status is unchanged by running it.

Usage: python benchmark/gold2_dev.py --candidate model/candidates/v50.crfsuite
"""

import argparse
import collections
import csv
import json
import random
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "benchmark"))
from binpath import bin_path  # noqa: E402

ROUNDS = ["eval/gold2/verdicts_r7.json", "eval/gold2/verdicts_r8.json"]


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--baseline", default=None, help="compare against another model instead of v1")
    args = ap.parse_args()

    gold = {}
    for f in ROUNDS:
        for raw, v in json.loads((ROOT / f).read_text(encoding="utf-8")).items():
            if v.get("judged_labels"):
                gold[raw] = {"labels": v["judged_labels"], "state": v.get("state", "?")}
    raws = sorted(gold)
    base = tag(raws, args.baseline)
    cand = tag(raws, args.candidate)

    contrib, by_state = [], collections.defaultdict(list)
    b_ok = c_ok = 0
    shifts = collections.Counter()
    for raw, a, c in zip(raws, base, cand):
        want = gold[raw]["labels"]
        if len(a["labels"]) != len(want):
            continue
        ba, ca = a["labels"] == want, c["labels"] == want
        b_ok += ba
        c_ok += ca
        if ba != ca:
            contrib.append(1 if ca else -1)
            by_state[gold[raw]["state"]].append(1 if ca else -1)
            if not ca:
                for t, g, x in zip(c["tokens"], want, c["labels"]):
                    if g != x:
                        shifts[f"{g} -> {x}"] += 1
    n = len(raws)
    net = sum(contrib)
    rng = random.Random(20260819)
    pop = contrib + [0] * (n - len(contrib))
    boots = sorted(sum(rng.choices(pop, k=n)) / n * 100 for _ in range(10000))

    bname = args.baseline or "v1"
    print(f"gold-2 DEV surface: {n} human-adjudicated records (rounds 7-8)")
    print(f"exact match   {bname} {b_ok}/{n} ({b_ok/n*100:.1f}%)   "
          f"candidate {c_ok}/{n} ({c_ok/n*100:.1f}%)")
    print(f"head-to-head  {contrib.count(1)} candidate / {contrib.count(-1)} {bname}"
          f"   net {net:+d}   95% CI [{boots[250]:+.2f}, {boots[9750]:+.2f}] pp")
    if shifts:
        print("\ncandidate's wrong-label shifts on its losses:")
        for k, v in shifts.most_common(6):
            print(f"  {v:3}  {k}")
    print(f"\nDEV SIGNAL: {'candidate ahead' if net > 0 else 'candidate behind' if net < 0 else 'tied'}"
          "  (dev only -- never a claim; gold-2 stays spent)")


if __name__ == "__main__":
    main()
