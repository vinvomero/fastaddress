"""Differential parity runner: compares the Rust dump binary's output against
the Python oracle at three layers (tokens, serialized attributes, labels) for
every dataset in benchmark/data/. Writes benchmark/results/parity_report.md.

Exit code 1 if any divergence is found (CI gate: zero unexplained divergences).

Usage: python benchmark/run_parity.py [--dump-bin PATH]
"""

import argparse
import os
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
from binpath import bin_path
import json
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA_DIR = Path(__file__).parent / "data"
ORACLE_DIR = Path(__file__).parent / "oracle"
RESULTS_DIR = Path(__file__).parent / "results"
EXAMPLE_CAP = 5


def compare_row(oracle, rust):
    """Return (layer, detail) for the first divergent layer, or None."""
    if oracle["tokens"] != rust["tokens"]:
        return ("tokens", {"oracle": oracle["tokens"], "rust": rust["tokens"]})
    o_attrs = [[(n, float(w)) for n, w in tok] for tok in oracle["attrs"]]
    r_attrs = [[(n, float(w)) for n, w in tok] for tok in rust["attrs"]]
    if o_attrs != r_attrs:
        for i, (o_tok, r_tok) in enumerate(zip(o_attrs, r_attrs)):
            if o_tok != r_tok:
                only_o = sorted(set(map(tuple, o_tok)) - set(map(tuple, r_tok)))
                only_r = sorted(set(map(tuple, r_tok)) - set(map(tuple, o_tok)))
                return ("attrs", {"token_index": i, "oracle_only": only_o, "rust_only": only_r})
        return ("attrs", {"detail": "length mismatch"})
    if oracle["labels"] != rust["labels"]:
        return ("labels", {"oracle": oracle["labels"], "rust": rust["labels"]})
    if oracle["tag_error"] != rust.get("tag_error"):
        return ("tag", {"oracle_error": oracle["tag_error"], "rust_error": rust.get("tag_error")})
    if oracle["tag"] is not None:
        o_pairs = [[k, v] for k, v in oracle["tag"][0].items()]
        o_norm = [o_pairs, oracle["tag"][1]]
        if o_norm != rust.get("tag"):
            return ("tag", {"oracle": o_norm, "rust": rust.get("tag")})
    return None


def run_dataset(name, dump_bin):
    oracle_path = ORACLE_DIR / f"{name}.jsonl"
    csv_path = DATA_DIR / f"{name}.csv"
    proc = subprocess.run(
        [dump_bin, str(csv_path)], capture_output=True, text=True, encoding="utf-8", check=True
    )
    rust_rows = [json.loads(line) for line in proc.stdout.splitlines() if line.strip()]
    with open(oracle_path, encoding="utf-8") as f:
        oracle_rows = [json.loads(line) for line in f]
    assert len(rust_rows) == len(oracle_rows), f"{name}: row count mismatch"

    stats = {"n": len(oracle_rows), "tokens": 0, "attrs": 0, "labels": 0, "tag": 0}
    examples = []
    for oracle, rust in zip(oracle_rows, rust_rows):
        div = compare_row(oracle, rust)
        if div:
            layer, detail = div
            stats[layer] += 1
            if len(examples) < EXAMPLE_CAP:
                examples.append({"raw": oracle["raw"], "layer": layer, "detail": detail})
    return stats, examples


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dump-bin", default=bin_path("dump"))
    args = parser.parse_args()

    RESULTS_DIR.mkdir(exist_ok=True)
    all_stats = {}
    all_examples = {}
    total_div = 0
    for csv_path in sorted(DATA_DIR.glob("*.csv")):
        name = csv_path.stem
        if not (ORACLE_DIR / f"{name}.jsonl").exists():
            sys.exit(f"missing oracle for {name} — run benchmark/dump_oracle.py first")
        stats, examples = run_dataset(name, args.dump_bin)
        all_stats[name] = stats
        all_examples[name] = examples
        div = stats["tokens"] + stats["attrs"] + stats["labels"] + stats["tag"]
        total_div += div
        print(
            f"{name:10s} n={stats['n']}  token_div={stats['tokens']}  "
            f"attr_div={stats['attrs']}  label_div={stats['labels']}  tag_div={stats['tag']}"
        )

    lines = [
        "# Parity Report — Rust engine vs usaddress " + version("usaddress"),
        "",
        "| Dataset | Rows | Token divs | Attr divs | Label divs | Tag divs |",
        "|---|---|---|---|---|---|",
    ]
    for name, s in all_stats.items():
        lines.append(
            f"| {name} | {s['n']} | {s['tokens']} | {s['attrs']} | {s['labels']} | {s['tag']} |"
        )
    lines.append("")
    if total_div:
        lines.append("## Divergence examples")
        for name, examples in all_examples.items():
            for ex in examples:
                lines.append(f"- `{name}` [{ex['layer']}] `{ex['raw']}`: {json.dumps(ex['detail'])[:400]}")
    else:
        lines.append("Zero divergences across all datasets and layers.")
    (RESULTS_DIR / "parity_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"-> {RESULTS_DIR / 'parity_report.md'}")
    sys.exit(1 if total_div else 0)


if __name__ == "__main__":
    main()
