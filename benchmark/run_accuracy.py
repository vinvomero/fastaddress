"""Accuracy harness (eval/PROTOCOL.md): scores models on the gold and clean
sets, reporting full-address exact match, per-label precision/recall/F1, and
(when comparing two models) the paired exact-match difference with a bootstrap
95% CI. Gate arithmetic uses only status=='adjudicated' gold records.

Usage:
  python benchmark/run_accuracy.py [--candidate path/to/model.crfsuite]

Without --candidate, produces the baseline report for the embedded original.
"""

import argparse
import csv
import json
import random
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

import sys as _sys
from pathlib import Path as _P
_sys.path.insert(0, str(_P(__file__).resolve().parent))
from binpath import bin_path

ROOT = Path(__file__).parent.parent
GOLD = ROOT / "eval" / "gold" / "candidates.jsonl"
CLEAN = ROOT / "eval" / "clean" / "clean.jsonl"
RESULTS = Path(__file__).parent / "results"
BOOTSTRAP_N = 2000
GOLD_MARGIN_PP = 3.0
CLEAN_REGRESSION_PP = 1.0


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def run_eval_tag(eval_bin, rows, model=None):
    """Tag raw strings via the Rust harness binary; returns list of label lists."""
    with tempfile.NamedTemporaryFile(
        "w", suffix=".csv", delete=False, encoding="utf-8", newline=""
    ) as tf:
        w = csv.writer(tf)
        w.writerow(["raw_address"])
        for r in rows:
            w.writerow([r["raw"]])
        tmp = tf.name
    cmd = [eval_bin, tmp] + (["--model", model] if model else [])
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=True)
    preds = [json.loads(line) for line in proc.stdout.splitlines() if line.strip()]
    assert len(preds) == len(rows)
    return preds


def score(rows, preds):
    """rows carry gold tokens+labels; preds carry predicted tokens+labels."""
    exact, per_label = [], defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
    skipped_tokenization = 0
    for gold, pred in zip(rows, preds):
        if gold["tokens"] != pred["tokens"]:
            # Tokenization mismatch (raw reconstruction artifact): count as miss.
            skipped_tokenization += 1
            exact.append(0)
            continue
        match = gold["labels"] == pred["labels"]
        exact.append(1 if match else 0)
        for g, p in zip(gold["labels"], pred["labels"]):
            if g == p:
                per_label[g]["tp"] += 1
            else:
                per_label[g]["fn"] += 1
                per_label[p]["fp"] += 1
    return exact, per_label, skipped_tokenization


def bootstrap_diff(exact_a, exact_b):
    rng = random.Random(20260813)
    n = len(exact_a)
    diffs = []
    for _ in range(BOOTSTRAP_N):
        idx = [rng.randrange(n) for _ in range(n)]
        diffs.append(
            (sum(exact_b[i] for i in idx) - sum(exact_a[i] for i in idx)) / n * 100
        )
    diffs.sort()
    return diffs[int(0.025 * BOOTSTRAP_N)], diffs[int(0.975 * BOOTSTRAP_N)]


def fmt_labels(per_label, cap=8):
    rows = []
    for label, c in sorted(per_label.items(), key=lambda kv: -(kv[1]["fn"] + kv[1]["fp"]))[:cap]:
        p = c["tp"] / (c["tp"] + c["fp"]) if c["tp"] + c["fp"] else 0
        r = c["tp"] / (c["tp"] + c["fn"]) if c["tp"] + c["fn"] else 0
        rows.append(f"| {label} | {p:.3f} | {r:.3f} | {c['tp'] + c['fn']} |")
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", default=None, help="path to a candidate .crfsuite")
    ap.add_argument(
        "--eval-bin",
        default=str(Path(bin_path("eval_tag"))),
    )
    args = ap.parse_args()

    clean = load_jsonl(CLEAN)
    gold_all = load_jsonl(GOLD)
    gold = [r for r in gold_all if r.get("status") == "adjudicated" and r.get("labels")]

    lines = ["# Accuracy Report", ""]
    verdicts = []

    for set_name, rows in (("clean", clean), ("gold-adjudicated", gold)):
        if not rows:
            lines.append(f"## {set_name}: no scoreable records yet")
            if set_name.startswith("gold"):
                lines.append(
                    f"({len(gold_all)} candidates exist; none adjudicated — gates pending human adjudication per protocol)"
                )
            lines.append("")
            continue
        base_preds = run_eval_tag(args.eval_bin, rows)
        base_exact, base_labels, base_skip = score(rows, base_preds)
        base_rate = sum(base_exact) / len(base_exact) * 100
        lines += [
            f"## {set_name} ({len(rows)} rows)",
            "",
            f"Original model exact match: **{base_rate:.2f}%** "
            f"({base_skip} tokenization-mismatch rows counted as miss)",
            "",
            "| Label (top by error volume) | Precision | Recall | Support |",
            "|---|---|---|---|",
            *fmt_labels(base_labels),
            "",
        ]
        if args.candidate:
            cand_preds = run_eval_tag(args.eval_bin, rows, model=args.candidate)
            cand_exact, _cl, _cs = score(rows, cand_preds)
            cand_rate = sum(cand_exact) / len(cand_exact) * 100
            lo, hi = bootstrap_diff(base_exact, cand_exact)
            diff = cand_rate - base_rate
            lines += [
                f"Candidate exact match: **{cand_rate:.2f}%** (diff {diff:+.2f}pp, 95% CI [{lo:+.2f}, {hi:+.2f}])",
                "",
            ]
            if set_name == "gold-adjudicated":
                ok = diff >= GOLD_MARGIN_PP and lo > 0
                verdicts.append(("gold gate (>= +3.0pp, CI>0)", ok))
            if set_name == "clean":
                ok = diff >= -CLEAN_REGRESSION_PP
                verdicts.append(("clean gate (>= -1.0pp)", ok))

    if args.candidate and verdicts:
        lines.append("## Pre-registered gates")
        for name, ok in verdicts:
            lines.append(f"- {name}: {'PASS' if ok else 'FAIL'}")
        lines.append("")

    RESULTS.mkdir(exist_ok=True)
    out = RESULTS / "accuracy_report.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[:30]))
    print(f"-> {out}")
    if args.candidate and verdicts and not all(ok for _n, ok in verdicts):
        sys.exit(1)


if __name__ == "__main__":
    main()
