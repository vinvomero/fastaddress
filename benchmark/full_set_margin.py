"""Exact full-set gold margin from contested-only adjudication.

WHY THIS EXISTS
---------------
PROTOCOL.md's gold gate is written against the full 1,500-record gold set
("exact-match rate ... exceeds the original model's by at least +3.0
percentage points"), but only the records where the two models disagree were
ever adjudicated. That looked like a gap between what was promised and what
was measured.

It is closeable exactly, without adjudicating the other ~1,400 records:

    margin = [correct(candidate) - correct(v1)] / N

A record where both models emit the SAME parse is either right for both or
wrong for both. Either way it adds the same amount to both terms of the
numerator, so it contributes exactly zero to the margin. The margin is
therefore fully determined by the records where the two models differ -- and
those are precisely the records that were adjudicated.

THE PREMISE THIS RESTS ON
-------------------------
The argument is only valid if the adjudicated set covers EVERY differing
record. If some differing record was never judged, the margin has an unmeasured
term and the number below is not exact. This script does not assume that -- it
recomputes the differing set from scratch and reports any record that differs
but carries no verdict. Two earlier "no regressions" claims in this project
were wrong because the check was structurally blind to records it never looked
at; this one names its blind spot instead of inheriting it.

Verdict arithmetic (per differing record):
    v1      -> incumbent right, candidate wrong   -> -1
    v2      -> candidate right, incumbent wrong   -> +1
    neither -> both wrong                         ->  0
    skip / unadjudicated -> unknown, reported as a bound, never scored

Usage: python benchmark/full_set_margin.py --candidate model/usaddr_v2.crfsuite
"""

import argparse
import csv
import json
import random
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent
EVAL_BIN = "C:/cargo-target/us-address-parser/release/eval_tag.exe"
BOOTSTRAP = 10000
SEED = 20260814


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
    ap.add_argument("--human-only", action="store_true",
                    help="score only verdicts confirmed by a human reviewer")
    args = ap.parse_args()

    gold = [json.loads(l) for l in open(ROOT / "eval" / "gold" / "candidates.jsonl", encoding="utf-8-sig") if l.strip()]
    raws = [r["raw"] for r in gold]
    n = len(gold)

    base = tag(raws)
    cand = tag(raws, args.candidate)
    merged = json.loads((ROOT / "eval" / "gold" / "verdicts-merged.json").read_text(encoding="utf-8"))

    differ = [raws[i] for i in range(n) if base[i]["labels"] != cand[i]["labels"]]
    judged = set(merged)

    print(f"gold set                     {n} records")
    print(f"models produce the same parse on  {n - len(differ)} ({(n-len(differ))/n*100:.1f}%)  -> contribute 0 to the margin")
    print(f"models differ on                  {len(differ)}")

    unjudged = [r for r in differ if r not in judged]
    print(f"  of those, adjudicated           {len(differ) - len(unjudged)}")
    print(f"  of those, NOT adjudicated       {len(unjudged)}   <- the only unmeasured term")

    # Per-record contribution to the margin numerator.
    contrib, unknown = [], 0
    for r in differ:
        info = merged.get(r)
        if info is None:
            unknown += 1
            continue
        if args.human_only and not info.get("human_reviewed"):
            unknown += 1
            continue
        v = info["verdict"]
        if v == "v2":
            contrib.append(1)
        elif v == "v1":
            contrib.append(-1)
        elif v == "neither":
            contrib.append(0)
        else:
            unknown += 1

    # Records where the models agree contribute a hard zero, and they are part
    # of the population being resampled -- so they belong in the bootstrap.
    population = contrib + [0] * (n - len(differ))
    point = sum(contrib) / n

    rng = random.Random(SEED)
    diffs = []
    for _ in range(BOOTSTRAP):
        s = sum(rng.choices(population, k=len(population)))
        diffs.append(s / len(population))
    diffs.sort()
    lo = diffs[int(0.025 * BOOTSTRAP)]
    hi = diffs[int(0.975 * BOOTSTRAP)]

    scope = "human-reviewed verdicts only" if args.human_only else "all verdicts"
    print(f"\n--- full-set margin ({scope}) ---")
    print(f"candidate wins {contrib.count(1)}   incumbent wins {contrib.count(-1)}   "
          f"both wrong {contrib.count(0)}   unknown {unknown}")
    print(f"point estimate  {point*100:+.2f} pp")
    print(f"95% bootstrap CI [{lo*100:+.2f}, {hi*100:+.2f}] pp  ({BOOTSTRAP} resamples, seed {SEED})")

    # Worst/best case if every unknown record went the wrong/right way.
    if unknown:
        print(f"bounds if all {unknown} unknown records resolved against / for the candidate: "
              f"{(sum(contrib)-unknown)/n*100:+.2f} pp  ..  {(sum(contrib)+unknown)/n*100:+.2f} pp")

    gate_pp, gate_ci = 3.0, lo > 0
    print(f"\nPROTOCOL gate: >= +3.0 pp AND 95% CI excludes zero")
    print(f"  margin >= +3.0 pp : {'PASS' if point*100 >= gate_pp else 'FAIL'}")
    print(f"  CI excludes zero  : {'PASS' if gate_ci else 'FAIL'}")
    if unjudged:
        print(f"\nWARNING: {len(unjudged)} differing records carry no verdict, so the margin above "
              f"is not exact. Adjudicate them to close this. Examples:")
        for r in unjudged[:10]:
            print(f"   {r[:70]}")


if __name__ == "__main__":
    main()
