"""U1: full failure taxonomy of the spent 20-county binding split.

The validation run cached no per-record outputs, so this tool re-derives the
split and REFUSES to classify until the regenerated divergence counters match
the recorded 2026-08-15 totals (candidate-right 1046, v1-right 378, both-wrong
758) -- a drifted reconstruction would silently classify a different record
set. If the current derivation path mismatches, the pre-city-filter variant is
tried too, and whichever matches is recorded in the report; matching neither is
a hard stop.

Outputs:
  benchmark/results/final_split_records.jsonl   per-record dump (raw, gold, v1, cand)
  benchmark/results/final-split-taxonomy.md     ranked class table with exemplars

Usage: python benchmark/taxonomy_final_split.py
"""

import collections
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "training"))
sys.path.insert(0, str(Path(__file__).parent))
import build_tiger_corpus as btc

btc.CACHE = Path("C:/cargo-target/us-address-parser/tiger_final_cache")
from final_validation import HOLDOUT, PER_COUNTY  # noqa: E402
from national_scan import tag  # noqa: E402

ROOT = Path(__file__).parent.parent
OUT_DIR = ROOT / "benchmark" / "results"
CANDIDATE = "model/usaddr_v31.crfsuite"
RECORDED = {"cand_right": 1046, "v1_right": 378, "both_wrong": 758}
SEED = 20260815


def build_rows(city_filter):
    rng = random.Random(SEED)
    rows, place = [], {}
    for sf, cf, ab in HOLDOUT:
        try:
            if sf not in place:
                place[sf] = btc.load_places(sf)
            got, _ = btc.county_rows(sf, cf, ab, PER_COUNTY, rng, place[sf])
        except Exception as e:
            print(f"  {ab}: skipped ({type(e).__name__})", flush=True)
            continue
        for r in got:
            if city_filter:
                city = [t for t, l in zip(r["tokens"], r["labels"]) if l == "PlaceName"]
                if not (city and all(t.isalpha() for t in city)):
                    continue
            rows.append({"tokens": r["tokens"], "labels": r["labels"], "state": ab})
    return rows


def score(rows):
    raws = [" ".join(r["tokens"]) for r in rows]
    v1 = tag(raws)
    cand = tag(raws, CANDIDATE)
    res = collections.Counter()
    records = []
    for i, r in enumerate(rows):
        if v1[i]["labels"] == cand[i]["labels"] or v1[i]["tokens"] != r["tokens"]:
            continue
        g = r["labels"]
        k = ("cand_right" if cand[i]["labels"] == g
             else "v1_right" if v1[i]["labels"] == g
             else "both_wrong")
        res[k] += 1
        records.append({"raw": raws[i], "state": r["state"], "bucket": k,
                        "gold": g, "v1": v1[i]["labels"], "cand": cand[i]["labels"]})
    return res, records


def norm_token(t):
    t = t.rstrip(",").lower()
    return "#" if t.isdigit() else t


def signature(rec, against):
    """Label-diff signature for clustering: (norm_token, gold_label, wrong_label)
    tuples for every mismatched position, order-preserving."""
    wrong = rec[against]
    parts = []
    for tok, g, w in zip(rec["raw"].split(), rec["gold"], wrong):
        if g != w:
            parts.append(f"{norm_token(tok)}|{g.replace('StreetName','SN')}>{w.replace('StreetName','SN')}")
    return "; ".join(parts)[:120]


def cluster(records, bucket, against):
    groups = collections.defaultdict(list)
    for r in records:
        if r["bucket"] != bucket:
            continue
        # Coarse signature: the LABEL-PAIR set generalizes across specific
        # tokens; the fine signature keeps tokens for exemplar reading.
        pairs = tuple(sorted({(g.replace("StreetName", "SN"), w.replace("StreetName", "SN"))
                              for g, w in zip(r["gold"], r[against]) if g != w}))
        groups[pairs].append(r)
    return sorted(groups.items(), key=lambda kv: -len(kv[1]))


def main():
    for variant, use_filter in (("current (city-filtered)", True), ("pre-filter", False)):
        print(f"deriving split: {variant} ...", flush=True)
        rows = build_rows(use_filter)
        res, records = score(rows)
        got = {k: res[k] for k in RECORDED}
        print(f"  totals {got} vs recorded {RECORDED}", flush=True)
        if got == RECORDED:
            matched = variant
            break
    else:
        raise SystemExit("HARD STOP: neither derivation variant reproduces the recorded totals; "
                         "the split cannot be trusted for taxonomy. Investigate before classifying.")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / "final_split_records.jsonl", "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")

    lines = ["# Final-split failure taxonomy (U1)", "",
             f"Derivation variant matching recorded totals: **{matched}**. "
             f"Counters asserted equal to the 2026-08-15 run before classification: "
             f"{RECORDED}.", ""]
    total_named = {"cand_right_v1_wrong_irrelevant": 0}
    for bucket, against, title in (("v1_right", "cand", "Candidate-wrong (v1 was right)"),
                                   ("both_wrong", "cand", "Both-wrong (candidate side)")):
        clusters = cluster(records, bucket, against)
        n_bucket = sum(len(v) for _, v in clusters)
        named = sum(len(v) for _, v in clusters if len(v) >= 3)
        lines += [f"## {title} — {n_bucket} records, "
                  f"{named} ({named/max(n_bucket,1)*100:.1f}%) in classes of ≥3", ""]
        lines += ["| # | count | states | label-pair signature | exemplar |", "|---|---|---|---|---|"]
        for i, (pairs, recs) in enumerate(clusters[:25], 1):
            states = collections.Counter(r["state"] for r in recs)
            st = ",".join(f"{s}:{n}" for s, n in states.most_common(3))
            sig = "; ".join(f"{g}→{w}" for g, w in pairs)[:60]
            ex = recs[0]
            fine = signature(ex, against)
            lines.append(f"| {i} | {len(recs)} | {st} | `{sig}` | `{ex['raw'][:44]}` — {fine[:60]} |")
        lines.append("")

    (OUT_DIR / "final-split-taxonomy.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"-> {OUT_DIR / 'final-split-taxonomy.md'}", flush=True)


if __name__ == "__main__":
    main()
