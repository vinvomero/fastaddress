"""Generate the U1 model-loading fixture from Python usaddress (the parity oracle).

Emits fixture.json with, for one address: the tokens, the CRFsuite attribute
name/weight pairs exactly as python-crfsuite's ItemSequence serializes usaddress's
feature dicts, and the labels usaddress assigns. The Rust test replays the
attributes through the vendored model and must reproduce the labels.
"""

import json
from importlib.metadata import version
from pathlib import Path

import pycrfsuite
import usaddress

ADDRESS = "123 N Main St Apt 4B Springfield IL 62704"


def main():
    tokens = usaddress.tokenize(ADDRESS)
    features = usaddress.tokens2features(tokens)
    items = pycrfsuite.ItemSequence(features).items()  # list[dict[str, float]]
    parsed = usaddress.parse(ADDRESS)  # list[(token, label)]
    fixture = {
        "address": ADDRESS,
        "usaddress_version": version("usaddress"),
        "tokens": tokens,
        "attrs": [sorted(item.items()) for item in items],
        "labels": [label for _tok, label in parsed],
    }
    out = Path(__file__).parent / "fixture.json"
    out.write_text(json.dumps(fixture, indent=1), encoding="utf-8")
    print(f"wrote {out} ({len(tokens)} tokens)")


if __name__ == "__main__":
    main()
