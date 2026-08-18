"""Emit the low-confidence labeling candidates as a fill-out CSV.

One row per address. The reviewer fills the `answer` column:
  ok                      the proposed parse is correct
  TOKEN=Label; ...        correct only the named tokens (gold-2c grammar)
  skip                    ambiguous / would be guessing
  (blank)                 not reviewed -- ignored on ingest, so partial is fine

Excel-friendly (UTF-8 BOM, quoted). The proposed_parse column shows the
model's current reading so a glance is enough to answer.

Usage: python training/humanlabel/make_label_csv.py --max-confidence 0.90
"""
import argparse
import csv
import json
from pathlib import Path

HERE = Path(__file__).parent
CANDS = HERE / "candidates_for_labeling.jsonl"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-confidence", type=float, default=0.90)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(CANDS, encoding="utf-8") if l.strip()]
    sel = [r for r in rows if r["min_confidence"] < a.max_confidence]
    out = Path(a.out) if a.out else HERE / f"label_batch_lt{int(a.max_confidence*100)}.csv"

    with open(out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["num", "confidence", "state", "address", "proposed_parse", "answer"])
        for n, r in enumerate(sel, 1):
            parse = " ".join(f"{t}={l}" for t, l in zip(r["prelabel_tokens"], r["prelabel_labels"]))
            w.writerow([n, f"{r['min_confidence']:.3f}", r["state"], r["raw"], parse, ""])
    print(f"{len(sel)} records (confidence < {a.max_confidence}) -> {out}")


if __name__ == "__main__":
    main()
