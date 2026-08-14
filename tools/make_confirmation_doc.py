"""Round-1 confirmation worklist: the records the gate legally cannot use yet.

WHY
---
PROTOCOL.md, step 3 of the labeling method, pre-registered this rule:

    "A human reviews every record before it counts. Records carry a status
     field -- prelabeled, llm_reviewed, or adjudicated -- and only adjudicated
     records enter gate arithmetic."

Round 1's verdicts were produced by an LLM and never confirmed by a human, so
by the protocol's own rule they are `llm_reviewed` and must not enter gate
arithmetic. Rounds 2 and 3 were human-reviewed and do count.

That leaves the gold gate computable only over a handful of records. This
builds the worklist that closes it -- and only the records that actually
matter: a record where the two models produce the SAME parse contributes
exactly zero to a margin, so it needs no verdict at all. The worklist is
therefore the differing, not-yet-human-reviewed set, which is far smaller than
round 1's full verdict list.

Blinding is preserved. The suggested answer is shown as a blinded letter under
a freshly re-rolled key, so confirming it cannot be biased by knowing which
model produced which parse.

Usage: python tools/make_confirmation_doc.py [--candidate model/usaddr_v2.crfsuite]
"""

import argparse
import csv
import json
import random
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent
G = ROOT / "eval" / "gold"
OUT = G / "CONFIRMATION-round1.md"
KEY = G / "blind_key-confirm.json"
EVAL_BIN = "C:/cargo-target/us-address-parser/release/eval_tag.exe"
SEED = 20260814


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
    ap.add_argument("--candidate", default="model/usaddr_v2.crfsuite")
    args = ap.parse_args()

    rng = random.Random(SEED)
    gold = [json.loads(l) for l in open(G / "candidates.jsonl", encoding="utf-8-sig") if l.strip()]
    raws = [r["raw"] for r in gold]
    base, cand = tag(raws), tag(raws, args.candidate)
    merged = json.loads((G / "verdicts-merged.json").read_text(encoding="utf-8"))
    census = json.loads((G / "census_evidence.json").read_text(encoding="utf-8")) if (G / "census_evidence.json").exists() else {}

    todo = []
    for i, raw in enumerate(raws):
        if base[i]["labels"] == cand[i]["labels"]:
            continue  # identical parse -> contributes zero to the margin
        info = merged.get(raw)
        if info and info.get("human_reviewed"):
            continue  # already counts
        todo.append((raw, base[i], cand[i], info))

    a_is_v1 = rng.random() < 0.5
    KEY.write_text(json.dumps({"A": "v1" if a_is_v1 else "v2",
                               "B": "v2" if a_is_v1 else "v1"}, indent=1), encoding="utf-8")

    def letter_for(which):
        return "A" if (which == "v1") == a_is_v1 else "B"

    out = [
        f"# Confirmation round — {len(todo)} addresses",
        "",
        "## Why you're being asked for these",
        "",
        "The evaluation protocol we wrote *before* training anything says only records a human "
        "reviewed may count toward the ship decision. The first batch of verdicts came from "
        "ChatGPT and were never confirmed by you, so by our own rule they cannot be used.",
        "",
        f"These **{len(todo)}** are the only records where that matters. Everywhere else the two "
        "models produce an identical parse, and an identical parse can't make one model look "
        "better than the other — so those records need no judgment at all.",
        "",
        "Models are blinded as **A** and **B** (key re-rolled for this round and written to the "
        "repo, so the suggestion below can't tip you off). **Suggested** is the earlier "
        "unconfirmed answer. Confirm it or write a different one.",
        "",
        "Answer **A**, **B**, **neither** (both parses wrong), or **skip** (genuinely ambiguous).",
        "",
        "---",
        "",
    ]

    for i, (raw, b, c, info) in enumerate(todo, 1):
        out.append(f"## {i}. `{raw}`")
        out.append("")
        ev = census.get(raw)
        if ev and ev.get("status") == "match":
            city = ev.get("city") or ""
            flag = ("  ⚠️ *resolved to a city not present in the input — treat as suspect*"
                    if city and city.upper() not in raw.upper() else "")
            hn = ev.get("house_number_range")
            out.append(
                f"*Census record:* {ev.get('matched')} — street **{ev.get('street')}**, "
                f"type `{ev.get('suffix_type') or '-'}`, pre-dir `{ev.get('pre_direction') or '-'}`, "
                f"post-dir `{ev.get('suffix_direction') or '-'}`, city **{city}**"
            )
            if hn:
                out.append(f"  (block range {hn} — the range this address falls in, not its own number){flag}")
            out.append("")

        sug = info["verdict"] if info else None
        toks = b["tokens"]
        out.append("| Token | Model A | Model B |")
        out.append("|---|---|---|")
        for j, t in enumerate(toks):
            bl = b["labels"][j] if j < len(b["labels"]) else "-"
            cl = c["labels"][j] if j < len(c["labels"]) else "-"
            if bl == cl:
                continue
            al = bl if a_is_v1 else cl
            bb = cl if a_is_v1 else bl
            out.append(f"| `{t}` | **{al}** | **{bb}** |")
        out.append("")
        if sug in ("v1", "v2"):
            out.append(f"**Suggested:** {letter_for(sug)}  →  **Your verdict:** _____")
        elif sug:
            out.append(f"**Suggested:** {sug}  →  **Your verdict:** _____")
        else:
            out.append("**Suggested:** *(never judged)*  →  **Your verdict:** _____")
        out.append("")
        out.append("---")
        out.append("")

    out += [
        "## When you're done",
        "",
        "Paste the answers back. The agent un-blinds them, recomputes the full-set margin using "
        "only human-reviewed evidence, and reports whether the model clears the pre-registered "
        "+3.0 percentage-point bar.",
    ]
    OUT.write_text("\n".join(out), encoding="utf-8")
    print(f"{len(todo)} records needing human review -> {OUT}")


if __name__ == "__main__":
    main()
