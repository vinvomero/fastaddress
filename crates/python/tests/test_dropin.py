"""Drop-in verification: the fastaddress binding must match usaddress on a corpus
sample, the crash class, empty input, and tag_mapping — driven through Python.

Run after installing the built wheel: python crates/python/tests/test_dropin.py
"""

import csv
import random
import sys
import time
from pathlib import Path

t0 = time.perf_counter()
import fastaddress  # noqa: E402

IMPORT_SECS = time.perf_counter() - t0

import fastaddressess  # noqa: E402

DATA_DIR = Path(__file__).parents[3] / "benchmark" / "data"
SAMPLE_PER_FILE = 250


def check(cond, msg):
    if not cond:
        sys.exit(f"FAIL: {msg}")


def main():
    rng = random.Random(20260809)
    rows = []
    for csv_path in sorted(DATA_DIR.glob("*.csv")):
        with open(csv_path, newline="", encoding="utf-8") as f:
            all_rows = [r["raw_address"] for r in csv.DictReader(f)]
        rows += rng.sample(all_rows, min(SAMPLE_PER_FILE, len(all_rows)))

    mismatches = 0
    for raw in rows:
        check(fastaddress.parse(raw) == usaddress.parse(raw), f"parse mismatch: {raw!r}")
        try:
            expected = usaddress.tag(raw)
            expected_err = None
        except usaddress.RepeatedLabelError:
            expected, expected_err = None, True
        try:
            got = fastaddress.tag(raw)
            got_err = None
        except fastaddress.RepeatedLabelError:
            got, got_err = None, True
        if expected_err != got_err or (expected is not None and (dict(expected[0]), expected[1]) != (dict(got[0]), got[1])):
            mismatches += 1
            print(f"tag mismatch: {raw!r}\n  py: {expected} err={expected_err}\n  rs: {got} err={got_err}")
    check(mismatches == 0, f"{mismatches} tag mismatches")

    # Ordered-dict order preserved
    tagged, kind = fastaddress.tag("123 N Main St Springfield IL 62704")
    check(list(tagged.keys())[0] == "AddressNumber", "component order not preserved")
    check(kind == "Street Address", "address_type wrong")

    # Crash-class behavior
    try:
        fastaddress.tag("59 ST JAMES PLACE NEW YORK NY 10038")
        sys.exit("FAIL: expected RepeatedLabelError")
    except fastaddress.RepeatedLabelError:
        pass
    tagged, _ = fastaddress.tag_native("59 ST JAMES PLACE NEW YORK NY 10038")
    check(len(tagged) > 0, "native mode returned nothing on crash-class input")

    # Empty / whitespace
    check(fastaddress.tag("") == ({}, "Ambiguous"), "empty input mismatch")
    check(fastaddress.tag("   ") == ({}, "Ambiguous"), "whitespace input mismatch")

    # tag_mapping parity
    mapping = {"AddressNumber": "HouseNumber"}
    check(
        dict(fastaddress.tag("123 Main St", tag_mapping=mapping)[0])
        == dict(usaddress.tag("123 Main St", tag_mapping=mapping)[0]),
        "tag_mapping mismatch",
    )

    # Confidence API: additive, and never changes what the plain calls return.
    for raw in rows[:300]:
        triples = fastaddress.parse_with_confidence(raw)
        check(
            [(t, l) for t, l, _c in triples] == fastaddress.parse(raw),
            f"parse_with_confidence changed parse output: {raw!r}",
        )
        check(
            all(0.0 <= c <= 1.0 for _t, _l, c in triples),
            f"confidence outside [0,1]: {raw!r}",
        )
        tagged, kind, conf, seq = fastaddress.tag_native_with_confidence(raw)
        plain_tagged, plain_kind = fastaddress.tag_native(raw)
        check(tagged == plain_tagged, f"tag_native_with_confidence changed output: {raw!r}")
        check(kind == plain_kind, f"address_type changed: {raw!r}")
        check(set(conf) == set(tagged), f"confidence keys misaligned: {raw!r}")
        check(0.0 <= seq <= 1.0, f"sequence confidence outside [0,1]: {raw!r}")
        check(
            all(seq <= c + 1e-9 for c in conf.values()),
            f"sequence confidence exceeds a component marginal: {raw!r}",
        )

    # Confidence path honors the RepeatedLabelError contract too.
    try:
        fastaddress.tag_with_confidence("59 ST JAMES PLACE NEW YORK NY 10038")
        sys.exit("FAIL: expected RepeatedLabelError from tag_with_confidence")
    except fastaddress.RepeatedLabelError:
        pass

    print(f"OK: {len(rows)} sampled rows drop-in identical; import time {IMPORT_SECS*1000:.0f}ms")


if __name__ == "__main__":
    main()
