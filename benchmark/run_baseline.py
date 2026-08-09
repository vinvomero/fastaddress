"""usaddress baseline for the pre-build gate: single-core throughput + parse quality.

Reads benchmark/data/<county>.csv (from fetch_data.py) and measures, per dataset:
  - throughput: addresses/sec through usaddress.tag, single process, single thread
  - tag_fail: RepeatedLabelError rate (usaddress's explicit parse failure)
  - zip_miss: parsed ZipCode absent or != the source record's zip
  - no_addrnum: raw line starts with a digit but no AddressNumber was tagged
  - no_street: no StreetName tagged

Writes benchmark/results/baseline_usaddress.json with stats and anomaly examples.
"""

import csv
import json
import time
from pathlib import Path

import usaddress

DATA_DIR = Path(__file__).parent / "data"
RESULTS_DIR = Path(__file__).parent / "results"
EXAMPLE_CAP = 10


def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        return [(r["raw_address"], r["source_zip"]) for r in csv.DictReader(f)]


def run_dataset(name, rows):
    stats = {"n": len(rows), "tag_fail": 0, "zip_miss": 0, "no_addrnum": 0, "no_street": 0}
    examples = {"tag_fail": [], "zip_miss": [], "no_addrnum": [], "no_street": []}

    start = time.perf_counter()
    parses = []
    for raw, _zip in rows:
        try:
            parses.append(usaddress.tag(raw)[0])
        except usaddress.RepeatedLabelError:
            parses.append(None)
    elapsed = time.perf_counter() - start

    for (raw, src_zip), tags in zip(rows, parses):
        if tags is None:
            stats["tag_fail"] += 1
            if len(examples["tag_fail"]) < EXAMPLE_CAP:
                examples["tag_fail"].append(raw)
            continue
        zip_tag = tags.get("ZipCode", "")
        if not zip_tag or zip_tag[:5] != src_zip[:5]:
            stats["zip_miss"] += 1
            if len(examples["zip_miss"]) < EXAMPLE_CAP:
                examples["zip_miss"].append({"raw": raw, "parsed_zip": zip_tag})
        if raw[:1].isdigit() and "AddressNumber" not in tags:
            stats["no_addrnum"] += 1
            if len(examples["no_addrnum"]) < EXAMPLE_CAP:
                examples["no_addrnum"].append({"raw": raw, "tags": dict(tags)})
        if "StreetName" not in tags:
            stats["no_street"] += 1
            if len(examples["no_street"]) < EXAMPLE_CAP:
                examples["no_street"].append({"raw": raw, "tags": dict(tags)})

    stats["seconds"] = round(elapsed, 3)
    stats["per_sec"] = round(len(rows) / elapsed, 1)
    for k in ("tag_fail", "zip_miss", "no_addrnum", "no_street"):
        stats[f"{k}_pct"] = round(100.0 * stats[k] / len(rows), 2)
    return stats, examples


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    report = {"library": "usaddress", "version": usaddress.__version__ if hasattr(usaddress, "__version__") else "0.5.16"}
    for path in sorted(DATA_DIR.glob("*.csv")):
        rows = load(path)
        stats, examples = run_dataset(path.stem, rows)
        report[path.stem] = {"stats": stats, "examples": examples}
        print(
            f"{path.stem:10s} n={stats['n']}  {stats['per_sec']}/sec  "
            f"tag_fail={stats['tag_fail_pct']}%  zip_miss={stats['zip_miss_pct']}%  "
            f"no_addrnum={stats['no_addrnum_pct']}%  no_street={stats['no_street_pct']}%"
        )
    out = RESULTS_DIR / "baseline_usaddress.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"-> {out}")


if __name__ == "__main__":
    main()
