"""Gold-2c review doc: absolute label approval, not an A/B comparison.

Gold-2 and gold-2b asked "which of these two parses is better?" -- verdicts
that expire the moment a new candidate appears. This asks "is this parse
correct?" and stores the approved sequence, so every future candidate scores
against the same fixed target with no further human review. That is the whole
reason gold-2c exists.

Selection: every record where any scored model disagrees (the informative
ones), plus a seeded random audit slice of the unanimous records -- because
both-wrong classes like the Canadian postal codes only surface in an audit,
never in a disagreement list.

Usage: python tools/make_gold2c_review_doc.py --models model/candidates/v43.crfsuite,model/candidates/v50.crfsuite
"""

import argparse
import collections
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

G2C = ROOT / "eval" / "gold2c"
SEED = 20260821
CAP = 150
AUDIT = 45


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
    ap.add_argument("--models", default="model/candidates/v43.crfsuite,model/candidates/v50.crfsuite")
    args = ap.parse_args()
    models = [m for m in args.models.split(",") if m]

    rows = [json.loads(l) for l in open(G2C / "candidates.jsonl", encoding="utf-8-sig") if l.strip()]
    raws = [r["raw"] for r in rows]
    v1 = tag(raws)
    others = {m: tag(raws, m) for m in models}

    disagree, unanimous = [], []
    for i, r in enumerate(rows):
        alts = {}
        for m, preds in others.items():
            if preds[i]["labels"] != v1[i]["labels"] and preds[i]["tokens"] == v1[i]["tokens"]:
                alts[Path(m).stem] = preds[i]["labels"]
        entry = {"i": i, "raw": raws[i], "state": r["state"], "tokens": v1[i]["tokens"],
                 "proposed": v1[i]["labels"], "alts": alts}
        (disagree if alts else unanimous).append(entry)

    rng = random.Random(SEED)
    audit = rng.sample(unanimous, min(AUDIT, len(unanimous)))
    picked = disagree + audit
    if len(picked) > CAP:
        picked = disagree[:CAP - AUDIT] + audit
    picked.sort(key=lambda e: e["i"])
    (G2C / "review_selection.json").write_text(
        json.dumps({"seed": SEED, "cap": CAP, "audit_size": len(audit),
                    "disagreement_count": len(disagree),
                    "indices": [e["i"] for e in picked]}, indent=1), encoding="utf-8")

    head = [f"# Gold-2c label approval — {len(picked)} addresses", "",
            "## What this is, and how it differs from rounds 7-9", "",
            "Those rounds asked which of two parses was better. Those verdicts died with the "
            "candidate pair that produced them, which is why the last dev surface had only 69 "
            "usable records and could not tell a winner from a loser.", "",
            "**This asks a different question: is the proposed parse correct?** Your answer is "
            "stored as the approved labelling for that address, and every future candidate "
            "gets scored against it forever, with no further review from you. Build it once, "
            "use it for the rest of the project.", "",
            "## How to answer", "",
            "- **`ok`** — the proposed labels are right.",
            "- **A correction** — write what the disputed token(s) should be, e.g. "
            "`ST = StreetNamePostType` or `WEST, CALDWELL = PlaceName`. Only the tokens you "
            "mention change; everything else stands as proposed.",
            "- **`skip`** — genuinely ambiguous, or you would be guessing. Stored unscoreable, "
            "never counted. Skipping is a real answer here, not a failure to answer.", "",
            f"Where a candidate model reads a token differently, its reading is shown in the "
            f"**Alternative** column so you can see the live disagreement — but the question is "
            f"still \"what is correct\", not \"who wins\". "
            f"{len(disagree)} records carry a disagreement; {len(audit)} are a seeded random "
            "audit of records where every model already agrees (those catch the cases where "
            "everyone is wrong together, like the Canadian postal codes in round 9).", "",
            "---", ""]

    body = []
    for n, e in enumerate(picked, 1):
        body.append(f"## {n}. `{e['raw']}`")
        body.append(f"*{e['state']}*" + ("" if e["alts"] else "  ·  _audit record: all models agree_"))
        body.append("")
        if e["alts"]:
            body.append("| Token | Proposed | Alternative |")
            body.append("|---|---|---|")
            for j, (t, l) in enumerate(zip(e["tokens"], e["proposed"])):
                diffs = {name: labs[j] for name, labs in e["alts"].items() if labs[j] != l}
                alt = ", ".join(f"{v} ({k})" for k, v in diffs.items()) if diffs else ""
                mark = " **←**" if diffs else ""
                body.append(f"| `{t}`{mark} | {'**' + l + '**' if diffs else l} | {alt} |")
        else:
            body.append("| Token | Proposed |")
            body.append("|---|---|")
            for t, l in zip(e["tokens"], e["proposed"]):
                body.append(f"| `{t}` | {l} |")
        body.append("")
        body.append("**Your answer:** `      `")
        body.append("")
        body.append("---")
        body.append("")

    tail = ["## When you're done", "",
            "Answers get stored as approved label sequences in "
            "`eval/gold2c/approved_labels.json`. Gold-2c is a **dev surface**: it steers "
            "candidate selection and may never be cited in a public claim. Before it steers "
            "anything, it has to prove itself — it must rank v43 above v50, which is the order "
            "gold-2b already established. If it fails that check it gets published as a failed "
            "instrument, like the two before it.", "",
            "Gold-2b's final scoring attempt stays unspent until this instrument earns its "
            "keep."]

    out = G2C / "REVIEW-labels.md"
    out.write_text("\n".join(head + body + tail), encoding="utf-8")
    states = collections.Counter(e["state"] for e in picked)
    print(f"{len(picked)} records for review ({len(disagree)} disagreements + {len(audit)} audit) "
          f"across {len(states)} states -> {out}")


if __name__ == "__main__":
    main()
