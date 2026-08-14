"""Fold the human-reviewed confirmation round into the verdict record.

Rebuilds the exact worklist make_confirmation_doc.py produced (same candidate,
same seed, same filter), un-blinds the A/B letters through the key written for
that round, and marks each record human_reviewed.

The rebuild must be deterministic or the answers land on the wrong addresses,
so --verify prints every mapping for eyeball confirmation before anything is
written. Nothing is saved without --write.

Usage:
  python tools/ingest_confirmation.py --verify
  python tools/ingest_confirmation.py --write
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
CANDIDATE = "model/usaddr_v19.crfsuite"

# Verdicts as supplied, reviewed by a human, keyed by position in the doc.
ANSWERS = {
    1: "A", 2: "A", 3: "A", 4: "A", 5: "A", 6: "A", 7: "A", 8: "A", 9: "A", 10: "A",
    11: "A", 12: "A", 13: "A", 14: "A", 15: "A", 16: "A", 17: "A", 18: "A", 19: "A", 20: "A",
    21: "A", 22: "A", 23: "A", 24: "A", 25: "A", 26: "skip", 27: "A", 28: "A", 29: "A", 30: "A",
    31: "A", 32: "A", 33: "A", 34: "B", 35: "neither", 36: "A", 37: "A", 38: "A", 39: "A", 40: "A",
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


def build_todo():
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
        todo.append(raw)
    # Consume the same rng draw the doc generator made, so the key matches.
    random.Random(SEED).random()
    return todo, merged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    todo, merged = build_todo()
    key = json.loads((G / "blind_key-confirm.json").read_text(encoding="utf-8"))

    if len(todo) != len(ANSWERS):
        raise SystemExit(f"worklist is {len(todo)} records but {len(ANSWERS)} answers were given "
                         f"-- the doc was regenerated against a different candidate; do not guess")

    resolved = {}
    for pos, raw in enumerate(todo, 1):
        a = ANSWERS[pos]
        verdict = key[a] if a in ("A", "B") else a
        resolved[raw] = verdict
        if args.verify:
            print(f"{pos:3}. {a:8} -> {verdict:8}  {raw[:62]}")

    if args.verify:
        from collections import Counter
        print("\n" + str(Counter(resolved.values())))
        print("\nCheck these against the reviewer's own comments before writing:")
        for pos in (1, 19, 26, 33, 34, 35, 39):
            print(f"  #{pos}: {todo[pos-1]}")
        return

    if not args.write:
        print("nothing written; pass --verify or --write")
        return

    for raw, verdict in resolved.items():
        merged[raw] = {"verdict": verdict, "round": 4, "human_reviewed": True}
    (G / "verdicts-merged.json").write_text(json.dumps(merged, indent=1), encoding="utf-8")
    print(f"wrote {len(resolved)} human-reviewed verdicts into verdicts-merged.json")


if __name__ == "__main__":
    main()
