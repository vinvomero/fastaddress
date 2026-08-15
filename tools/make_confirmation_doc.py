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
OUT = G / "CONFIRMATION-round5.md"
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
    citydir = json.loads((G / "citydir_evidence.json").read_text(encoding="utf-8")) if (G / "citydir_evidence.json").exists() else {}

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
        f"# Address review — {len(todo)} parses to judge",
        "",
        "## What this is",
        "",
        "Each entry below is one real address where the original parser and the retrained one "
        "disagree about what the pieces mean. You're deciding which reading is right.",
        "",
        "**These decide whether the new model ships.** It already clears every other gate: it "
        "matches the original exactly on upstream's held-out set (159/159) and gets every one of "
        "the 75 previously-judged records right. What it also does is relabel the addresses "
        "below, and the accuracy bar we set before building anything can only count records a "
        "human has actually reviewed. If these go the model's way it clears the bar; if they "
        "don't, it doesn't ship. Please judge them on the evidence rather than on that fact — a "
        "bar we talk ourselves over is worth nothing.",
        "",
        "**One of them is a trap, deliberately left in.** At least one address here is a case "
        "where the model's new reading is wrong and the original was right. The Census evidence "
        "under each entry will show you which. I have not marked it.",
        "",
        f"These **{len(todo)}** are the only ones that matter. Everywhere else the two parsers "
        "agree, and when they agree neither can look better than the other — so those need no "
        "judgment at all.",
        "",
        "## How to answer",
        "",
        "The two parsers are hidden as **A** and **B**, reshuffled for this round, so the "
        "suggestion can't sway you. Each table shows the whole address so you can see the reading "
        "in context; the rows they actually disagree on are marked **←** and bolded.",
        "",
        "Write one of: **A** · **B** · **neither** (both readings wrong) · **skip** (genuinely "
        "ambiguous). **Suggested** is the earlier unconfirmed answer — agreeing with it is a fine "
        "outcome, it just needs to be your call.",
        "",
        "Where a Census record was found it's quoted underneath. Treat it as evidence, not proof: "
        "anything flagged with ⚠️ resolved to a city that isn't in the address, which usually "
        "means the geocoder guessed.",
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

        # For the "<letter> <CITY>" ambiguity, the geocoder's own decomposition
        # is the decisive evidence: which side of the split it put the letter on.
        cd = citydir.get(raw)
        if cd and cd.get("reading") in ("place", "directional"):
            if cd["reading"] == "place":
                out.append(
                    f"*Census splits this as:* city **{cd.get('city')}** — the `{cd.get('letter')}` "
                    f"is part of the **city name**, street is **{cd.get('street')}**"
                )
            else:
                out.append(
                    f"*Census splits this as:* city **{cd.get('city')}**, street **{cd.get('street')}** "
                    f"with suffix direction **{cd.get('suffix_direction')}** — here the "
                    f"`{cd.get('letter')}` really is a **direction**, not part of the city"
                )
            out.append("")

        sug = info["verdict"] if info else None
        toks = b["tokens"]
        # The whole parse is shown, not just the differing tokens: judging "is
        # LK a city or a street type" is impossible without seeing how the rest
        # of the address was read. Disagreements are marked so they still stand
        # out at a glance.
        out.append("| | Token | Model A | Model B |")
        out.append("|---|---|---|---|")
        for j, t in enumerate(toks):
            bl = b["labels"][j] if j < len(b["labels"]) else "-"
            cl = c["labels"][j] if j < len(c["labels"]) else "-"
            al = bl if a_is_v1 else cl
            bb = cl if a_is_v1 else bl
            if bl == cl:
                out.append(f"| | `{t}` | {al} | {bb} |")
            else:
                out.append(f"| **←** | `{t}` | **{al}** | **{bb}** |")
        out.append("")
        if sug in ("v1", "v2"):
            out.append(f"**Suggested: {letter_for(sug)}**  →  **Your verdict:** `      `")
        elif sug:
            out.append(f"**Suggested: {sug}**  →  **Your verdict:** `      `")
        else:
            out.append("**Suggested: none — never judged**  →  **Your verdict:** `      `")
        out.append("")
        out.append("---")
        out.append("")

    out += [
        "## When you're done",
        "",
        "Paste the answers back in any form — `1. A, 2. B, 3. neither` is fine, and you can group "
        "runs of the same answer. I'll un-blind them, fold them into the record, and recompute the "
        "margin using only human-reviewed evidence so the published figure is one you stood "
        "behind.",
        "",
        "If any of these are genuinely too ambiguous to call, **skip** is a real answer and is "
        "recorded as such — a forced guess would be worse than an honest gap.",
    ]
    OUT.write_text("\n".join(out), encoding="utf-8")
    print(f"{len(todo)} records needing human review -> {OUT}")


if __name__ == "__main__":
    main()
