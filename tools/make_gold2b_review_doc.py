"""Round-9 review doc: gold-2b disagreements, blinded, cohort-tagged.

Gold-2b's analysis structure is fixed by the owner's rulings (PROTOCOL2,
2026-08-16): the strict-disjoint cohort is the primary, two labelled
sensitivity cohorts sit beside it, and a without-WY robustness line repeats
the primary. Every record here carries its cohort so all four analyses
compute from one human pass.

Tripwire unchanged: above 150 disagreements a seeded sample of 150 is drawn
BEFORE any verdict exists and the spec is written to disk.

Blinding: fresh A/B key per round, written to eval/gold2b/blind_key_r9.json.

Usage: python tools/make_gold2b_review_doc.py --candidate model/candidates/v50.crfsuite
"""

import argparse
import csv
import json
import random
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "benchmark"))
from binpath import bin_path  # noqa: E402

G2B = ROOT / "eval" / "gold2b"
SEED = 20260818
TRIPWIRE = 150


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
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--round", type=int, default=9)
    ap.add_argument("--attempt", type=int, default=1)
    args = ap.parse_args()
    rnd = args.round

    cohorts = json.loads((G2B / "COHORTS.json").read_text(encoding="utf-8"))
    strict = set(cohorts["strict"])
    lineage = set(cohorts["lineage_sensitivity"])
    aggregate = set(cohorts["aggregate_sensitivity"])

    def cohort_of(state):
        if state in strict:
            return "strict"
        if state in lineage:
            return "lineage-sensitivity"
        if state in aggregate:
            return "aggregate-sensitivity"
        return "?"

    rows = [json.loads(l) for l in open(G2B / "candidates.jsonl", encoding="utf-8-sig") if l.strip()]
    raws = [r["raw"] for r in rows]
    v1 = tag(raws)
    cand = tag(raws, args.candidate)

    dis = []
    for i, r in enumerate(rows):
        if v1[i]["labels"] != cand[i]["labels"] and v1[i]["tokens"] == cand[i]["tokens"]:
            dis.append({"raw": raws[i], "state": r["state"], "source": r.get("source", ""),
                        "cohort": cohort_of(r["state"]), "tokens": v1[i]["tokens"],
                        "v1": v1[i]["labels"], "cand": cand[i]["labels"]})

    total = len(dis)
    sampled = False
    if total > TRIPWIRE:
        rng = random.Random(SEED)
        idx = sorted(rng.sample(range(total), TRIPWIRE))
        (G2B / f"tripwire_sample_r{rnd}.json").write_text(
            json.dumps({"seed": SEED, "total_disagreements": total,
                        "sample_size": TRIPWIRE, "indices": idx}), encoding="utf-8")
        dis = [dis[i] for i in idx]
        sampled = True

    rng = random.Random(SEED + 1)
    a_is_v1 = rng.random() < 0.5
    (G2B / f"blind_key_r{rnd}.json").write_text(
        json.dumps({"A": "v1" if a_is_v1 else "v2", "B": "v2" if a_is_v1 else "v1"}, indent=1),
        encoding="utf-8")

    n_strict = sum(1 for d in dis if d["cohort"] == "strict")
    head = [f"# Address review — Round {rnd} (gold-2b): {len(dis)} parses", "",
            "## What this is", "",
            "Gold-2b is the replacement national exam, built after gold-2's two attempts were "
            "spent: 2,912 records across 32 states in the strict cohort, drawn only from "
            "datasets that neither the previous exam nor any training corpus ever touched. "
            "This is scoring attempt " + str(args.attempt) + " of 2 for its lifetime.", "",
            f"These are every record where the two parsers disagree" +
            (f" — sampled to {TRIPWIRE} of {total} by the pre-registered tripwire (seeded draw, "
             f"spec committed before any verdicts)." if sampled else
             f" ({total} of 3,569 records; under the 150 tripwire, so you're seeing all of them)."),
            "",
            f"**{n_strict} are in the strict cohort**, which is the primary analysis. The rest sit "
            "in the two labelled sensitivity cohorts and are marked as such — your verdicts on "
            "them feed the secondary numbers only.", "",
            "Models are blinded as **A** / **B** under a fresh key. Answer **A** · **B** · "
            "**neither** · **skip** per entry. Only human verdicts enter any gate.", "",
            "---", ""]

    body = []
    for i, d in enumerate(dis, 1):
        tag_note = "" if d["cohort"] == "strict" else f"  ·  _{d['cohort']}_"
        body.append(f"## {i}. `{d['raw']}`")
        body.append(f"*{d['state']} — {d['source'][:70]}{tag_note}*")
        body.append("")
        body.append("| | Token | Model A | Model B |")
        body.append("|---|---|---|---|")
        for t, l1, lc in zip(d["tokens"], d["v1"], d["cand"]):
            a = l1 if a_is_v1 else lc
            b = lc if a_is_v1 else l1
            if l1 == lc:
                body.append(f"| | `{t}` | {a} | {b} |")
            else:
                body.append(f"| **←** | `{t}` | **{a}** | **{b}** |")
        body.append("")
        body.append("**Your verdict:** `      `")
        body.append("")
        body.append("---")
        body.append("")

    tail = ["## When you're done", "",
            "Paste answers back in any form. They get un-blinded, stored with the approved label "
            "sequences, and the pre-registered gates compute from human verdicts only. Four "
            "numbers get reported together, per your rulings: the strict-cohort primary, both "
            "sensitivity cohorts labelled separately, and the primary repeated without Wyoming.",
            "", f"This is scoring attempt {args.attempt} of 2 against gold-2b. After the second, "
            "the set is spent and a fresh one is required for any further claim."]

    out = G2B / f"REVIEW-round{rnd}.md"
    out.write_text("\n".join(head + body + tail), encoding="utf-8")
    print(f"{len(dis)} disagreements ({total} before tripwire, sampled={sampled}); "
          f"strict {n_strict} -> {out}")


if __name__ == "__main__":
    main()
