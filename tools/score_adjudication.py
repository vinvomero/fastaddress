"""Score a filled adjudication pass (tools/make_adjudication_doc.py output).

Reads verdicts (group number -> A/B/neither/skip, plus per-address exceptions),
un-blinds them via eval/gold/blind_key.json, and reports how often each model
was judged correct on the contested records.

IMPORTANT — what this can and cannot support:
  * Contested-only: measures RELATIVE accuracy where the parsers differ, not
    absolute accuracy over the full gold set.
  * The adjudicator's identity is recorded in the output. Per eval/PROTOCOL.md,
    only HUMAN-adjudicated records count toward the pre-registered gold gate;
    an LLM pass is triage evidence that informs the next round.

Usage: python tools/score_adjudication.py --verdicts <path.json> --adjudicator "name"
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent
SRC = ROOT / "eval" / "gold" / "disagreements.jsonl"
KEY = ROOT / "eval" / "gold" / "blind_key.json"
OUT = ROOT / "benchmark" / "results" / "adjudication_result.md"


def signature(rec):
    return tuple((d["v1"], d["v2"]) for d in rec["differing_tokens"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verdicts", required=True)
    ap.add_argument("--adjudicator", required=True)
    ap.add_argument("--human", action="store_true", help="set only for human adjudication")
    args = ap.parse_args()

    rows = [json.loads(l) for l in open(SRC, encoding="utf-8") if l.strip()]
    key = json.loads(KEY.read_text(encoding="utf-8"))  # {"A": "v1"|"v2", ...}
    verdicts = json.loads(Path(args.verdicts).read_text(encoding="utf-8"))
    group_verdicts = {int(k): v for k, v in verdicts["groups"].items()}
    exceptions = verdicts.get("exceptions", {})  # raw address -> verdict

    # Rebuild groups exactly as the doc generator did: by shape, size desc.
    groups = defaultdict(list)
    for r in rows:
        groups[signature(r)].append(r)
    ordered = sorted(groups.values(), key=len, reverse=True)

    tally = {"v1": 0, "v2": 0, "neither": 0, "skip": 0}
    per_record = []
    for i, grp in enumerate(ordered, 1):
        gv = group_verdicts.get(i, "skip")
        for r in grp:
            v = exceptions.get(r["raw"], gv)
            winner = key.get(v, v)  # A/B -> v1/v2; neither/skip pass through
            tally[winner] += 1
            per_record.append((r["raw"], v, winner))

    scored = tally["v1"] + tally["v2"]
    total = len(rows)
    lines = [
        "# Contested-record adjudication result",
        "",
        f"Adjudicator: **{args.adjudicator}** "
        f"({'human — counts toward the protocol gate' if args.human else 'LLM — triage evidence, does NOT satisfy the protocol gate'})",
        "",
        f"Contested records: {total} of 1,500 gold candidates (the rest were labeled identically by both models).",
        "",
        "| Outcome | Records | Share of contested |",
        "|---|---|---|",
        f"| v1 (shipped model) judged correct | {tally['v1']} | {tally['v1']/total*100:.1f}% |",
        f"| v2 (retrained candidate) judged correct | {tally['v2']} | {tally['v2']/total*100:.1f}% |",
        f"| neither correct | {tally['neither']} | {tally['neither']/total*100:.1f}% |",
        f"| skipped (ambiguous) | {tally['skip']} | {tally['skip']/total*100:.1f}% |",
        "",
    ]
    if scored:
        lines.append(
            f"Head-to-head on the {scored} decided records: "
            f"**v2 {tally['v2']/scored*100:.0f}% / v1 {tally['v1']/scored*100:.0f}%**."
        )
        lines.append("")
    lines += [
        "## Limits",
        "",
        "- Contested-only: this is relative accuracy where the parsers differ, not absolute "
        "accuracy across the gold set. Both models were identical on "
        f"{1500 - total} of 1,500 records.",
    ]
    if not args.human:
        lines.append(
            "- The adjudicator was an LLM. `eval/PROTOCOL.md` requires human adjudication for the "
            "gold gate, and the prelabels were themselves machine-generated, so this is "
            "corroborating triage evidence — not gate-satisfying data."
        )
    lines += ["", "## Per-record verdicts", "", "| Address | Verdict (blind) | Model |", "|---|---|---|"]
    for raw, v, winner in per_record:
        lines.append(f"| `{raw}` | {v} | {winner} |")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[:22]))
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
