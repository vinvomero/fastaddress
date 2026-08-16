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

THIRD READINGS
--------------
A "v2" verdict says *the parse the reviewer was shown* was correct. It does not
say "anything other than v1 is correct". A newly trained model can differ from
v1 in a way nobody has ever judged, and scoring that as a win would be exactly
the blind spot that produced two false "no regressions" claims in this project:
the check would be structurally unable to see the failure it was meant to catch.

So --judged-parse takes the model whose output the reviewer actually saw. On a
"v2" record the candidate must reproduce *that* parse to count as a win. If it
emits a third reading, it is counted as UNKNOWN and reported for adjudication,
never as a win. Without the flag the script reports how many third readings
exist and refuses to treat them as decided.

Usage:
  python benchmark/full_set_margin.py --candidate model/usaddr_v20.crfsuite \\
      --judged-parse model/usaddr_v19.crfsuite
"""

import argparse
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
EVAL_BIN = bin_path("eval_tag")
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
    ap.add_argument("--judged-parse", default=None,
                    help="model whose output the reviewer actually saw; on a v2 record the "
                         "candidate must reproduce it to count as a win")
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

    judged = tag(raws, args.judged_parse) if args.judged_parse else None
    idx = {r: i for i, r in enumerate(raws)}

    # Per-record contribution to the margin numerator.
    contrib, unknown, third = [], 0, []
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
            # The reviewer approved a specific parse, not "anything but v1".
            # Round 5 onward stores that parse's labels on the record itself;
            # earlier rounds fall back to the --judged-parse model.
            i = idx[r]
            approved = info.get("judged_labels") or (judged[i]["labels"] if judged is not None else None)
            if approved is not None and cand[i]["labels"] != approved:
                third.append(r)
                unknown += 1
                continue
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
    if third:
        print(f"\n{len(third)} THIRD READINGS: the candidate differs from v1 *and* from the parse "
              f"the reviewer approved. Counted as unknown, not as wins — they need adjudication:")
        for r in third[:10]:
            print(f"   {r[:70]}")
    elif args.judged_parse is None:
        print("\nNOTE: --judged-parse not supplied, so a v2 record counts as a win whenever the "
              "candidate differs from v1 — including in a way nobody judged. Pass the model the "
              "reviewer actually saw to rule that out.")

    if unjudged:
        print(f"\nWARNING: {len(unjudged)} differing records carry no verdict, so the margin above "
              f"is not exact. Adjudicate them to close this. Examples:")
        for r in unjudged[:10]:
            print(f"   {r[:70]}")


if __name__ == "__main__":
    main()
