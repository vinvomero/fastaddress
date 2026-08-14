"""Round-3 adjudication doc: only the records with no verdict yet.

Earlier rounds matched by disagreement SHAPE, which grew tangled once verdicts
spanned two rounds and two candidate models. This builds the worklist by RAW
ADDRESS instead — a record either has a verdict already or it does not — which
is unambiguous and cannot mis-map.

Blinding is preserved (models shown as A/B, key written to disk). Census
evidence is attached where the geocoder matched.

Usage: python tools/make_round3_doc.py
"""

import json
import random
from pathlib import Path

ROOT = Path(__file__).parent.parent
G = ROOT / "eval" / "gold"
OUT = G / "ADJUDICATION-round3.md"
KEY = G / "blind_key-round3.json"
SEED = 20260814


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))


def sig(r):
    return tuple((d["v1"], d["v2"]) for d in r["differing_tokens"])


def adjudicated_addresses():
    """Every raw address that already carries a verdict, from both rounds."""
    from collections import defaultdict

    done = {}
    # Round 1: group verdicts over the archived disagreement set
    rows = [json.loads(l) for l in open(G / "disagreements-prior.jsonl", encoding="utf-8-sig") if l.strip()]
    key = load(G / "blind_key-prior.json")
    verd = load(G / "verdicts-chatgpt-2026-08-13.json")
    exc = verd.get("exceptions", {})
    groups = defaultdict(list)
    for r in rows:
        groups[sig(r)].append(r)
    for i, grp in enumerate(sorted(groups.values(), key=len, reverse=True), 1):
        gl = verd["groups"].get(str(i))
        for r in grp:
            letter = exc.get(r["raw"], gl)
            if letter:
                done[r["raw"]] = key.get(letter, letter)
    # Round 2: explicit per-address verdicts
    r2 = load(G / "verdicts-round2-2026-08-14.json")
    k2 = load(G / "blind_key.json")
    for addr, letter in r2.get("addresses", {}).items():
        done[addr] = k2.get(letter, letter)
    return done


def main():
    rng = random.Random(SEED)
    rows = [json.loads(l) for l in open(G / "disagreements.jsonl", encoding="utf-8") if l.strip()]
    done = adjudicated_addresses()
    todo = [r for r in rows if r["raw"] not in done]

    a_is_v1 = rng.random() < 0.5
    KEY.write_text(
        json.dumps({"A": "v1" if a_is_v1 else "v2", "B": "v2" if a_is_v1 else "v1"}, indent=1),
        encoding="utf-8",
    )
    census = {}
    cp = G / "census_evidence.json"
    if cp.exists():
        census = load(cp)

    out = [
        f"# Adjudication round 3 — {len(todo)} addresses",
        "",
        f"The candidate now differs from the incumbent on {len(rows)} of 1,500 messy addresses. "
        f"**{len(rows) - len(todo)} already have your verdicts** and are excluded. These "
        f"{len(todo)} are the ones never judged.",
        "",
        "Models are blinded as **A** and **B** (the key is re-rolled each round and written to the "
        "repo). Judge which parse is *correct*. Answer **A**, **B**, **neither**, or **skip**.",
        "",
        "---",
        "",
    ]
    for i, r in enumerate(todo, 1):
        out.append(f"## {i}. `{r['raw']}`")
        out.append("")
        ev = census.get(r["raw"])
        if ev and ev.get("status") == "match":
            city = (ev.get("city") or "")
            flag = " ⚠️ *(resolved to a city not in the input — treat with suspicion)*" if city and city.upper() not in r["raw"].upper() else ""
            out.append(
                f"*Census:* {ev.get('matched')} — street **{ev.get('street')}**, "
                f"type `{ev.get('suffix_type')}`, city **{city}**{flag}"
            )
            out.append("")
        out.append("| Token | Model A | Model B |")
        out.append("|---|---|---|")
        for d in r["differing_tokens"]:
            a = d["v1"] if a_is_v1 else d["v2"]
            b = d["v2"] if a_is_v1 else d["v1"]
            out.append(f"| `{d['token']}` | {a} | {b} |")
        out.append("")
        out.append("**Verdict:** _____")
        out.append("")
        out.append("---")
        out.append("")

    out += [
        "## When you're done",
        "",
        "Tell the agent. It will un-blind, fold these into the running tally, and report whether the "
        "candidate is clean across every adjudicated record — the last evidence gap before a ship "
        "decision.",
    ]
    OUT.write_text("\n".join(out), encoding="utf-8")
    print(f"{len(todo)} unadjudicated records -> {OUT}")


if __name__ == "__main__":
    main()
