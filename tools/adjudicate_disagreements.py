"""Disagreement triage for gold adjudication (findings round 1).

Adjudicating all 1,500 gold candidates is expensive; only the records where two
models disagree can change a relative verdict. This writes
eval/gold/disagreements.jsonl — one record per contested address with both
models' labels side by side and a blank `verdict` field ("v1", "v2", "neither").

Methodological note (must accompany any result): adjudicating only contested
records measures RELATIVE accuracy on contested cases, not absolute accuracy on
the full set. It answers "when they differ, who is right more often?" — useful
triage, not a substitute for the protocol's full-set gate.

Usage:
  python tools/adjudicate_disagreements.py --candidate model/usaddr_v2_r4.crfsuite
"""

import argparse
import csv
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent
GOLD = ROOT / "eval" / "gold" / "candidates.jsonl"
OUT = ROOT / "eval" / "gold" / "disagreements.jsonl"
EVAL_BIN = "C:/cargo-target/us-address-parser/release/eval_tag.exe"


def tag_all(rows, eval_bin, model=None):
    with tempfile.NamedTemporaryFile(
        "w", suffix=".csv", delete=False, encoding="utf-8", newline=""
    ) as tf:
        w = csv.writer(tf)
        w.writerow(["raw_address"])
        for r in rows:
            w.writerow([r["raw"]])
        tmp = tf.name
    cmd = [eval_bin, tmp] + (["--model", model] if model else [])
    out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=True)
    return [json.loads(l) for l in out.stdout.splitlines() if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--eval-bin", default=EVAL_BIN)
    args = ap.parse_args()

    rows = [json.loads(l) for l in open(GOLD, encoding="utf-8") if l.strip()]
    v1 = tag_all(rows, args.eval_bin)
    v2 = tag_all(rows, args.eval_bin, args.candidate)

    contested = []
    for r, a, b in zip(rows, v1, v2):
        if a["labels"] != b["labels"]:
            contested.append(
                {
                    "raw": r["raw"],
                    "source": r["source"],
                    "tokens": a["tokens"],
                    "v1_labels": a["labels"],
                    "v2_labels": b["labels"],
                    "differing_tokens": [
                        {"token": t, "v1": x, "v2": y}
                        for t, x, y in zip(a["tokens"], a["labels"], b["labels"])
                        if x != y
                    ],
                    "verdict": "",  # "v1" | "v2" | "neither" — filled by adjudicator
                    "notes": "",
                }
            )
    with open(OUT, "w", encoding="utf-8") as f:
        for c in contested:
            f.write(json.dumps(c) + "\n")
    print(f"{len(contested)} contested of {len(rows)} ({len(contested)/len(rows)*100:.1f}%) -> {OUT}")


if __name__ == "__main__":
    main()
