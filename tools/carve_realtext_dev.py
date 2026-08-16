"""Carve the real-text dev holdout out of the training corpus (RT-U2).

Draws a seeded, state-stratified 2,000-row sample from
training/corpus/realtext.jsonl, writes it to eval/realtext_dev.jsonl
(committed), and REWRITES the training corpus without those rows — the
holdout is physically absent from anything training can read, not merely
flagged. Disjointness is then asserted a second way, by normalized
identity, so a duplicate row slipping through would fail the build.

Runs once. Refuses to run if eval/realtext_dev.jsonl already exists —
re-carving after training has seen the corpus would poison the holdout.

Usage: python tools/carve_realtext_dev.py
"""

import collections
import json
import random
from pathlib import Path

ROOT = Path(__file__).parent.parent
CORPUS = ROOT / "training" / "corpus" / "realtext.jsonl"
HOLDOUT = ROOT / "eval" / "realtext_dev.jsonl"
MANIFEST = ROOT / "training" / "REALTEXT_MANIFEST.json"
SEED = 20260818
N = 2000


def norm_identity(tokens):
    return " ".join("".join(ch for ch in t.upper() if ch.isalnum()) for t in tokens)


def main():
    if HOLDOUT.exists():
        raise SystemExit(f"REFUSED: {HOLDOUT} already exists — the holdout is carved once, ever.")

    rows = [json.loads(l) for l in open(CORPUS, encoding="utf-8") if l.strip()]
    by_state = collections.defaultdict(list)
    for i, r in enumerate(rows):
        by_state[r["origin"]].append(i)

    total = len(rows)
    # Largest-remainder proportional allocation to exactly N.
    quotas = {s: N * len(ix) / total for s, ix in by_state.items()}
    alloc = {s: int(q) for s, q in quotas.items()}
    for s, _ in sorted(quotas.items(), key=lambda kv: kv[1] - int(kv[1]), reverse=True):
        if sum(alloc.values()) >= N:
            break
        alloc[s] += 1

    rng = random.Random(SEED)
    picked = set()
    for s in sorted(by_state):
        picked.update(rng.sample(by_state[s], alloc[s]))
    assert len(picked) == N, len(picked)

    import usaddress
    held, kept = [], []
    for i, r in enumerate(rows):
        if i in picked:
            raw = " ".join(r["tokens"])
            assert usaddress.tokenize(raw) == r["tokens"], f"round-trip fail: {raw}"
            held.append({"raw": raw, **r})
        else:
            kept.append(r)

    held_ids = {norm_identity(r["tokens"]) for r in held}
    kept_ids = {norm_identity(r["tokens"]) for r in kept}
    overlap = held_ids & kept_ids
    assert not overlap, f"identity overlap holdout<->training: {len(overlap)}"

    with open(HOLDOUT, "w", encoding="utf-8") as f:
        for r in held:
            f.write(json.dumps(r) + "\n")
    with open(CORPUS, "w", encoding="utf-8") as f:
        for r in kept:
            f.write(json.dumps(r) + "\n")

    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    m["dev_holdout"] = {"file": "eval/realtext_dev.jsonl", "rows": N, "seed": SEED,
                       "carved": "2026-08-15", "training_rows_after_carve": len(kept),
                       "stratification": "proportional by state, largest remainder",
                       "per_state": {s: alloc[s] for s in sorted(alloc)}}
    m["total_rows"] = len(kept)
    MANIFEST.write_text(json.dumps(m, indent=1), encoding="utf-8")

    states = collections.Counter(r["origin"] for r in held)
    print(f"holdout: {len(held)} rows, {len(states)} states -> {HOLDOUT}")
    print(f"training corpus rewritten: {len(kept)} rows (was {total})")


if __name__ == "__main__":
    main()
