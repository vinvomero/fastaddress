# Speed Report — three-way benchmark

Corpus: 20738 addresses (all benchmark datasets). Machine: 8 logical cores.
usaddress 0.5.16 (python-crfsuite), usaddr wheel 0.1.0 (Rust, same model).

| Configuration | Addresses/sec | Multiplier vs baseline |
|---|---|---|
| usaddress, single core (baseline) | 10,493 | 1.0x |
| **usaddr wheel, single core (like-for-like)** | 110,119 | **10.5x** |
| native Rust, single core | 72,688 | 6.9x |
| usaddress, 8 processes (multiprocessing) | 15,849 | 1.5x |
| native Rust, 8 threads | 212,916 | 20.3x |

Multi-core like-for-like (native 8-thread vs usaddress 8-process): 13.4x

Go/no-go vs the >=10x single-core bar: **PASS** (10.5x)

Both parsers ran the identical compat workload: `tag()` over every row, catching
RepeatedLabelError. Reproduce: `python benchmark/run_speed.py`.
