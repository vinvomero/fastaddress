"""Ingest the batch-2 answered CSV into approved training rows.

Joins by normalized address to candidates_batch2.jsonl (robust to row order),
applies corrections with the gold-2c grammar, and handles the multi-occurrence
case with a positional-plausibility rule: a street-component label is applied
only to occurrences NOT in the last two tokens, a place/state/zip label only to
occurrences NOT in the first two. That resolves "NC HWY ... NC" (first NC is a
route prefix, trailing NC is the state) without a hand list. Any multi-role case
the rule cannot resolve cleanly is dropped and reported, never guessed.

Output: training/humanlabel/approved_labels2.jsonl.
Usage: python training/humanlabel/ingest_labels2.py --csv <path>
"""
import argparse
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
CANDS = HERE / "candidates_batch2.jsonl"
OUT = HERE / "approved_labels2.jsonl"
import usaddress

LABELS = {
    "AddressNumber", "AddressNumberPrefix", "AddressNumberSuffix", "BuildingName",
    "CornerOf", "IntersectionSeparator", "LandmarkName", "NotAddress",
    "OccupancyIdentifier", "OccupancyType", "PlaceName", "Recipient", "StateName",
    "StreetName", "StreetNamePostDirectional", "StreetNamePostModifier",
    "StreetNamePostType", "StreetNamePreDirectional", "StreetNamePreModifier",
    "StreetNamePreType", "SubaddressIdentifier", "SubaddressType", "USPSBoxGroupID",
    "USPSBoxGroupType", "USPSBoxID", "USPSBoxType", "ZipCode",
}
STREETISH = {"StreetName", "StreetNamePreType", "StreetNamePostType",
             "StreetNamePreDirectional", "StreetNamePostDirectional",
             "StreetNamePreModifier", "StreetNamePostModifier"}
TAILISH = {"StateName", "ZipCode", "PlaceName"}


def norm_tok(t):
    return "".join(c for c in t.upper() if c.isalnum())


def norm_id(s):
    return " ".join(norm_tok(t) for t in s.split())


ORDINAL = {"first": 1, "1st": 1, "second": 2, "2nd": 2, "2d": 2, "third": 3, "3rd": 3,
           "fourth": 4, "4th": 4}


def apply_correction(tokens, labels, tok, label, n_pos, multi, drop, num):
    # The reviewer disambiguated repeats inline as "first X" / "second X".
    parts = tok.split(None, 1)
    which = None
    if len(parts) == 2 and parts[0].lower() in ORDINAL:
        which = ORDINAL[parts[0].lower()]
        tok = parts[1]
    idxs = [i for i, t in enumerate(tokens) if norm_tok(t) == norm_tok(tok)]
    if not idxs:
        drop.append(f"#{num}: token {tok!r} not found in {' '.join(tokens)}")
        return False
    if which is not None:
        if which > len(idxs):
            drop.append(f"#{num}: asked for occurrence {which} of {tok!r} but only {len(idxs)}")
            return False
        idxs = [idxs[which - 1]]
    elif len(idxs) > 1:
        # No ordinal given. Keep occurrences where the label is positionally
        # plausible: a street label not in the last two tokens, a tail label not
        # in the first two. Legitimate duplicated addresses keep both; a state
        # abbrev used as route-prefix-and-state keeps only the prefix occurrence.
        if label in STREETISH:
            plausible = [i for i in idxs if i < n_pos - 2]
        elif label in TAILISH:
            plausible = [i for i in idxs if i >= 2]
        else:
            plausible = idxs
        if not plausible:
            drop.append(f"#{num}: {tok!r} x{len(idxs)} -> {label}, no plausible position: "
                        f"{' '.join(tokens)}")
            return False
        if len(plausible) > 1:
            multi.append(f"#{num}: {tok!r} x{len(plausible)} -> {label}")
        idxs = plausible
    for i in idxs:
        labels[i] = label
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args()

    cand = {norm_id(json.loads(l)["raw"]): json.loads(l)
            for l in open(CANDS, encoding="utf-8") if l.strip()}
    rows = list(csv.DictReader(open(a.csv, encoding="utf-8-sig")))

    approved, skipped, multi, drop = [], 0, [], []
    for r in rows:
        ans = (r.get("answer") or "").strip()
        if not ans or ans.lower() == "skip":
            skipped += 1
            continue
        c = cand.get(norm_id(r["address"]))
        if not c:
            drop.append(f"#{r['num']}: no candidate match for {r['address'][:50]!r}")
            continue
        toks, labs = c["prelabel_tokens"], list(c["prelabel_labels"])
        ok = True
        if ans.lower() != "ok":
            for part in [p.strip() for p in ans.split(";") if p.strip()]:
                if "=" not in part:
                    drop.append(f"#{r['num']}: bad correction {part!r}")
                    ok = False
                    continue
                tk, lb = [x.strip() for x in part.split("=", 1)]
                if lb not in LABELS:
                    drop.append(f"#{r['num']}: unknown label {lb!r}")
                    ok = False
                    continue
                if not apply_correction(toks, labs, tk, lb, len(toks), multi, drop, r["num"]):
                    ok = False
        if not ok:
            continue
        if usaddress.tokenize(" ".join(toks)) != toks:
            drop.append(f"#{r['num']}: tokenize round-trip failed")
            continue
        approved.append({"tokens": toks, "labels": labs, "state": c["state"],
                         "target_class": c["target_class"], "origin": "humanlabel2",
                         "corrected": ans.lower() != "ok"})

    n_corr = sum(1 for x in approved if x["corrected"])
    print(f"approved {len(approved)} ({len(approved)-n_corr} ok, {n_corr} corrected), "
          f"{skipped} skipped, {len(drop)} dropped")
    import collections
    bycls = collections.Counter(x["target_class"] for x in approved)
    print("by class:", dict(bycls))
    if drop:
        print(f"\ndropped ({len(drop)}):")
        for d in drop[:60]:
            print("  ", d)
    if a.verify:
        return
    with open(OUT, "w", encoding="utf-8") as f:
        for x in approved:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
