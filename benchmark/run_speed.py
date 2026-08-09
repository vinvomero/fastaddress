"""Three-way speed benchmark per plan R4/R5/R8.

Measures, over all benchmark datasets combined:
  1. usaddress single-core (Python, compat tag loop)         <- baseline
  2. usaddr wheel single-core (same loop through the binding) <- like-for-like headline
  3. native Rust single-core (bench_native binary)
  4. multi-core: multiprocessing usaddress vs threaded native Rust

Writes benchmark/results/speed_report.md and prints the go/no-go verdict
against the >=10x single-core bar.

Usage: python benchmark/run_speed.py [--bench-bin PATH]
"""

import argparse
import csv
import json
import multiprocessing
import os
import subprocess
import sys
import time
from importlib.metadata import version
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
RESULTS_DIR = Path(__file__).parent / "results"
BAR = 10.0


def load_rows():
    rows = []
    for csv_path in sorted(DATA_DIR.glob("*.csv")):
        with open(csv_path, newline="", encoding="utf-8") as f:
            rows += [r["raw_address"] for r in csv.DictReader(f)]
    return rows


def usaddress_worker(raw):
    import usaddress

    try:
        usaddress.tag(raw)
    except usaddress.RepeatedLabelError:
        pass
    return None


def time_python_loop(tag_fn, error_cls, rows):
    start = time.perf_counter()
    for raw in rows:
        try:
            tag_fn(raw)
        except error_cls:
            pass
    return time.perf_counter() - start


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bench-bin",
        default=os.environ.get("BENCH_NATIVE", str(Path("target/release/bench_native.exe"))),
    )
    args = parser.parse_args()

    import usaddr
    import usaddress

    rows = load_rows()
    n = len(rows)
    cores = os.cpu_count() or 1
    print(f"{n} rows, {cores} logical cores")

    # Warm-up both taggers
    usaddress.tag("123 Main St Springfield IL 62704")
    usaddr.tag("123 Main St Springfield IL 62704")

    # Alternate sides across three rounds and keep each side's best, so
    # monotonic machine-load drift penalizes neither parser systematically.
    py_secs, rs_secs = float("inf"), float("inf")
    for _ in range(3):
        py_secs = min(py_secs, time_python_loop(usaddress.tag, usaddress.RepeatedLabelError, rows))
        rs_secs = min(rs_secs, time_python_loop(usaddr.tag, usaddr.RepeatedLabelError, rows))
    py_rate = n / py_secs
    rs_rate = n / rs_secs
    print(f"usaddress single-core (best of 3):    {py_rate:,.0f}/sec ({py_secs:.1f}s)")
    print(f"usaddr wheel single-core (best of 3): {rs_rate:,.0f}/sec ({rs_secs:.1f}s)")

    # Native side runs over the SAME full corpus (every dataset CSV), aggregated.
    env = {**os.environ, "BENCH_STAGE": "full"}
    native = {}
    for threads in (1, cores):
        total_rows, total_secs = 0, 0.0
        for csv_path in sorted(DATA_DIR.glob("*.csv")):
            out = subprocess.run(
                [args.bench_bin, str(csv_path), str(threads)],
                capture_output=True, text=True, check=True, env=env,
            )
            r = json.loads(out.stdout)
            total_rows += r["rows"]
            total_secs += r["secs"]
        native[threads] = total_rows / total_secs
    native_rate_1 = native[1]
    native_rate_n = native[cores]
    print(f"native Rust single-core:  {native_rate_1:,.0f}/sec")
    print(f"native Rust {cores} threads:   {native_rate_n:,.0f}/sec")

    with multiprocessing.Pool(cores) as pool:
        # Warm up: worker spawn + per-worker usaddress model load stay outside
        # the timed window, matching the native side's pre-warmed model.
        pool.map(usaddress_worker, rows[:400], chunksize=50)
        start = time.perf_counter()
        pool.map(usaddress_worker, rows, chunksize=200)
        mp_secs = time.perf_counter() - start
    mp_rate = n / mp_secs
    print(f"usaddress {cores} processes:   {mp_rate:,.0f}/sec ({mp_secs:.1f}s)")

    like_for_like = rs_rate / py_rate
    native_mult = native_rate_1 / py_rate
    mc_mult = native_rate_n / mp_rate
    verdict = "PASS" if like_for_like >= BAR else "FAIL"

    RESULTS_DIR.mkdir(exist_ok=True)
    report = f"""# Speed Report — three-way benchmark

Corpus: {n} addresses (all benchmark datasets). Machine: {cores} logical cores.
usaddress {version('usaddress')} (python-crfsuite), usaddr wheel 0.1.0 (Rust, same model).

| Configuration | Addresses/sec | Multiplier vs baseline |
|---|---|---|
| usaddress, single core (baseline) | {py_rate:,.0f} | 1.0x |
| **usaddr wheel, single core (like-for-like)** | {rs_rate:,.0f} | **{like_for_like:.1f}x** |
| native Rust, single core | {native_rate_1:,.0f} | {native_mult:.1f}x |
| usaddress, {cores} processes (multiprocessing) | {mp_rate:,.0f} | {mp_rate / py_rate:.1f}x |
| native Rust, {cores} threads | {native_rate_n:,.0f} | {native_rate_n / py_rate:.1f}x |

Multi-core like-for-like (native {cores}-thread vs usaddress {cores}-process): {mc_mult:.1f}x

Go/no-go vs the >=10x single-core bar: **{verdict}** ({like_for_like:.1f}x)

Both parsers ran the identical compat workload: `tag()` over every row, catching
RepeatedLabelError. Reproduce: `python benchmark/run_speed.py`.
"""
    (RESULTS_DIR / "speed_report.md").write_text(report, encoding="utf-8")
    print(f"-> {RESULTS_DIR / 'speed_report.md'}")
    print(f"GO/NO-GO ({BAR:.0f}x bar): {verdict} — like-for-like {like_for_like:.1f}x")
    sys.exit(0 if verdict == "PASS" else 1)


if __name__ == "__main__":
    main()
