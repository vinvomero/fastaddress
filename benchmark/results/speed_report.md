# Speed Report — three-way benchmark

Corpus: 20738 addresses (all benchmark datasets). Machine: 8 logical cores.
usaddress 0.5.16 (python-crfsuite), usaddr wheel 0.1.0 (Rust, same model).

| Configuration | Addresses/sec | Multiplier vs baseline |
|---|---|---|
| usaddress, single core (baseline) | 3,537 | 1.0x |
| **usaddr wheel, single core (like-for-like)** | 36,319 | **10.3x** |
| native Rust, single core | 37,336 | 10.6x |
| usaddress, 8 processes (multiprocessing) | 8,198 | 2.3x |
| native Rust, 8 threads | 142,846 | 40.4x |

Multi-core like-for-like (native 8-thread vs usaddress 8-process): 17.4x

Go/no-go vs the >=10x single-core bar: **PASS** (10.3x)

Both parsers ran the identical compat workload: `tag()` over every row, catching
RepeatedLabelError. Reproduce: `python benchmark/run_speed.py`.
