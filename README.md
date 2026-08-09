# us-address-parser (working name)

Benchmark-first build of a modern US address parser. Requirements: see the brainstorm
requirements doc (2026-08-09). Current phase: **pre-build gate** — measuring usaddress's
real-world accuracy and throughput on public county tax-roll data before any parser build.

## Layout

- `benchmark/` — reproducible benchmark suite (first deliverable, per R5)
  - `fetch_data.py` — pulls address samples from public county open-data APIs
  - `data/` — fetched raw samples (CSV; regenerate with the fetch script)
  - `run_baseline.py` — usaddress single-core throughput + parse-quality measurement
