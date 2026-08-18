"""Build a value-ordered human-labeling candidate list (V19-line, real-data path).

The gold-2c archaeology showed the only route to a v2 that beats DataMade's
model is more of what made that model good: real, human-labeled free text --
especially the classes where the current models diverge from reality
(suffix-present streets above all).

This does NOT fetch. It draws from the 299,832 owner-mail rows already pulled
into the realtext cache, reconstructs each full free-text address, drops any
that collide by normalized identity with gold-1/2/2b/2c, prelabels each with
the shipping model AND its per-token confidence, and orders the list so the
records the model is least sure about come first. A human reviews top-down --
confirm the prelabel or correct it -- and every reviewed record is one the
model genuinely needs. Label as far down as the budget allows; the ordering
means early effort counts most.

Output: training/humanlabel/candidates_for_labeling.jsonl (ordered),
        training/humanlabel/LABELSET_MANIFEST.json (stats + disjointness proof).
"""
import collections
import glob
import gzip
import json
import os
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE = "C:/cargo-target/us-address-parser/realtext_cache/checkpoints"
OUT = Path(__file__).parent / "candidates_for_labeling.jsonl"
MANIFEST = Path(__file__).parent / "LABELSET_MANIFEST.json"
SEED = 20260824
POOL_TARGET = 5000   # ordered candidates to emit; human labels as far as budget allows

import fastaddress  # shipping model, for prelabel + confidence


def norm(s):
    return " ".join("".join(c for c in t.upper() if c.isalnum()) for t in s.split())


def load_eval_identities():
    ids = set()
    for f in ["eval/gold/candidates.jsonl", "eval/gold2/candidates.jsonl",
              "eval/gold2b/candidates.jsonl", "eval/gold2c/candidates.jsonl"]:
        p = ROOT / f
        if p.exists():
            for line in open(p, encoding="utf-8-sig"):
                line = line.strip()
                if line:
                    ids.add(norm(json.loads(line)["raw"]))
    return ids


def reconstruct(row):
    lines = [l.strip() for l in row.get("lines", []) if l and l.strip()]
    tail = " ".join(x for x in [row.get("city", ""), row.get("st", ""), row.get("zip", "")] if x)
    return " ".join(lines + ([tail] if tail else [])).strip()


def klass(labels):
    ls = set(labels)
    if "Recipient" in ls:
        return "recipient"
    if ls & {"USPSBoxType", "USPSBoxGroupType"}:
        return "box"
    if "StreetNamePostType" in ls:
        return "suffix-present"
    if "StreetName" in ls:
        return "suffix-omitted"
    return "other"


def main():
    eval_ids = load_eval_identities()
    rng = random.Random(SEED)
    pool, seen = [], set()
    for f in sorted(glob.glob(f"{CACHE}/*.json.gz")):
        st = os.path.basename(f)[:-8]
        with gzip.open(f, "rt", encoding="utf-8") as fh:
            d = json.load(fh)
        rows = d.get("rows", []) if isinstance(d, dict) else d
        for r in rows:
            if not isinstance(r, dict):
                continue
            raw = reconstruct(r)
            if len(raw.split()) < 3:
                continue
            nid = norm(raw)
            if nid in eval_ids or nid in seen:
                continue
            seen.add(nid)
            pool.append((raw, st))
    print(f"pool after dedup vs eval + self: {len(pool):,}")
    rng.shuffle(pool)
    draw = pool[: POOL_TARGET * 3]
    scored = []
    for raw, st in draw:
        try:
            triples = fastaddress.parse_with_confidence(raw)
        except Exception:
            continue
        if not triples:
            continue
        toks = [t for t, _, _ in triples]
        labs = [l for _, l, _ in triples]
        min_conf = min(c for _, _, c in triples)
        scored.append({"raw": raw, "state": st, "prelabel_tokens": toks,
                       "prelabel_labels": labs, "min_confidence": round(min_conf, 5),
                       "class": klass(labs)})
        if len(scored) >= POOL_TARGET:
            break
    scored.sort(key=lambda r: r["min_confidence"])
    with open(OUT, "w", encoding="utf-8") as f:
        for r in scored:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    by_class = collections.Counter(r["class"] for r in scored)
    conf_bands = collections.Counter(
        ("<0.90" if r["min_confidence"] < 0.90 else
         "0.90-0.99" if r["min_confidence"] < 0.99 else ">=0.99") for r in scored)
    MANIFEST.write_text(json.dumps({
        "built": "2026-08-18", "seed": SEED, "records": len(scored),
        "source": "realtext_cache raw pool (299,832 fetched owner-mail rows), no new fetch",
        "disjoint_from": ["gold-1", "gold-2", "gold-2b", "gold-2c"],
        "ordering": "ascending weakest-token confidence (most informative first)",
        "class_mix": dict(by_class), "confidence_bands": dict(conf_bands),
        "states": sorted(set(r["state"] for r in scored)),
    }, indent=1), encoding="utf-8")
    print(f"wrote {len(scored):,} ordered candidates -> {OUT}")
    print("class mix:", dict(by_class))
    print("confidence bands:", dict(conf_bands))


if __name__ == "__main__":
    main()
