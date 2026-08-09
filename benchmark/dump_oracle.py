"""Oracle dumper: for every raw_address in benchmark/data/*.csv, emit the Python
usaddress ground truth as JSONL — tokens, ItemSequence-serialized attributes,
and labels (or the RepeatedLabelError signal). Consumed by run_parity.py.

Requires the pinned versions in benchmark/requirements.txt.
"""

import csv
import json
import sys
from importlib.metadata import version
from pathlib import Path

import pycrfsuite
import usaddress

DATA_DIR = Path(__file__).parent / "data"
ORACLE_DIR = Path(__file__).parent / "oracle"

PINNED = "0.5.16"


def dump_file(csv_path: Path, out_path: Path):
    n = 0
    with open(csv_path, newline="", encoding="utf-8") as f, open(
        out_path, "w", encoding="utf-8"
    ) as out:
        for row in csv.DictReader(f):
            raw = row["raw_address"]
            tokens = usaddress.tokenize(raw)
            if tokens:
                features = usaddress.tokens2features(tokens)
                items = pycrfsuite.ItemSequence(features).items()
                attrs = [sorted(item.items()) for item in items]
                labels = [label for _t, label in usaddress.parse(raw)]
            else:
                attrs, labels = [], []
            try:
                tag_result = list(usaddress.tag(raw))
                tag_error = None
            except usaddress.RepeatedLabelError:
                tag_result = None
                tag_error = "RepeatedLabelError"
            out.write(
                json.dumps(
                    {
                        "raw": raw,
                        "tokens": tokens,
                        "attrs": attrs,
                        "labels": labels,
                        "tag": tag_result,
                        "tag_error": tag_error,
                    }
                )
                + "\n"
            )
            n += 1
    print(f"{csv_path.stem}: {n} rows -> {out_path}")


def main():
    installed = version("usaddress")
    if installed != PINNED:
        sys.exit(f"oracle requires usaddress=={PINNED}, found {installed}")
    ORACLE_DIR.mkdir(exist_ok=True)
    for csv_path in sorted(DATA_DIR.glob("*.csv")):
        dump_file(csv_path, ORACLE_DIR / f"{csv_path.stem}.jsonl")


if __name__ == "__main__":
    main()
