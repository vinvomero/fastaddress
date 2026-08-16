"""Round-7 review doc: gold-2 disagreements, blinded, tripwire-compliant.

Tags every gold-2 record with v1 and the candidate, keeps the disagreements,
and applies PROTOCOL2's adjudication-volume tripwire: if disagreements exceed
150, a seeded random sample of 150 is drawn BEFORE any verdicts exist and the
sample spec is written to disk — the margin then uses a sampling-adjusted CI.

Blinding: fresh A/B key per round, written to eval/gold2/blind_key_r7.json.
No suggestions are shown — gold-2 records have no prior LLM verdicts, and a
clean first read is worth more than a prefilled one.

Usage: python tools/make_gold2_review_doc.py --candidate model/candidates/v36.crfsuite
       python tools/make_gold2_review_doc.py --candidate ... --round 8 --attempt 2

Round 8 (attempt 2 of 2) uses a fresh seed and a fresh blind key; the
tripwire semantics are identical and the sample spec (if triggered) is
still drawn before any verdicts exist.
"""

import argparse
import csv
import json
import random
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent
G2 = ROOT / "eval" / "gold2"
EVAL_BIN = "C:/cargo-target/us-address-parser/release/eval_tag.exe"
BASE_SEED = 20260809  # + round; round 7 reproduces the original 20260816
TRIPWIRE = 150


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
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--round", type=int, default=7)
    ap.add_argument("--attempt", type=int, default=1)
    args = ap.parse_args()
    rnd = args.round
    seed = BASE_SEED + rnd

    rows = [json.loads(l) for l in open(G2 / "candidates.jsonl", encoding="utf-8-sig") if l.strip()]
    raws = [r["raw"] for r in rows]
    v1 = tag(raws)
    cand = tag(raws, args.candidate)

    disagreements = []
    for i, r in enumerate(rows):
        if v1[i]["labels"] != cand[i]["labels"] and v1[i]["tokens"] == cand[i]["tokens"]:
            disagreements.append({"raw": raws[i], "state": r["state"], "source": r.get("source", ""),
                                  "tokens": v1[i]["tokens"], "v1": v1[i]["labels"], "cand": cand[i]["labels"]})

    total = len(disagreements)
    sampled = False
    if total > TRIPWIRE:
        # Tripwire: seeded sample drawn before any verdicts, spec persisted.
        rng = random.Random(seed)
        idx = sorted(rng.sample(range(total), TRIPWIRE))
        (G2 / f"tripwire_sample_r{rnd}.json").write_text(
            json.dumps({"seed": seed, "total_disagreements": total, "sample_size": TRIPWIRE,
                        "indices": idx}), encoding="utf-8")
        disagreements = [disagreements[i] for i in idx]
        sampled = True

    rng = random.Random(seed + 1)
    a_is_v1 = rng.random() < 0.5
    (G2 / f"blind_key_r{rnd}.json").write_text(
        json.dumps({"A": "v1" if a_is_v1 else "v2", "B": "v2" if a_is_v1 else "v1"}, indent=1),
        encoding="utf-8")

    head = [f"# Address review — Round {rnd} (national free-text): {len(disagreements)} parses", "",
            "## What this is", "",
            "Real owner-mailing addresses fetched from state and county open-data portals across "
            "the country — free text as assessors wrote it, the evidence base for any public "
            "'national' claim. These are every record where the two parsers disagree" +
            (f" — sampled down to {TRIPWIRE} of {total} by the pre-registered tripwire "
             f"(seeded draw, spec committed before any verdicts; the margin uses a "
             f"sampling-adjusted CI)." if sampled else "."), "",
            "No suggestions this round: gold-2 has no prior machine verdicts, and a clean first "
            "read is worth more than a prefilled one. Models are blinded as A/B under a fresh "
            "key. Answer **A** · **B** · **neither** · **skip** per entry.", "",
            "The source dataset is named under each address — these are records of real "
            "properties, so public listings are fair evidence.", "", "---", ""]

    body = []
    for i, d in enumerate(disagreements, 1):
        body.append(f"## {i}. `{d['raw']}`")
        body.append(f"*{d['state']} — {d['source'][:80]}*")
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

    tailer = ["## When you're done", "",
              "Paste answers back in any form. They get un-blinded, stored with the approved "
              "label sequences, and the pre-registered gates compute from human verdicts only. "
              f"This is scoring attempt {args.attempt} of 2 against gold-2 — the attempt count "
              "ships with any claim either way."]
    doc = "\n".join(head + body + tailer)
    out = G2 / f"REVIEW-round{rnd}.md"
    out.write_text(doc, encoding="utf-8")
    print(f"{len(disagreements)} disagreements ({total} before tripwire, sampled={sampled}) -> {out}")


if __name__ == "__main__":
    main()
