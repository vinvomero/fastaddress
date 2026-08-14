"""Score round-2 adjudication (fresh groups only) and report the combined picture.

Group numbers in the round-2 doc index the FRESH groups (those not carried
forward), not the full ordered group list — scoring must rebuild the same split
the doc generator used or verdicts land on the wrong records.
"""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent
G = ROOT / "eval" / "gold"

def sig(r): return tuple((d["v1"], d["v2"]) for d in r["differing_tokens"])
def load(p, **kw): return json.loads(Path(p).read_text(encoding="utf-8-sig"), **kw)

rows = [json.loads(l) for l in open(G / "disagreements.jsonl", encoding="utf-8") if l.strip()]
key = load(G / "blind_key.json")
verd = load(G / "verdicts-round2-2026-08-14.json")
fresh_v = {int(k): v for k, v in verd["fresh_groups"].items()}

# Rebuild prior shapes exactly as the doc generator did
prior_key = load(G / "blind_key-prior.json")
prior_verd = load(G / "verdicts-chatgpt-2026-08-13.json")
pgv = {int(k): v for k, v in prior_verd["groups"].items()}
prows = [json.loads(l) for l in open(G / "disagreements-prior.jsonl", encoding="utf-8-sig") if l.strip()]
pg = defaultdict(list)
for r in prows: pg[sig(r)].append(r)
pordered = sorted(pg.values(), key=len, reverse=True)
prior = {}
for i, grp in enumerate(pordered, 1):
    letter = pgv.get(i)
    if letter: prior[sig(grp[0])] = prior_key.get(letter, letter)

groups = defaultdict(list)
for r in rows: groups[sig(r)].append(r)
ordered = sorted(groups.values(), key=len, reverse=True)
carried = [g for g in ordered if sig(g[0]) in prior]
fresh = [g for g in ordered if sig(g[0]) not in prior]

tally = {"v1": 0, "v2": 0, "neither": 0, "skip": 0}
fresh_tally = {"v1": 0, "v2": 0, "neither": 0, "skip": 0}
for i, grp in enumerate(fresh, 1):
    v = fresh_v.get(i, "skip")
    w = key.get(v, v)
    for _ in grp:
        tally[w] += 1; fresh_tally[w] += 1
for grp in carried:
    w = prior[sig(grp[0])]
    for _ in grp: tally[w] += 1

print(f"blind key this round: {key}")
print(f"fresh groups: {len(fresh)} ({sum(len(g) for g in fresh)} records) | carried: {len(carried)} ({sum(len(g) for g in carried)} records)")
print(f"\nFRESH (new shapes v12 introduced): {fresh_tally}")
print(f"COMBINED all {len(rows)} contested records: {tally}")
d = tally["v1"] + tally["v2"]
if d: print(f"decided head-to-head: v12 {tally['v2']}/{d} ({tally['v2']/d*100:.0f}%), v1 {tally['v1']}/{d} ({tally['v1']/d*100:.0f}%)")
