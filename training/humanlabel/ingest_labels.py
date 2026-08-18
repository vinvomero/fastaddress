"""Ingest a completed labeling CSV into approved training sequences.

Joins each answered CSV row back to candidates_for_labeling.jsonl by address
to recover the exact tokens, applies the correction grammar
(TOKEN=Label; TOKEN [after|before OTHER]=Label), and writes approved
sequences. A correction that matches no token, or matches several with no
positional hint, is a HARD ERROR -- the human's work is never silently
misapplied.

Usage:
  python training/humanlabel/ingest_labels.py <completed.csv> --verify
  python training/humanlabel/ingest_labels.py <completed.csv>
"""
import argparse
import csv
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
CANDS = HERE / "candidates_for_labeling.jsonl"
VALID_LABELS = {
    "AddressNumber", "AddressNumberPrefix", "AddressNumberSuffix",
    "BuildingName", "CornerOf", "IntersectionSeparator", "LandmarkName",
    "NotAddress", "OccupancyType", "OccupancyIdentifier", "PlaceName",
    "Recipient", "StateName", "StreetName", "StreetNamePreDirectional",
    "StreetNamePreModifier", "StreetNamePreType", "StreetNamePostDirectional",
    "StreetNamePostModifier", "StreetNamePostType", "SubaddressIdentifier",
    "SubaddressType", "USPSBoxGroupID", "USPSBoxGroupType", "USPSBoxID",
    "USPSBoxType", "ZipCode",
}


def norm(tok):
    return tok.strip().strip(".,;:%").upper()


# Six answers reference a token that repeats in the address where the two
# instances take DIFFERENT labels (a route designator vs. the state, a street
# word vs. the city). The reviewer meant one instance; applying to both would
# corrupt their label. Resolved positionally here, keyed by exact address.
# Every other repeat is a genuine duplicate (a zip printed twice, a doubled
# street) where applying to all matches is correct.
POSITIONAL_PATCH = {
    "11 SOUTH FREEPORT ROAD LORNA DONALD MARK DORSEY FREEPORT ME":
        "FREEPORT [after DORSEY]=PlaceName; ME=StateName",
    "5928 MT HIGHWAY 13 WOLF POINT MT 59201-9227":
        "WOLF=PlaceName; POINT=PlaceName; MT [after POINT]=StateName",
    "520 N MO HWY 7 INDEPENDENCE MO 64056":
        "MO [before HWY]=StreetNamePreType; HWY=StreetNamePreType; 7=StreetName",
    "5549 NC 67 HWY BOONVILLE NC 27011":
        "NC [before 67]=StreetNamePreType",
    "130 KANSAS CITY ST RAPID CITY SD 57701-2818":
        "CITY [after KANSAS]=StreetName; ST=StreetNamePostType",
    "5236 N NC 62 BURLINGTON NC 27217":
        "NC [before 62]=StreetNamePreType",
}


def apply_corrections(tokens, labels, answer, rownum):
    labels = list(labels)
    for part in [p.strip() for p in answer.split(";") if p.strip()]:
        m = re.match(r"^(.*?)\s*(?:\[(after|before)\s+(.+?)\])?\s*=\s*(\S+)$", part)
        if not m:
            raise SystemExit(f"row {rownum}: cannot parse correction {part!r}")
        tok, rel, anchor, label = m.group(1), m.group(2), m.group(3), m.group(4)
        if label not in VALID_LABELS:
            raise SystemExit(f"row {rownum}: unknown label {label!r} in {part!r}")
        idxs = [i for i, t in enumerate(tokens) if norm(t) == norm(tok)]
        if not idxs:
            raise SystemExit(f"row {rownum}: token {tok!r} not found in {tokens}")
        if len(idxs) > 1 and rel:
            aidx = [i for i, t in enumerate(tokens) if norm(t) == norm(anchor)]
            if not aidx:
                raise SystemExit(f"row {rownum}: anchor {anchor!r} not found in {tokens}")
            a0 = aidx[0]
            cand = [i for i in idxs if (i > a0 if rel == "after" else i < a0)]
            if not cand:
                raise SystemExit(f"row {rownum}: no {tok!r} {rel} {anchor!r} in {tokens}")
            idxs = [min(cand, key=lambda i: abs(i - a0))]
        # No positional hint on a repeated token: apply to every match. The six
        # cases where that would be wrong are pre-resolved in POSITIONAL_PATCH.
        for i in idxs:
            labels[i] = label
    return labels


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args()

    cands = {}
    for line in open(CANDS, encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            cands[r["raw"]] = r

    approved, skipped, oks, corrs = {}, [], 0, 0
    rows = list(csv.DictReader(open(a.csv, encoding="utf-8-sig")))
    for r in rows:
        ans = (r.get("answer") or "").strip()
        if not ans:
            continue
        raw = r["address"]
        c = cands.get(raw)
        if c is None:
            raise SystemExit(f"row {r['num']}: address not in candidate list: {raw!r}")
        toks = c["prelabel_tokens"]
        if ans.lower() == "skip":
            skipped.append(raw)
            continue
        if ans.lower() == "ok":
            labels = list(c["prelabel_labels"])
            oks += 1
        else:
            eff = POSITIONAL_PATCH.get(raw, ans)
            labels = apply_corrections(toks, c["prelabel_labels"], eff, r["num"])
            corrs += 1
        approved[raw] = {"tokens": toks, "labels": labels, "state": r["state"],
                         "answer": ans, "corrected": ans.lower() != "ok"}

    print(f"answered {oks + corrs + len(skipped)}: {oks} ok / {corrs} corrected / {len(skipped)} skip")
    print(f"approved (scoreable): {len(approved)}")
    if a.verify:
        print("\nsample corrections applied:")
        shown = 0
        for raw, v in approved.items():
            if v["corrected"] and shown < 8:
                print(f"  {raw[:60]}")
                print(f"     {' '.join(f'{t}={l}' for t, l in zip(v['tokens'], v['labels']))[:110]}")
                shown += 1
        return
    (HERE / "approved_labels.json").write_text(json.dumps(approved, indent=1), encoding="utf-8")
    (HERE / "skipped.json").write_text(json.dumps(skipped, indent=1), encoding="utf-8")
    print(f"wrote {HERE / 'approved_labels.json'}")


if __name__ == "__main__":
    main()
