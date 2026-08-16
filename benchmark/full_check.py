"""Comprehensive candidate check: clean gate + EVERY adjudicated record.

Supersedes the round-scoped checks. Two premature "no regressions" claims came
from evaluating against only one round's verdicts; this evaluates against the
merged per-address verdict file, so any judged record a candidate gets wrong
shows up regardless of which round judged it.

Semantics per verdict:
  v1      -> the incumbent's parse was correct; the candidate must MATCH v1
  v2      -> the challenger-style parse was correct; the candidate must DIFFER from v1
  neither -> both were wrong; not scored either way (improvement opportunity)
  skip    -> ambiguous; not scored

Usage: python benchmark/full_check.py --candidate model/usaddr_v16.crfsuite
"""

import argparse
import sys
import csv
import json
import subprocess
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from binpath import bin_path

ROOT = Path(__file__).parent.parent
EVAL_BIN = bin_path("eval_tag")


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


def load_jsonl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8-sig") if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    args = ap.parse_args()

    clean = load_jsonl(ROOT / "eval" / "clean" / "clean.jsonl")
    raws = [r["raw"] for r in clean]
    base, cand = tag(raws), tag(raws, args.candidate)

    def exact(preds):
        return sum(1 for g, p in zip(clean, preds) if g["tokens"] == p["tokens"] and g["labels"] == p["labels"])

    v1c, cc, n = exact(base), exact(cand), len(clean)
    clean_ok = cc >= v1c
    print(f"CLEAN GATE      v1 {v1c}/{n} ({v1c/n*100:.2f}%)   candidate {cc}/{n} ({cc/n*100:.2f}%)  "
          f"{'PASS' if clean_ok else 'FAIL'}")

    merged = json.loads((ROOT / "eval" / "gold" / "verdicts-merged.json").read_text(encoding="utf-8"))
    gold = load_jsonl(ROOT / "eval" / "gold" / "candidates.jsonl")
    graws = [r["raw"] for r in gold]
    gv1, gc = tag(graws), tag(graws, args.candidate)
    idx = {r["raw"]: i for i, r in enumerate(gold)}

    ok, bad, both_wrong, skipped = 0, [], 0, 0
    human_bad = 0
    for addr, info in merged.items():
        i = idx.get(addr)
        if i is None:
            continue
        differs = gv1[i]["labels"] != gc[i]["labels"]
        v = info["verdict"]
        if v == "v1":
            (ok := ok + 1) if not differs else bad.append((addr, info))
            if differs and info.get("human_reviewed"):
                human_bad += 1
        elif v == "v2":
            if differs:
                ok += 1
            else:
                bad.append((addr, info))
                if info.get("human_reviewed"):
                    human_bad += 1
        elif v == "neither":
            both_wrong += 1
        else:
            skipped += 1

    print(f"JUDGED RECORDS  matches adjudicated answer on {ok}, fails {len(bad)} "
          f"({human_bad} of them human-reviewed), both-wrong {both_wrong}, skip {skipped}")
    for addr, info in bad[:10]:
        print(f"   FAIL (round {info['round']}{', human' if info.get('human_reviewed') else ''}): {addr[:60]}")
    verdict = "STRICTLY BETTER OR EQUAL" if (clean_ok and not bad) else "NOT YET CLEAN"
    print(f"\nVERDICT: {verdict}")


if __name__ == "__main__":
    main()
