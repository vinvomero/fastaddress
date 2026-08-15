"""Fold round 5 (the v23-deciding review) into the verdict record.

Same discipline as ingest_confirmation.py: rebuild the worklist
deterministically, verify the answer-to-address mapping against the reviewer's
own comments before writing, un-blind through the round's key.

One improvement: each record stores the exact label sequence the reviewer
approved (`judged_labels`). Rounds 1-4 recorded only "the candidate's parse
was right", which forced the margin script to reconstruct WHICH parse the
reviewer saw from a --judged-parse model argument. Storing the labels
themselves makes every future margin computation self-contained and immune to
the third-reading ambiguity.

Usage:
  python tools/ingest_round5.py --verify
  python tools/ingest_round5.py --write
"""

import argparse
import csv
import json
import random
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent
G = ROOT / "eval" / "gold"
EVAL_BIN = "C:/cargo-target/us-address-parser/release/eval_tag.exe"
SEED = 20260814
CANDIDATE = "model/usaddr_v23.crfsuite"

# Round-5 verdicts as supplied, reviewed by the human reviewer, keyed by doc position.
ANSWERS = {
    1: "A", 2: "A", 3: "B", 4: "A", 5: "A", 6: "A", 7: "A", 8: "A", 9: "A", 10: "A",
    11: "A", 12: "A", 13: "A", 14: "A", 15: "A", 16: "A", 17: "A", 18: "A", 19: "A", 20: "A",
    21: "A", 22: "A", 23: "A", 24: "A", 25: "A", 26: "A", 27: "A", 28: "B", 29: "A", 30: "A",
    31: "A", 32: "A", 33: "A", 34: "A", 35: "A", 36: "A",
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
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    gold = [json.loads(l) for l in open(G / "candidates.jsonl", encoding="utf-8-sig") if l.strip()]
    raws = [r["raw"] for r in gold]
    base, cand = tag(raws), tag(raws, CANDIDATE)
    merged = json.loads((G / "verdicts-merged.json").read_text(encoding="utf-8"))

    todo = []
    for i, raw in enumerate(raws):
        if base[i]["labels"] == cand[i]["labels"]:
            continue
        info = merged.get(raw)
        if info and info.get("human_reviewed"):
            continue
        todo.append((raw, base[i]["labels"], cand[i]["labels"]))
    random.Random(SEED).random()  # consume the key draw, matching the doc generator

    key = json.loads((G / "blind_key-confirm.json").read_text(encoding="utf-8"))
    if len(todo) != len(ANSWERS):
        raise SystemExit(f"worklist has {len(todo)} records, {len(ANSWERS)} answers given -- refusing to guess")

    resolved = {}
    for pos, (raw, v1_labels, v23_labels) in enumerate(todo, 1):
        a = ANSWERS[pos]
        verdict = key[a] if a in ("A", "B") else a
        judged = v23_labels if verdict == "v2" else v1_labels if verdict == "v1" else None
        resolved[raw] = (verdict, judged)
        if args.verify:
            print(f"{pos:3}. {a:8} -> {verdict:8}  {raw[:62]}")

    if args.verify:
        from collections import Counter
        print("\n" + str(Counter(v for v, _ in resolved.values())))
        print("\nSpot-checks against the reviewer's comments:")
        for pos in (1, 3, 15, 19, 23, 28):
            print(f"  #{pos}: {todo[pos-1][0]}")
        return

    if not args.write:
        print("nothing written; pass --verify or --write")
        return

    for raw, (verdict, judged) in resolved.items():
        rec = {"verdict": verdict, "round": 5, "human_reviewed": True}
        if judged is not None:
            rec["judged_labels"] = judged
        merged[raw] = rec
    (G / "verdicts-merged.json").write_text(json.dumps(merged, indent=1), encoding="utf-8")
    print(f"wrote {len(resolved)} round-5 verdicts (with judged label sequences) into verdicts-merged.json")


if __name__ == "__main__":
    main()
