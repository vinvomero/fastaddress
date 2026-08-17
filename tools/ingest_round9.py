"""Ingest Round-9 human verdicts (gold-2b scoring attempt 1, candidate v50).

Rebuilds the 136-record disagreement worklist deterministically (same tag and
compare logic, same record order as make_gold2b_review_doc.py), un-blinds via
the committed round-9 key, and stores each verdict with the approved label
sequence so a third reading is impossible.

Usage: python tools/ingest_round9.py [--verify]
"""

import argparse
import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "benchmark"))
from binpath import bin_path  # noqa: E402

G2B = ROOT / "eval" / "gold2b"
CANDIDATE = "model/candidates/v50.crfsuite"

LETTERS = (
    "B B B B B A A A A A "     # 1-10
    "B n A B B n n A A A "     # 11-20
    "A A A n n n n A n n "     # 21-30
    "n A B n n n n n A B "     # 31-40
    "A B B B B B A B A A "     # 41-50
    "A A A B A A n B A A "     # 51-60
    "A A A A A B n B B n "     # 61-70
    "B B B A A B B n A n "     # 71-80
    "B B B A B n n n A A "     # 81-90
    "B A n n B A A n B B "     # 91-100
    "A A B n A B B A A n "     # 101-110
    "B A A B A n B A B A "     # 111-120
    "A B B B B A A A n n "     # 121-130
    "B n n A B n"              # 131-136
).split()

# Notes the reviewer attached to specific records, kept with the verdict.
NOTES = {
    1: "Grayson Grove Dr in public records; source omitted Dr, so GROVE stays StreetName",
    5: "440 Merry Way, Pike Road AL: WAY is the suffix, PIKE ROAD the locality",
    7: "Arkansas roads such as Hempstead 314: the number is roadway name, not a unit",
    13: "One Capitol Mall is conventional; ONE is the address number",
    15: "#1 Capitol Mall is the same structure rendered differently",
    20: "Lower Broadview Rd; record dropped Rd, BROADVIEW stays StreetName",
    22: "Smyrna records 27 S Market Street Plz: ST is name material, PLZ the terminal type",
    40: "5828 Pinto Place, Rancho Cucamonga: PLACE is the type, RANCH begins the locality",
    43: "4109 Quail Hollow St, Evansville: HOLLOW is name, missing St is the suffix",
    45: "Southern Star is the street name (fuller Southern Star St exists)",
    46: "Rue/Camino functioning as a street-name pretype",
    57: "RUE is the pretype and ST begins St Louis; the models split the two facts",
    66: "Stablewood Circle, Pass Christian: CIRCLE the suffix, PASS CHRISTIA[N] the locality",
    71: "Belews Creek Rd; source omitted Rd, leaving CREEK as StreetName",
    72: "2705 E Ave F is the Bismarck form: E directional, Ave pretype, F street name",
    102: "Ledgewood Commons is the recorded form; Commons/Cmns is the terminal type",
    104: "870 Heritage Hills is the address name, but UNIT is also an occupancy marker",
    106: "52 East St, Nunda: East is StreetName, St the suffix",
    108: "6517 Clay Ct W, Canal Winchester: W is a street post-directional",
    115: "372 Park Ct N, La Vergne: N is on the street, not the locality",
    116: "Plaza on the Lake belongs together as street-name material",
    117: "5103 Village Crest Dr; CREST is name material, source dropped Dr",
    119: "Azure Oak is a complete street name; terminal nouns are not automatically suffixes",
    131: "19731 County Hwy Z, Richland Center: RICHLAND begins the locality",
    132: "Oak Drive Addition: ADN means Addition, neither directional nor a separate PlaceName",
    135: "Coal River Mountain Rd: MTN is name material, RD the suffix",
}
# Blocks the reviewer called out as systematic rather than per-record.
BLOCK_NOTES = {
    **{i: "Canadian postal-code string; neither parser labels the components correctly"
       for i in range(24, 39)},
    **{i: "Camino pretype + Dos Vidas street name + Las Cruces locality; no offered parse "
          "captures all three boundaries" for i in (80, 86, 88)},
}


def tag(raws, model=None):
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8", newline="") as tf:
        w = csv.writer(tf)
        w.writerow(["raw_address"])
        for r in raws:
            w.writerow([r])
        tmp = tf.name
    cmd = [bin_path("eval_tag"), tmp] + (["--model", model] if model else [])
    out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=True)
    return [json.loads(l) for l in out.stdout.splitlines() if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true", help="print mapping, write nothing")
    args = ap.parse_args()

    key = json.loads((G2B / "blind_key_r9.json").read_text(encoding="utf-8"))
    cohorts = json.loads((G2B / "COHORTS.json").read_text(encoding="utf-8"))
    strict = set(cohorts["strict"])
    lineage = set(cohorts["lineage_sensitivity"])
    aggregate = set(cohorts["aggregate_sensitivity"])

    def cohort_of(st):
        return ("strict" if st in strict else
                "lineage-sensitivity" if st in lineage else
                "aggregate-sensitivity" if st in aggregate else "?")

    rows = [json.loads(l) for l in open(G2B / "candidates.jsonl", encoding="utf-8-sig") if l.strip()]
    raws = [r["raw"] for r in rows]
    v1 = tag(raws)
    cand = tag(raws, CANDIDATE)

    work = []
    for i, r in enumerate(rows):
        if v1[i]["labels"] != cand[i]["labels"] and v1[i]["tokens"] == cand[i]["tokens"]:
            work.append({"raw": raws[i], "state": r["state"], "cohort": cohort_of(r["state"]),
                         "tokens": v1[i]["tokens"], "v1": v1[i]["labels"], "v2": cand[i]["labels"]})
    assert len(work) == len(LETTERS) == 136, (len(work), len(LETTERS))

    verdicts = {}
    for idx, (w, letter) in enumerate(zip(work, LETTERS), 1):
        if letter == "n":
            model, judged = "neither", None
        else:
            model = key[letter]
            judged = w[model]
        entry = {"verdict": model, "state": w["state"], "cohort": w["cohort"],
                 "round": 9, "judged_labels": judged}
        note = NOTES.get(idx) or BLOCK_NOTES.get(idx)
        if note:
            entry["note"] = note
        verdicts[w["raw"]] = entry

    n_v2 = sum(1 for v in verdicts.values() if v["verdict"] == "v2")
    n_v1 = sum(1 for v in verdicts.values() if v["verdict"] == "v1")
    n_ne = sum(1 for v in verdicts.values() if v["verdict"] == "neither")
    print(f"ingested {len(verdicts)}: candidate(v50) {n_v2} / incumbent {n_v1} / neither {n_ne}")
    print(f"key: A={key['A']} B={key['B']}")
    if args.verify:
        for idx, (w, letter) in enumerate(zip(work, LETTERS), 1):
            print(f"{idx:4} {letter} -> {verdicts[w['raw']]['verdict']:7} [{w['cohort'][:6]}] {w['raw'][:56]}")
        return
    (G2B / "verdicts_r9.json").write_text(json.dumps(verdicts, indent=1), encoding="utf-8")
    print(f"wrote {G2B / 'verdicts_r9.json'}")


if __name__ == "__main__":
    main()
