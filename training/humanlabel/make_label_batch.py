"""Generate a human-labeling batch doc from the value-ordered candidate list.

Confirm-or-correct workflow, same as gold-2c: each record shows the model's
proposed parse; the reviewer answers `ok`, a correction like
`MT = PlaceName; GILEAD = PlaceName`, or `skip`. Records come in value order
(model least sure first), so a partial batch still captures the highest-value
labels. Each approved record becomes training input; the ordering means the
first hour of review teaches the model more than the tenth.

Usage: python training/humanlabel/make_label_batch.py --start 1 --count 300
"""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).parent
CANDS = HERE / "candidates_for_labeling.jsonl"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--count", type=int, default=300)
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(CANDS, encoding="utf-8") if l.strip()]
    batch = rows[a.start - 1: a.start - 1 + a.count]

    head = [f"# Address labeling — batch {a.start}-{a.start + len(batch) - 1} "
            f"of {len(rows)}", "",
            "## What this is", "",
            "Real owner-mail addresses the shipping model is **least sure about**, ordered so "
            "the most informative come first. Every record you label becomes training data for "
            "a future v2 -- the one thing the campaign proved it needs is more real, "
            "human-labeled free text of exactly this kind. None of these appear in any "
            "evaluation set, so training on them keeps every gold set honest.", "",
            "## How to answer", "",
            "Under each address is the model's proposed parse. For each record:",
            "- **`ok`** — the parse is right.",
            "- **A correction** — name only the tokens that are wrong, e.g. "
            "`MT = PlaceName; GILEAD = PlaceName` or `LUXSTOR = Recipient`. Everything you "
            "don't mention stays as proposed.",
            "- **`skip`** — genuinely ambiguous or you'd be guessing. Never counted; skipping "
            "is a real answer.", "",
            "You'll notice many of these are already wrong — that's the point. The model reads "
            "`MT GILEAD` as a box number, splits `EL RENO`, calls a street a state. Your "
            "corrections are what fix that. Stop whenever your time runs out; the ordering "
            "means you never waste effort on the easy ones.", "",
            "---", ""]

    body = []
    for n, r in enumerate(batch, a.start):
        body.append(f"## {n}. `{r['raw']}`")
        body.append(f"*{r['state']} · model confidence {r['min_confidence']:.2f}*")
        body.append("")
        body.append("| Token | Proposed label |")
        body.append("|---|---|")
        for t, l in zip(r["prelabel_tokens"], r["prelabel_labels"]):
            body.append(f"| `{t}` | {l} |")
        body.append("")
        body.append("**Your answer:** `      `")
        body.append("")
        body.append("---")
        body.append("")

    tail = ["## When you're done", "",
            "Paste answers back in any form. They're stored as approved label sequences and "
            "join the training corpus for the next v2 attempt. This is a dev/training asset, "
            "not an exam: gold-2b's final scoring attempt stays untouched, and any model this "
            "produces still has to clear gold-2c (your absolute labels) and then the exam "
            "before it could ship.", "",
            f"Batch size is yours to set — this is records {a.start}-"
            f"{a.start + len(batch) - 1}; there are {len(rows)} in value order. Label as far "
            "as your budget allows; ask for the next batch when ready."]

    out = HERE / f"BATCH-{a.start:04d}.md"
    out.write_text("\n".join(head + body + tail), encoding="utf-8")
    print(f"batch {a.start}-{a.start + len(batch) - 1} ({len(batch)} records) -> {out}")


if __name__ == "__main__":
    main()
