"""Convention check for the TIGER-derived corpus.

Same role validate_synth.py plays for synthetic data: assert the conventions
we verified against upstream's labeled.xml, so a future edit to the mapping
cannot silently reintroduce a label style the model was never trained on.

Each rule cites the upstream evidence that justifies it.

Usage: python training/validate_tiger.py  (exit 1 on violation)
"""

import json
import sys
from collections import Counter
from pathlib import Path

import usaddress

from build_tiger_corpus import ROUTE_DESIGNATORS

TIGER = Path(__file__).parent / "corpus" / "tiger.jsonl"
VALID_LABELS = set(usaddress.LABELS)


def check(row):
    """Return a list of violation strings for one row."""
    toks, labs = row["tokens"], row["labels"]
    bad = []

    for t, l in zip(toks, labs):
        if l not in VALID_LABELS:
            bad.append(f"{l!r} is not a model label (token {t!r})")

    # Upstream: "OLD US HIGHWAY 90" -> Old=PreModifier only because US/HIGHWAY
    # are PreTypes. "Old Peachtree Road" -> Old=StreetName. A PreModifier with
    # no PreType in the row means the conditional mapping regressed.
    if "StreetNamePreModifier" in labs and "StreetNamePreType" not in labs:
        bad.append("StreetNamePreModifier without a StreetNamePreType")

    # Upstream splits numbered route designations (207 StreetNamePreType labels
    # in labeled.xml). A designator word leading the StreetName run and
    # followed by a bare number means apply_route_pretype() did not fire.
    idx = [i for i, l in enumerate(labs) if l == "StreetName"]
    if len(idx) >= 2:
        first = toks[idx[0]].lower().strip(".-,")
        second = toks[idx[1]].lstrip("#").rstrip(",")
        if first in ROUTE_DESIGNATORS and second.isdigit():
            bad.append(f"unsplit route designation: {toks[idx[0]]!r} {toks[idx[1]]!r}")

    # Structural: every emitted address is composed number-first, and a street
    # phrase without a StreetName is not a street phrase.
    if labs[0] != "AddressNumber":
        bad.append(f"row does not begin with AddressNumber (got {labs[0]})")
    if "StreetName" not in labs:
        bad.append("no StreetName in row")

    return bad


def main():
    if not TIGER.exists():
        print(f"{TIGER} not found -- run build_tiger_corpus.py first")
        sys.exit(1)

    rows = [json.loads(l) for l in open(TIGER, encoding="utf-8") if l.strip()]
    violations = []
    for r in rows:
        for v in check(r):
            violations.append((" ".join(r["tokens"]), v))

    if violations:
        kinds = Counter(v for _, v in violations)
        for raw, v in violations[:10]:
            print(f"VIOLATION: {raw[:60]} | {v}")
        print(f"\n{len(violations)} violations across {len(rows)} rows")
        for k, n in kinds.most_common(8):
            print(f"  {n:6}  {k}")
        sys.exit(1)

    labels = Counter(l for r in rows for l in r["labels"])
    print(f"{len(rows)} TIGER sequences: conventions OK")
    print("label coverage:")
    for l, n in labels.most_common():
        print(f"  {l:28} {n:7}")


if __name__ == "__main__":
    main()
