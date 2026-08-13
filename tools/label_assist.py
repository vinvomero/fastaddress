"""Gold-set candidate sampler and prelabeler (eval/PROTOCOL.md step 1).

Samples candidates per the protocol mix, prelabels each with the original
usaddress model, and writes eval/gold/candidates.jsonl with per-record status.
Records where the original crashes get status "needs_label"; everything else
starts as "prelabeled". Later passes (LLM review, human adjudication) update
status in place — only "adjudicated" records count toward gates.

Deterministic: fixed seed, sorted inputs.
"""

import csv
import json
import random
from pathlib import Path

import usaddress

ROOT = Path(__file__).parent.parent
DATA = ROOT / "benchmark" / "data"
OUT = ROOT / "eval" / "gold" / "candidates.jsonl"

TARGET = 1500
MIX = {"cook_mail": 900, "us_addrs_cases": 375, "nyc": 225}
SEED = 20260813


def load(name):
    with open(DATA / f"{name}.csv", newline="", encoding="utf-8") as f:
        return [r["raw_address"] for r in csv.DictReader(f)]


def prelabel(raw):
    try:
        parsed = usaddress.parse(raw)
        return [[tok, label] for tok, label in parsed], "prelabeled", None
    except Exception as e:  # RepeatedLabelError can't happen in parse(); belt+braces
        return None, "needs_label", type(e).__name__


def crash_in_tag(raw):
    try:
        usaddress.tag(raw)
        return False
    except usaddress.RepeatedLabelError:
        return True


def main():
    rng = random.Random(SEED)
    records = []
    for source, count in MIX.items():
        rows = sorted(set(load(source)))
        if source == "nyc":
            # Protocol: the NYC slice targets hard cases — prefer crash-class rows.
            crash_rows = [r for r in rows if crash_in_tag(r)]
            normal = [r for r in rows if r not in set(crash_rows)]
            take = crash_rows[:count] + rng.sample(normal, max(0, count - len(crash_rows)))
        else:
            take = rng.sample(rows, min(count, len(rows)))
        for raw in take:
            labels, status, err = prelabel(raw)
            records.append(
                {
                    "raw": raw,
                    "source": source,
                    "tag_crashes_original": crash_in_tag(raw),
                    "prelabel": labels,
                    "status": status,
                    "error": err,
                    "notes": "",
                }
            )
    rng.shuffle(records)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    n_crash = sum(1 for r in records if r["tag_crashes_original"])
    print(f"{len(records)} candidates -> {OUT} ({n_crash} crash-class)")


if __name__ == "__main__":
    main()
