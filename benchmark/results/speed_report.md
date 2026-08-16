# Speed Report — three-way benchmark

Corpus: 20738 addresses (all benchmark datasets). Machine: 8 logical cores.
usaddress 0.5.16 (python-crfsuite), fastaddress wheel 0.1.0 (Rust, same model).

| Configuration | Addresses/sec | Multiplier vs baseline |
|---|---|---|
| usaddress, single core (baseline) | 7,941 | 1.0x |
| **fastaddress wheel, single core (like-for-like)** | 89,653 | **11.3x** |
| native Rust, single core | 108,918 | 13.7x |
| usaddress, 8 processes (multiprocessing) | 15,450 | 1.9x |
| native Rust, 8 threads | 360,035 | 45.3x |

Multi-core like-for-like (native 8-thread vs usaddress 8-process): 23.3x

Go/no-go vs the >=10x single-core bar: **PASS** (11.3x)

Both parsers ran the identical compat workload: `tag()` over every row, catching
RepeatedLabelError. Reproduce: `python benchmark/run_speed.py`.
