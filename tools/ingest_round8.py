"""Ingest Round-8 human verdicts (gold-2 scoring attempt 2, candidate v43).

Rebuilds the 64-record disagreement worklist deterministically (same tag +
compare logic and record order as make_gold2_review_doc.py), un-blinds via
the committed round-8 key (A=v1, B=v2), and stores verdicts with the
approved label sequence (judged_labels) so third readings are impossible.

Consistency checks before writing:
  - worklist length == 64 and every position has a verdict
  - West Caldwell block (#34-40): every winner labels the West token PlaceName
  - S Burlington records (#57,58,60,61,62): winner labels S as PlaceName
  - PMB records (#6,#32): winner is v1 per the human note

Usage: python tools/ingest_round8.py [--verify]
"""

import argparse
import csv
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent
G2 = ROOT / "eval" / "gold2"
EVAL_BIN = "C:/cargo-target/us-address-parser/release/eval_tag.exe"
CANDIDATE = "model/candidates/v43.crfsuite"

# Human verdict letters, 2026-08-16, entered verbatim from the review reply.
LETTERS = (
    "A B n B B A B B B B "    # 1-10
    "A B B B A A B B n B "    # 11-20
    "A n n B B B B A B A "    # 21-30
    "A A B B A B A A A A "    # 31-40
    "B A A A A B B n B A "    # 41-50
    "B B B A B A B B B B "    # 51-60
    "B B A A"                  # 61-64
).split()

NOTES = {
    6: "PMB = Private Mailbox; federal standard: Subaddress Type + Identifier",
    14: "Den Hollow is the street name; omitted St is the suffix",
    19: "neither handles the full disputed span (Thwy terminal type vs N predirectional)",
    22: "29 = AddressNumber; leading ROOSEVELT TRAIL unexplained by either",
    23: "0 Swans Rd / C/O Robert Fogg / Raymond ME; both sequences misplace a span",
    26: "14744 W Chicago, Detroit: Chicago is StreetName",
    30: "S Trail Ridge Ave: TRL belongs to StreetName, not pre-type",
    33: "20 1/2 Ave S: 20 = StreetName",
    45: "Winterberry Xing: CROSSING is the terminal street type",
    48: "Lantana: CROSSING should be post-type; neither model has it",
    51: "Westberry Ct W: W is a post-directional",
    52: "Westberry Ct W: W is a post-directional",
    54: "Apple Springs Holw: HOLW is the terminal suffix",
    55: "N Chesterfield = abbreviated locality; N is PlaceName",
    63: "COMMONS -> CMNS is a USPS street suffix; COMMONS = StreetNamePostType",
    64: "P O BOX = spaced PO BOX; P, O, BOX are the box type",
}


def tag(raws, model=None):
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8", newline="") as tf:
        w = csv.writer(tf)
        w.writerow(["raw_address"])
        for r in raws:
            w.writerow([r])
        tmp = tf.name
    cmd = [EVAL_BIN, tmp] + (["--model", model] if model else [])
    out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=True)
    return [json.loads(l) for l in out.stdout.splitlines() if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true", help="print mapping, write nothing")
    args = ap.parse_args()

    key = json.loads((G2 / "blind_key_r8.json").read_text(encoding="utf-8"))
    rows = [json.loads(l) for l in open(G2 / "candidates.jsonl", encoding="utf-8-sig") if l.strip()]
    raws = [r["raw"] for r in rows]
    v1 = tag(raws)
    cand = tag(raws, CANDIDATE)

    work = []
    for i, r in enumerate(rows):
        if v1[i]["labels"] != cand[i]["labels"] and v1[i]["tokens"] == cand[i]["tokens"]:
            work.append({"raw": raws[i], "state": r["state"],
                         "tokens": v1[i]["tokens"], "v1": v1[i]["labels"], "v2": cand[i]["labels"]})
    assert len(work) == len(LETTERS) == 64, (len(work), len(LETTERS))

    verdicts, problems = {}, []
    for idx, (w, letter) in enumerate(zip(work, LETTERS), 1):
        if letter == "n":
            model, judged = "neither", None
        else:
            model = key[letter]          # A/B -> v1/v2
            judged = w[model]
        entry = {"verdict": model, "state": w["state"], "round": 8,
                 "judged_labels": judged}
        if idx in NOTES:
            entry["note"] = NOTES[idx]
        verdicts[w["raw"]] = entry

        # consistency checks
        def tok_label(substr):
            got = [l for t, l in zip(w["tokens"], (judged or [])) if t.rstrip(",").upper() == substr]
            return got
        if idx in (34, 35, 36, 37, 38, 39, 40) and judged:
            if "PlaceName" not in tok_label("WEST"):
                problems.append(f"#{idx} West Caldwell: WEST not PlaceName in winner")
        if idx in (57, 58, 60, 61, 62) and judged:
            if "PlaceName" not in tok_label("S"):
                problems.append(f"#{idx} S Burlington: S not PlaceName in winner")
        if idx in (6, 32) and model != "v1":
            problems.append(f"#{idx} PMB: expected v1 winner per note, got {model}")

    n_v2 = sum(1 for v in verdicts.values() if v["verdict"] == "v2")
    n_v1 = sum(1 for v in verdicts.values() if v["verdict"] == "v1")
    n_ne = sum(1 for v in verdicts.values() if v["verdict"] == "neither")
    print(f"ingested {len(verdicts)}: candidate(v43) {n_v2} / incumbent {n_v1} / neither {n_ne}")
    print(f"key: A={key['A']} B={key['B']}")
    for p in problems:
        print("CONSISTENCY:", p)
    if args.verify:
        for idx, (w, letter) in enumerate(zip(work, LETTERS), 1):
            print(f"{idx:3} {letter} -> {verdicts[w['raw']]['verdict']:7} | {w['raw'][:60]}")
        return
    if problems:
        raise SystemExit("consistency problems above -- NOT writing; resolve first")
    (G2 / "verdicts_r8.json").write_text(json.dumps(verdicts, indent=1), encoding="utf-8")
    print(f"wrote {G2 / 'verdicts_r8.json'}")


if __name__ == "__main__":
    main()
