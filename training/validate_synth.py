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

# The model's label set. "Second*" variants are NOT model labels — usaddress
# adds that prefix during tag() grouping — so emitting them in training data
# silently teaches a label the model can never usefully predict.
VALID_LABELS = set(__import__("usaddress").LABELS)


def main():
    rows = [json.loads(l) for l in open(SYNTH, encoding="utf-8") if l.strip()]
    violations = []
    for r in rows:
        labels = set(r["labels"])
        # The route-qualifier rule is scoped to highway/street contexts. The same
        # words are legitimate landmark tokens ("West Business Center"), so a
        # sequence labeled entirely as a landmark phrase is exempt.
        is_landmark_phrase = "LandmarkName" in labels
        # Route-designation exception, from the adjudicated parse of
        # "Alvy Prk And Hghwy # 54": after an intersection separator, the '#'
        # in a highway designation is part of the street name, not an
        # identifier. Scoped to that context so the general rule still holds.
        is_route_designation = "IntersectionSeparator" in labels
        for tok, lab in zip(r["tokens"], r["labels"]):
            if lab not in VALID_LABELS:
                violations.append((r["tokens"], tok, lab, "not a model label"))
            # '#' is part of the identifier it precedes, never a type label.
            if tok == "#" and lab not in ID_LABELS and not (is_route_designation and lab == "StreetName"):
                violations.append((r["tokens"], tok, lab, "'#' must carry an identifier label"))
            if (
                tok.lower() in ("business", "bypass", "alt")
                and lab != "StreetName"
                and not (is_landmark_phrase and lab == "LandmarkName")
            ):
                violations.append(
                    (r["tokens"], tok, lab, "route qualifier must be StreetName outside landmark phrases")
                )
    if violations:
        for toks, tok, lab, why in violations[:10]:
            print(f"VIOLATION: {' '.join(toks)[:60]} | {tok!r} -> {lab} ({why})")
        print(f"{len(violations)} convention violations")
        sys.exit(1)
    print(f"{len(rows)} synthetic sequences: conventions OK")


if __name__ == "__main__":
    main()
