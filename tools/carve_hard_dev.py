"""Carve the hard-class dev holdout out of the extended corpus (G2B-U3).

The existing dev holdout is drawn from exactly-aligned rows -- the easy 55%
-- which is why v36 scored +0.900 there while sitting at parity on gold-2.
This one is drawn only from the extended ladder's rungs: omitted suffixes,
near-matches, recipient prefixes, no-number rows, canonical variants. It is
the surface that can actually see the classes gold-2 kept punishing.

Same one-shot discipline as the first carve: rows are physically removed
from the training corpus, disjointness is asserted a second way by
normalized identity, and the script refuses to run twice.

Usage: python tools/carve_hard_dev.py
"""

import collections
import json
import random
from pathlib import Path

ROOT = Path(__file__).parent.parent
CORPUS = ROOT / "training" / "corpus" / "realtext2.jsonl"
HOLDOUT = ROOT / "eval" / "realtext_hard_dev.jsonl"
MANIFEST = ROOT / "training" / "REALTEXT2_MANIFEST.json"
SEED = 20260817
N = 1500


def norm_identity(tokens):
    return " ".join("".join(ch for ch in t.upper() if ch.isalnum()) for t in tokens)


def rung_of(origin):
    # origins look like rt2-2e-MA
    parts = origin.split("-")
    return parts[1] if len(parts) > 2 else origin


def main():
    if HOLDOUT.exists():
        raise SystemExit(f"REFUSED: {HOLDOUT} already exists -- carved once, ever.")

    rows = [json.loads(l) for l in open(CORPUS, encoding="utf-8") if l.strip()]
    # Stratify by rung first (so the small rungs survive), then by state within rung.
    by_rung = collections.defaultdict(list)
    for i, r in enumerate(rows):
        by_rung[rung_of(r["origin"])].append(i)

    total = len(rows)
    quotas = {k: N * len(v) / total for k, v in by_rung.items()}
    alloc = {k: int(q) for k, q in quotas.items()}
    # Floor every rung at 40 rows where it has them, so 2d/2b are measurable at all.
    for k in alloc:
        alloc[k] = min(len(by_rung[k]), max(alloc[k], 40))
    # Trim/extend the largest rung to land exactly on N.
    big = max(alloc, key=lambda k: alloc[k])
    alloc[big] += N - sum(alloc.values())

    rng = random.Random(SEED)
    picked = set()
    for k in sorted(by_rung):
        picked.update(rng.sample(by_rung[k], alloc[k]))
    assert len(picked) == N, (len(picked), alloc)

    import usaddress
    held, kept = [], []
    for i, r in enumerate(rows):
        if i in picked:
            raw = " ".join(r["tokens"])
            assert usaddress.tokenize(raw) == r["tokens"], f"round-trip fail: {raw}"
            held.append({"raw": raw, **r})
        else:
            kept.append(r)

    overlap = {norm_identity(r["tokens"]) for r in held} & {norm_identity(r["tokens"]) for r in kept}
    assert not overlap, f"identity overlap holdout<->training: {len(overlap)}"

    with open(HOLDOUT, "w", encoding="utf-8") as f:
        for r in held:
            f.write(json.dumps(r) + "\n")
    with open(CORPUS, "w", encoding="utf-8") as f:
        for r in kept:
            f.write(json.dumps(r) + "\n")

    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    m["hard_dev_holdout"] = {
        "file": "eval/realtext_hard_dev.jsonl", "rows": N, "seed": SEED,
        "carved": "2026-08-16", "training_rows_after_carve": len(kept),
        "stratification": "proportional by rung with a 40-row floor, random within rung",
        "per_rung": {k: alloc[k] for k in sorted(alloc)},
    }
    MANIFEST.write_text(json.dumps(m, indent=1), encoding="utf-8")

    print(f"hard dev holdout: {len(held)} rows -> {HOLDOUT}")
    print(f"  per rung: {dict(sorted(alloc.items()))}")
    print(f"training corpus rewritten: {len(kept)} rows (was {total})")


if __name__ == "__main__":
    main()
