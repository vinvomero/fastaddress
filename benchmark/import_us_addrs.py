"""Import the us-addrs project's test address files as a parity dataset.

Downloads the two raw address lists from raphaellaude/us-addrs (MIT-adjacent
prior art credited in the README) and writes benchmark/data/us_addrs_cases.csv
in the standard benchmark shape. These are the documented hard cases a prior
Rust port mistagged — required regression data per plan R3.
"""

import csv
import urllib.request
from pathlib import Path

URLS = [
    "https://raw.githubusercontent.com/raphaellaude/us-addrs/main/tests/test_data/test_addrs.txt",
    "https://raw.githubusercontent.com/raphaellaude/us-addrs/main/tests/test_data/us50.test.raw",
]

OUT = Path(__file__).parent / "data" / "us_addrs_cases.csv"


def main():
    rows = []
    for url in URLS:
        with urllib.request.urlopen(url, timeout=60) as resp:
            text = resp.read().decode("utf-8")
        rows += [line.strip() for line in text.splitlines() if line.strip()]
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["raw_address", "source_zip"])
        for r in rows:
            w.writerow([r, ""])
    print(f"wrote {len(rows)} rows -> {OUT}")


if __name__ == "__main__":
    main()
