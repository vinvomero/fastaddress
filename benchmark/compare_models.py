"""Head-to-head comparison of a candidate model against v1 (plan: the
'better in every way' check).

Reports, for a candidate:
  1. Clean-set exact match vs v1 (the pre-registered regression gate)
  2. Saint-name class: does the candidate fix the class v1 is adjudicated wrong on?
  3. Regression check: on the previously-contested records where v1 was judged
     CORRECT, does the candidate now agree with v1?
  4. New disagreements introduced against v1 across the full gold candidate set

'Better in every way' means: clean gate held, saint-name class fixed, zero
regressions on v1's adjudicated wins, and no large new disagreement surface.

Usage: python benchmark/compare_models.py --candidate model/usaddr_v3.crfsuite
"""

import argparse
import csv
import json
import re
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent
EVAL_BIN = "C:/cargo-target/us-address-parser/release/eval_tag.exe"
SAINT_RE = re.compile(r"^\s*\d+\s+ST\.?\s+\w", re.IGNORECASE)


def tag(rows, model=None):
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8", newline="") as tf:
        w = csv.writer(tf)
        w.writerow(["raw_address"])
        for r in rows:
            w.writerow([r])
        tmp = tf.name
    cmd = [EVAL_BIN, tmp] + (["--model", model] if model else [])
    out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=True)
    return [json.loads(l) for l in out.stdout.splitlines() if l.strip()]


def load_jsonl(p):
    # utf-8-sig: files recovered via shell redirect can carry a BOM.
    return [json.loads(l) for l in open(p, encoding="utf-8-sig") if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    args = ap.parse_args()

    # --- 1. clean gate
    clean = load_jsonl(ROOT / "eval" / "clean" / "clean.jsonl")
    raws = [r["raw"] for r in clean]
    base, cand = tag(raws), tag(raws, args.candidate)
    def exact(preds):
        return sum(1 for g, p in zip(clean, preds) if g["tokens"] == p["tokens"] and g["labels"] == p["labels"])
    v1_clean, cand_clean = exact(base), exact(cand)
    n = len(clean)

    # --- 2/3/4. gold candidates
    gold = load_jsonl(ROOT / "eval" / "gold" / "candidates.jsonl")
    graws = [r["raw"] for r in gold]
    g_v1, g_cand = tag(graws), tag(graws, args.candidate)

    saint_idx = [i for i, r in enumerate(gold) if SAINT_RE.match(r["raw"])]
    saint_fixed = sum(1 for i in saint_idx if g_cand[i]["labels"] != g_v1[i]["labels"])

    # regression check against adjudicated v1-wins
    # Round-1 adjudicated v1-wins. NOTE: this set alone is not a sufficient
    # regression check — it only covers shapes that existed in round 1. New
    # shapes a candidate introduces are checked separately below, a gap that
    # let an earlier candidate report "zero regressions" while losing 3 of 4
    # decided new-shape comparisons.
    key = json.loads((ROOT / "eval" / "gold" / "blind_key-prior.json").read_text(encoding="utf-8-sig"))
    verd = json.loads((ROOT / "eval" / "gold" / "verdicts-chatgpt-2026-08-13.json").read_text(encoding="utf-8-sig"))
    gv = {int(k): v for k, v in verd["groups"].items()}
    exc = verd.get("exceptions", {})
    dis = load_jsonl(ROOT / "eval" / "gold" / "disagreements-prior.jsonl")
    groups = defaultdict(list)
    for r in dis:
        groups[tuple((d["v1"], d["v2"]) for d in r["differing_tokens"])].append(r)
    ordered = sorted(groups.values(), key=len, reverse=True)
    v1_wins = []
    for i, grp in enumerate(ordered, 1):
        for r in grp:
            raw_v = exc.get(r["raw"], gv.get(i, "skip"))
            if key.get(raw_v, raw_v) == "v1":
                v1_wins.append(r["raw"])
    idx_by_raw = {r["raw"]: i for i, r in enumerate(gold)}
    held, lost = 0, []
    for raw in v1_wins:
        i = idx_by_raw.get(raw)
        if i is None:
            continue
        if g_cand[i]["labels"] == g_v1[i]["labels"]:
            held += 1
        else:
            lost.append(raw)

    new_dis = [i for i in range(len(gold)) if g_v1[i]["labels"] != g_cand[i]["labels"]]
    new_non_saint = [i for i in new_dis if i not in set(saint_idx)]

    print(f"CLEAN GATE     v1 {v1_clean}/{n} ({v1_clean/n*100:.2f}%)  candidate {cand_clean}/{n} ({cand_clean/n*100:.2f}%)")
    print(f"SAINT CLASS    {len(saint_idx)} records; candidate differs from v1 on {saint_fixed} (v1 is adjudicated wrong here)")
    print(f"REGRESSIONS    v1's {len(v1_wins)} adjudicated wins: candidate matches v1 on {held}, diverges on {len(lost)}")
    for raw in lost[:8]:
        print(f"   lost: {raw[:60]}")
    print(f"NEW SURFACE    candidate differs from v1 on {len(new_dis)}/{len(gold)} gold rows "
          f"({len(new_non_saint)} outside the saint class)")

    # Round-2 adjudication of the shapes a candidate newly introduced.
    r2 = ROOT / "eval" / "gold" / "verdicts-round2-2026-08-14.json"
    k2 = ROOT / "eval" / "gold" / "blind_key.json"
    if r2.exists() and k2.exists():
        v2v = json.loads(r2.read_text(encoding="utf-8-sig"))
        key2 = json.loads(k2.read_text(encoding="utf-8-sig"))
        counts = {"v1": 0, "v2": 0, "neither": 0, "skip": 0}
        for letter in v2v["fresh_groups"].values():
            counts[key2.get(letter, letter)] += 1
        print(f"NEW-SHAPE ADJ  of the newly-introduced shapes: candidate correct {counts['v2']}, "
              f"v1 correct {counts['v1']}, both wrong {counts['neither']} "
              f"(losses here are regressions the round-1 set cannot see)")


if __name__ == "__main__":
    main()
