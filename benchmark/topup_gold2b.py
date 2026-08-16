#!/usr/bin/env python3
"""Gold-2b strict-cohort top-up to satisfy the 2,900 size floor.

Per the 2026-08-16 human ruling recorded in eval/gold2/PROTOCOL2.md ("Size floor
repair, before any scoring: the strict cohort is topped up from its own
already-approved sources to >=2,900 records (~91/state, robust to a TX drop) —
more data from approved sources, nothing reweighted, nothing removed") and the
pass-through fidelity outcome documented in eval/gold2b/FIDELITY_CHECKS.md
(WA FAIL -> WA records dropped and excluded from the top-up; AL/LA/TX/MS PASS).

Mechanics:
- Strict cohort: the 33 pre-registered strict states minus fidelity failures.
  Sensitivity states (WI/WV/MN aggregate-lineage; FL/GA/MA/MT/NC/NJ
  same-lineage) are NOT touched: their 73 records stay exactly as fetched.
- Per strict state: the 73 in-set records are preserved byte-for-byte; the
  12 already-fetched, already-deduped checkpoint spares (85 kept - 73 trimmed)
  are added first; the remainder comes from fresh seeded windows on the SAME
  approved endpoint/config (fetch_gold2b.CONFIG unchanged), deduped by
  normalized identity against gold-1, gold-2, clean, realtext training corpus,
  realtext dev holdout, every gold-2b checkpoint record, and everything added
  during this top-up.
- Top-up RNG: random.Random(f"20260819-topup-{state}") — deterministic,
  distinct from the build seed windows.
- Top-up fetch logs/checkpoints: gold2b_cache/checkpoints_topup/<ST>.json
  (kept out of checkpoints/ so fetch_gold2b --assemble is not confused).

Usage:
  python benchmark/topup_gold2b.py --run      # fetch + rewrite candidates.jsonl
  python benchmark/topup_gold2b.py --dry      # report plan only
"""
import json
import random
import sys
from collections import OrderedDict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fetch_gold2b as fg

TARGET = 91
BASE_N = 73

STRICT = ["AK", "AL", "AR", "AZ", "CO", "DE", "HI", "IA", "IL", "IN", "LA",
          "MD", "MI", "MO", "MS", "ND", "NE", "NM", "NV", "NY", "OH", "OK",
          "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "WA", "WY"]
LINEAGE_SENSITIVITY = ["FL", "GA", "MA", "MT", "NC", "NJ"]
AGGREGATE_SENSITIVITY = ["WI", "WV", "MN"]
# Fidelity outcome (eval/gold2b/FIDELITY_CHECKS.md, this session):
FIDELITY = {"AL": "PASS", "LA": "PASS", "TX": "PASS", "MS": "PASS", "WA": "FAIL"}
DROPPED = [s for s, v in FIDELITY.items() if v == "FAIL"]

TOPUP_CKPT = fg.CACHE / "checkpoints_topup"


def load_candidates():
    by_state = OrderedDict()
    with open(fg.CANDIDATES_OUT, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            by_state.setdefault(rec["state"], []).append(rec)
    return by_state


def all_checkpoint_identities():
    ids = set()
    for p in fg.CKPT_DIR.glob("*.json"):
        with open(p, encoding="utf-8") as f:
            for rec in json.load(f).get("records", []):
                ids.add(fg.norm_identity(rec["raw"]))
    return ids


def spares_for(state, in_set_ids):
    with open(fg.CKPT_DIR / f"{state}.json", encoding="utf-8") as f:
        ck = json.load(f)
    return [r for r in ck.get("records", [])
            if fg.norm_identity(r["raw"]) not in in_set_ids]


def fetch_more(state, need, excl_sets, global_ids, log):
    """Fresh seeded windows on the same approved source; returns new records."""
    cfg = dict(fg.CONFIG[state])
    cfg["_state"] = state
    rng = random.Random(f"{fg.SEED}-topup-{state}")
    new, removed = [], {k: 0 for k in list(excl_sets) + ["gold2b-existing"]}
    rows_pulled = 0
    for attempt, want in enumerate((need * 5, need * 12, need * 30), 1):
        try:
            if cfg.get("aggregate"):
                rows, _total = fg.fetch_aggregate(cfg, rng, want, log)
            else:
                rows, _total = fg.fetch_arcgis(cfg, rng, want, log)
        except Exception as e:  # noqa: BLE001
            log.append(f"attempt {attempt} fetch error: {str(e)[:200]}")
            continue
        rows_pulled += len(rows)
        rng.shuffle(rows)
        for row in rows:
            raw = fg.build_raw(cfg, row)
            if not raw or not fg.plausible(raw, cfg, row):
                continue
            nid = fg.norm_identity(raw)
            hit = None
            for name, s in excl_sets.items():
                if nid in s:
                    hit = name
                    break
            if hit is None and nid in global_ids:
                hit = "gold2b-existing"
            if hit:
                removed[hit] += 1
                continue
            global_ids.add(nid)
            new.append({"raw": raw, "state": state, "source": cfg["source"],
                        "dataset": cfg["dataset"], "fetched": fg.FETCH_DATE})
            if len(new) >= need:
                break
        if len(new) >= need:
            break
        log.append(f"attempt {attempt}: have {len(new)}/{need} after dedupe, widening")
    return new, removed, rows_pulled


def main():
    dry = "--dry" in sys.argv
    by_state = load_candidates()
    strict_live = [s for s in STRICT if s not in DROPPED]
    excl_sets = fg.load_exclusion_sets()
    global_ids = all_checkpoint_identities()
    for recs in by_state.values():
        for r in recs:
            global_ids.add(fg.norm_identity(r["raw"]))

    TOPUP_CKPT.mkdir(parents=True, exist_ok=True)
    report = []
    for state in strict_live:
        existing = by_state.get(state, [])
        assert len(existing) == BASE_N, f"{state}: expected {BASE_N} in set"
        in_ids = {fg.norm_identity(r["raw"]) for r in existing}
        spares = spares_for(state, in_ids)
        need_after_spares = TARGET - len(existing) - len(spares)
        log = []
        if dry:
            report.append((state, len(existing), len(spares), need_after_spares, 0, {}))
            continue
        for r in spares:
            global_ids.add(fg.norm_identity(r["raw"]))
        new, removed, rows_pulled = ([], {}, 0)
        if need_after_spares > 0:
            print(f"[{state}] fetching {need_after_spares} net-new ...")
            new, removed, rows_pulled = fetch_more(state, need_after_spares,
                                                   excl_sets, global_ids, log)
        added = spares + new
        added = added[: TARGET - len(existing)]
        by_state[state] = existing + added
        shortfall = TARGET - len(by_state[state])
        (TOPUP_CKPT / f"{state}.json").write_text(json.dumps({
            "state": state, "target": TARGET, "existing": len(existing),
            "spares_used": len(spares), "new_fetched": len(new),
            "rows_pulled": rows_pulled, "dedupe_removed": removed,
            "fetch_log": log, "shortfall": shortfall,
            "records_added": added,
        }, ensure_ascii=False, indent=1), encoding="utf-8")
        report.append((state, len(existing), len(spares), len(new), shortfall, removed))
        print(f"[{state}] {len(existing)}+{len(spares)} spares+{len(new)} new "
              f"= {len(by_state[state])}" + (f" SHORTFALL {shortfall}" if shortfall else ""))

    if dry:
        for r in report:
            print(r)
        return

    # drop fidelity-failed states, keep sensitivity states untouched
    order = [s for s in by_state if s not in DROPPED]
    n = 0
    with open(fg.CANDIDATES_OUT, "w", encoding="utf-8") as f:
        for state in order:
            for rec in by_state[state]:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                n += 1
    strict_total = sum(len(by_state[s]) for s in strict_live)
    sens_total = sum(len(by_state[s]) for s in LINEAGE_SENSITIVITY + AGGREGATE_SENSITIVITY)
    print(f"\nWrote {n} records -> {fg.CANDIDATES_OUT}")
    print(f"strict cohort: {len(strict_live)} states, {strict_total} records "
          f"(floor 2900: {'MET' if strict_total >= 2900 else 'NOT MET'})")
    print(f"sensitivity states untouched: {sens_total} records; dropped: {DROPPED}")

    cohorts = {
        "strict": strict_live,
        "lineage_sensitivity": LINEAGE_SENSITIVITY,
        "aggregate_sensitivity": AGGREGATE_SENSITIVITY,
        "wy_amendment": ["WY"],
        "fidelity": FIDELITY,
        "strict_total": strict_total,
        "grand_total": n,
    }
    out = fg.GOLD2B_DIR / "COHORTS.json"
    out.write_text(json.dumps(cohorts, indent=2) + "\n", encoding="utf-8")
    print(f"Cohorts -> {out}")


if __name__ == "__main__":
    main()
