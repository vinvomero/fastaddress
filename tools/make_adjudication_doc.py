"""Turn eval/gold/disagreements.jsonl into a human-fillable adjudication doc.

Design choices that matter:
  * Grouped by disagreement SHAPE (the ordered set of label flips), so the 31
    identical saint-name cases are one decision instead of 31.
  * Blind: models are shown as A and B. The adjudicator judges which parse is
    correct, not which model they expect to win. The A/B -> v1/v2 mapping is
    written to eval/gold/blind_key.json (auditable, not in the doc).
  * Ordered by group size, so the highest-leverage decisions come first.

Usage: python tools/make_adjudication_doc.py
Outputs: eval/gold/ADJUDICATION.md  +  eval/gold/blind_key.json
"""

import json
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent
SRC = ROOT / "eval" / "gold" / "disagreements.jsonl"
DOC = ROOT / "eval" / "gold" / "ADJUDICATION.md"
KEY = ROOT / "eval" / "gold" / "blind_key.json"
SEED = 20260813
EXAMPLES_PER_GROUP = 3
LIST_CAP = 12


def signature(rec):
    return tuple((d["v1"], d["v2"]) for d in rec["differing_tokens"])


def prior_verdicts_by_shape():
    """Carry forward verdicts from an earlier adjudication pass.

    A verdict is about which PARSE is correct, so it transfers to any later
    candidate producing the identical disagreement shape. Prior letters are
    translated through the prior blind key into model terms (incumbent vs
    challenger), which is what actually carries.
    """
    prior_dis = ROOT / "eval" / "gold" / "disagreements-prior.jsonl"
    prior_key = ROOT / "eval" / "gold" / "blind_key-prior.json"
    prior_verd = ROOT / "eval" / "gold" / "verdicts-chatgpt-2026-08-13.json"
    if not (prior_dis.exists() and prior_key.exists() and prior_verd.exists()):
        return {}
    # utf-8-sig: files recovered via shell redirect can carry a BOM.
    key = json.loads(prior_key.read_text(encoding="utf-8-sig"))
    verd = json.loads(prior_verd.read_text(encoding="utf-8-sig"))
    gv = {int(k): v for k, v in verd["groups"].items()}
    rows = [json.loads(l) for l in open(prior_dis, encoding="utf-8-sig") if l.strip()]
    groups = defaultdict(list)
    for r in rows:
        groups[signature(r)].append(r)
    ordered = sorted(groups.values(), key=len, reverse=True)
    out = {}
    for i, grp in enumerate(ordered, 1):
        letter = gv.get(i)
        if not letter:
            continue
        out[signature(grp[0])] = key.get(letter, letter)  # -> "v1" | "v2" | neither/skip
    return out


def main():
    rng = random.Random(SEED)
    rows = [json.loads(l) for l in open(SRC, encoding="utf-8") if l.strip()]

    # Blind assignment: a coin flip decides whether A=v1 or A=v2, once for the
    # whole document (consistent labels across every group).
    a_is_v1 = rng.random() < 0.5
    KEY.write_text(
        json.dumps({"A": "v1" if a_is_v1 else "v2", "B": "v2" if a_is_v1 else "v1"}, indent=1),
        encoding="utf-8",
    )

    def key_a_model(flag):
        return "v1" if flag else "v2"

    def key_b_model(flag):
        return "v2" if flag else "v1"

    def a_label(d):
        return d["v1"] if a_is_v1 else d["v2"]

    def b_label(d):
        return d["v2"] if a_is_v1 else d["v1"]

    groups = defaultdict(list)
    for r in rows:
        groups[signature(r)].append(r)
    ordered = sorted(groups.values(), key=len, reverse=True)

    prior = prior_verdicts_by_shape()
    inv = {v: k for k, v in {"A": key_a_model(a_is_v1), "B": key_b_model(a_is_v1)}.items()}
    carried = [g for g in ordered if signature(g[0]) in prior]
    fresh = [g for g in ordered if signature(g[0]) not in prior]
    n_fresh = sum(len(g) for g in fresh)

    out = [
        f"# Adjudication round 2 — {n_fresh} addresses need your call",
        "",
        f"The parsers now disagree on {len(rows)} of 1,500 messy addresses ({len(ordered)} distinct "
        f"shapes). **{len(carried)} shapes carry your verdicts forward from last time and need no "
        f"action** — they are listed at the bottom for reference only. That leaves "
        f"**{len(fresh)} groups covering {n_fresh} addresses** to judge.",
        "",
        "**Models are blinded as A and B on purpose.** Judge which parse is *correct*, not which "
        "model you expect to win. (The A/B mapping is recorded in the repo, so the result stays "
        "auditable.)",
        "",
        "## How to fill this out",
        "",
        "For each group, replace the `Verdict:` value with **A**, **B**, **neither**, or **skip** "
        "(use skip when the address is genuinely ambiguous). If one address in a group deserves a "
        "different answer than the rest, add a line under it — group verdicts are defaults, not "
        "handcuffs.",
        "",
        "Labels are usaddress component names: `AddressNumber`, `StreetName`, "
        "`StreetNamePostType` (St/Ave/Rd), `StreetNamePreDirectional` (N/S/E/W before the name), "
        "`PlaceName` (city), `StateName`, `ZipCode`, `OccupancyType`/`OccupancyIdentifier` "
        "(Apt 4B), `USPSBoxType`/`USPSBoxID` (PO Box 12), `Recipient`, `LandmarkName`, "
        "`BuildingName`.",
        "",
        "---",
        "",
    ]

    for i, grp in enumerate(fresh, 1):
        n = len(grp)
        flips = grp[0]["differing_tokens"]
        out.append(f"## Group {i} — {n} address{'es' if n > 1 else ''}")
        out.append("")
        out.append("**The disagreement:**")
        out.append("")
        out.append("| Token | Model A says | Model B says |")
        out.append("|---|---|---|")
        for d in flips:
            out.append(f"| `{d['token']}` | {a_label(d)} | {b_label(d)} |")
        out.append("")
        out.append("**Examples:**")
        out.append("")
        for r in grp[:EXAMPLES_PER_GROUP]:
            out.append(f"- `{r['raw']}`")
        if n > EXAMPLES_PER_GROUP:
            extra = [r["raw"] for r in grp[EXAMPLES_PER_GROUP:LIST_CAP]]
            for e in extra:
                out.append(f"- `{e}`")
            if n > LIST_CAP:
                out.append(f"- …and {n - LIST_CAP} more with the same shape")
        out.append("")
        out.append(f"**Verdict:** _____   (A / B / neither / skip)")
        out.append("")
        out.append("---")
        out.append("")

    if carried:
        out += [
            "## Already decided last round — no action needed",
            "",
            "These shapes match verdicts you already gave; they are carried forward automatically "
            "and listed only so the record is complete.",
            "",
        ]
        for grp in carried:
            model = prior[signature(grp[0])]
            letter = inv.get(model, model)
            flips = ", ".join(f"`{d['token']}`" for d in grp[0]["differing_tokens"][:3])
            out.append(
                f"- {len(grp)} address(es) differing on {flips} — your prior verdict favors "
                f"**Model {letter}** here"
            )
        out.append("")
        out.append("---")
        out.append("")

    out += [
        "## When you're done",
        "",
        "Tell the agent it's filled in. It will read the verdicts, un-blind them, and score the "
        "gold gate — which decides whether the retrained model ships or stays shelved.",
        "",
        "Disclosed limitation: judging only contested cases measures *relative* accuracy on the "
        "cases where the parsers differ, not absolute accuracy across all 1,500. It informs the "
        "decision; it does not replace the full-set gate in the protocol.",
    ]

    DOC.write_text("\n".join(out), encoding="utf-8")
    print(f"{len(rows)} records in {len(ordered)} groups -> {DOC}")
    print(f"blind key -> {KEY}")


if __name__ == "__main__":
    main()
