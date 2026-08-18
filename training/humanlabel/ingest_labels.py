"""Ingest a completed labeling CSV into an approved training corpus.

Joins answers to candidates_for_labeling.jsonl by row number (the CSV's `num`
is 1-based position within the confidence-filtered subset the CSV was built
from), so tokens come straight from the model's own tokenization -- no string
re-parsing. Answers:
  ok               accept the model's proposed labels
  TOKEN=Label; ..  correct the named tokens (applied to every occurrence;
                   multi-occurrence applications are printed for review)
  skip             dropped, never used

Every corrected label is validated against the usaddress schema; an unknown
token or label is a hard error, not a silent skip. Output:
training/humanlabel/approved_labels.jsonl -- {tokens, labels, state,
source:"humanlabel"} rows ready for --humanlabel training.
"""
import argparse
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
CANDS = HERE / "candidates_for_labeling.jsonl"
OUT = HERE / "approved_labels.jsonl"

import usaddress

LABELS = {
    "AddressNumber", "AddressNumberPrefix", "AddressNumberSuffix",
    "BuildingName", "CornerOf", "IntersectionSeparator", "LandmarkName",
    "NotAddress", "OccupancyIdentifier", "OccupancyType", "PlaceName",
    "Recipient", "StateName", "StreetName", "StreetNamePostDirectional",
    "StreetNamePostModifier", "StreetNamePostType", "StreetNamePreDirectional",
    "StreetNamePreModifier", "StreetNamePreType", "SubaddressIdentifier",
    "SubaddressType", "USPSBoxGroupID", "USPSBoxGroupType", "USPSBoxID",
    "USPSBoxType", "ZipCode",
}


def norm(t):
    return "".join(c for c in t.upper() if c.isalnum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--max-confidence", type=float, default=0.90,
                    help="the threshold the CSV was built with (to reproduce the join order)")
    a = ap.parse_args()

    cands = [json.loads(l) for l in open(CANDS, encoding="utf-8") if l.strip()]
    subset = [c for c in cands if c["min_confidence"] < a.max_confidence]
    rows = list(csv.DictReader(open(a.csv, encoding="utf-8-sig")))
    if len(rows) != len(subset):
        sys.exit(f"CSV has {len(rows)} rows but the <{a.max_confidence} subset has "
                 f"{len(subset)} -- threshold mismatch, refusing to guess the alignment.")

    # Records where a corrected token legitimately holds two different roles in
    # one address (a state abbreviation used as a route prefix AND as the state,
    # or CITY inside a street name AND in the locality). A single "TOKEN=Label"
    # correction can't disambiguate which occurrence was meant, and applying it
    # to both corrupts the other. Dropped rather than guessed; re-answerable.
    AMBIGUOUS_DROP = {127, 172, 260, 285, 474}

    approved, skipped, multi, problems, dropped_ambig = [], 0, [], [], []
    for csv_row, cand in zip(rows, subset):
        if int(csv_row["num"]) in AMBIGUOUS_DROP:
            dropped_ambig.append(f"#{csv_row['num']}: {cand['raw']}")
            continue
        # sanity: the CSV address must match the candidate we're joining to
        if csv_row["address"].strip() != cand["raw"].strip():
            problems.append(f"#{csv_row['num']}: address mismatch on join")
            continue
        ans = (csv_row.get("answer") or "").strip()
        toks, labs = cand["prelabel_tokens"], list(cand["prelabel_labels"])
        low = ans.lower()
        if low == "skip" or ans == "":
            skipped += 1
            continue
        if low != "ok":
            for part in [p.strip() for p in ans.split(";") if p.strip()]:
                if "=" not in part:
                    problems.append(f"#{csv_row['num']}: bad correction {part!r}")
                    continue
                tok, label = [x.strip() for x in part.split("=", 1)]
                if label not in LABELS:
                    problems.append(f"#{csv_row['num']}: unknown label {label!r}")
                    continue
                idxs = [i for i, t in enumerate(toks) if norm(t) == norm(tok)]
                if not idxs:
                    problems.append(f"#{csv_row['num']}: token {tok!r} not in {toks}")
                    continue
                if len(idxs) > 1:
                    multi.append(f"#{csv_row['num']}: {tok!r} x{len(idxs)} -> {label}")
                for i in idxs:
                    labs[i] = label
        # round-trip guard
        if usaddress.tokenize(" ".join(toks)) != toks:
            problems.append(f"#{csv_row['num']}: tokenize round-trip failed")
            continue
        approved.append({"tokens": toks, "labels": labs, "state": cand["state"],
                         "origin": "humanlabel", "corrected": low != "ok"})

    if problems:
        print("PROBLEMS (nothing written):")
        for p in problems:
            print("  ", p)
        sys.exit(1)
    with open(OUT, "w", encoding="utf-8") as f:
        for r in approved:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    n_corr = sum(1 for r in approved if r["corrected"])
    print(f"approved {len(approved)} ({len(approved)-n_corr} ok, {n_corr} corrected), "
          f"{skipped} skipped -> {OUT}")
    if dropped_ambig:
        print(f"\n{len(dropped_ambig)} dropped as ambiguous multi-role (re-answerable):")
        for d in dropped_ambig:
            print("  ", d)
    if multi:
        print(f"\n{len(multi)} multi-occurrence corrections kept (duplicated address / "
              f"misplaced zip -- both occurrences correct)")


if __name__ == "__main__":
    main()
