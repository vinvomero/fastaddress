"""Convention check for synthetic training data.

Round 3 shipped synthetic labels that contradicted the gold convention ('#'
labeled as a type rather than part of the identifier; route qualifiers labeled
as post-types) and measurably degraded the model. This asserts the conventions
that failure taught us, so the mistake cannot silently recur.

Usage: python training/validate_synth.py  (exit 1 on violation)
"""

import json
import sys
from pathlib import Path

SYNTH = Path(__file__).parent / "corpus" / "synth.jsonl"

ID_LABELS = {"USPSBoxID", "OccupancyIdentifier", "AddressNumber"}


def main():
    rows = [json.loads(l) for l in open(SYNTH, encoding="utf-8") if l.strip()]
    violations = []
    for r in rows:
        for tok, lab in zip(r["tokens"], r["labels"]):
            # '#' is part of the identifier it precedes, never a type label.
            if tok == "#" and lab not in ID_LABELS:
                violations.append((r["tokens"], tok, lab, "'#' must carry an identifier label"))
            if tok.lower() in ("business", "bypass", "alt") and lab != "StreetName":
                violations.append((r["tokens"], tok, lab, "route qualifier must be StreetName"))
    if violations:
        for toks, tok, lab, why in violations[:10]:
            print(f"VIOLATION: {' '.join(toks)[:60]} | {tok!r} -> {lab} ({why})")
        print(f"{len(violations)} convention violations")
        sys.exit(1)
    print(f"{len(rows)} synthetic sequences: conventions OK")


if __name__ == "__main__":
    main()
