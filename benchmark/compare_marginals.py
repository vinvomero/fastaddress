"""Ground-truth cross-check for the Rust confidence path.

Runs the SAME model (model/usaddr.crfsuite) over the SAME addresses in
pycrfsuite and in our Rust implementation, and reports the maximum absolute
difference in per-position marginal probabilities and in sequence
probabilities.

pycrfsuite's Tagger exposes `.marginal(label, position)` and
`.probability(labels)`; those are the reference values here. Features come from
usaddress's own `tokenize` + `tokens2features` on the Python side and from our
feature extractor on the Rust side, so a feature-extraction divergence would
also show up as a marginal divergence.

Usage:
  cargo build --release -j 1                 (with CARGO_TARGET_DIR set)
  python benchmark/compare_marginals.py --rows 2000
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

import pycrfsuite
import usaddress

ROOT = Path(__file__).parent.parent
MODEL = ROOT / "model" / "usaddr.crfsuite"
DUMP_BIN = "C:/cargo-target/us-address-parser/release/dump_marginals.exe"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=str(ROOT / "benchmark" / "data" / "cook.csv"))
    ap.add_argument("--rows", type=int, default=2000)
    ap.add_argument("--bin", default=DUMP_BIN)
    args = ap.parse_args()

    proc = subprocess.run(
        [args.bin, args.csv, str(args.rows)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    rust = [json.loads(line) for line in proc.stdout.splitlines() if line.strip()]
    print(f"rust rows: {len(rust)}")

    tagger = pycrfsuite.Tagger()
    tagger.open(str(MODEL))
    py_labels = list(tagger.labels())

    max_marginal_diff = 0.0
    max_marginal_at = None
    max_seq_diff = 0.0
    max_seq_at = None
    token_mismatch = 0
    label_mismatch = 0
    positions = 0

    for row in rust:
        raw = row["raw"]
        tokens = usaddress.tokenize(raw)
        if list(tokens) != list(row["tokens"]):
            token_mismatch += 1
            continue
        features = usaddress.tokens2features(tokens)
        tagger.set(features)
        tags = tagger.tag()
        if list(tags) != list(row["labels"]):
            label_mismatch += 1

        names = row["label_names"]
        for t in range(len(tokens)):
            positions += 1
            for j, name in enumerate(names):
                ref = tagger.marginal(name, t)
                got = row["marginals"][t][j]
                d = abs(ref - got)
                if d > max_marginal_diff:
                    max_marginal_diff = d
                    max_marginal_at = (raw, t, name, ref, got)

        ref_p = tagger.probability(list(row["labels"]))
        d = abs(ref_p - row["sequence_probability"])
        if d > max_seq_diff:
            max_seq_diff = d
            max_seq_at = (raw, ref_p, row["sequence_probability"])

    print(f"positions compared: {positions}")
    print(f"tokenizer mismatches (rows skipped): {token_mismatch}")
    print(f"viterbi label mismatches (rows): {label_mismatch}")
    print(f"max |marginal_rust - marginal_pycrfsuite| = {max_marginal_diff:.3e}")
    if max_marginal_at:
        raw, t, name, ref, got = max_marginal_at
        print(f"  worst at {raw!r} pos {t} label {name}: py={ref!r} rust={got!r}")
    print(f"max |seq_prob_rust - seq_prob_pycrfsuite| = {max_seq_diff:.3e}")
    if max_seq_at:
        raw, ref, got = max_seq_at
        print(f"  worst at {raw!r}: py={ref!r} rust={got!r}")

    ok = max_marginal_diff < 1e-9 and max_seq_diff < 1e-9 and token_mismatch == 0
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
