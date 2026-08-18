"""Emit batch-2 candidates as a fill-out CSV, grouped by target class.

Same answer grammar as batch 1: ok / TOKEN=Label; ... / skip / blank.
Grouped by class so you can label one bucket per sitting and we can measure
per-class movement on gold-2c afterward.

Usage: python training/humanlabel/make_label_csv2.py
"""
import csv, json
from pathlib import Path

HERE = Path(__file__).parent
rows = [json.loads(l) for l in open(HERE / "candidates_batch2.jsonl", encoding="utf-8") if l.strip()]
order = ["recipient", "abbrev_city", "route", "stateish_city", "directional",
         "multiword_place", "suffix_present"]
rows.sort(key=lambda r: (order.index(r["target_class"]), r["min_confidence"]))
out = HERE / "label_batch2.csv"
with open(out, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["num", "target_class", "confidence", "state", "address", "proposed_parse", "answer"])
    for n, r in enumerate(rows, 1):
        parse = " ".join(f"{t}={l}" for t, l in zip(r["prelabel_tokens"], r["prelabel_labels"]))
        w.writerow([n, r["target_class"], f"{r['min_confidence']:.3f}", r["state"], r["raw"], parse, ""])
print(f"{len(rows)} records -> {out}")
