# Speed Report — three-way benchmark

Corpus: 20738 addresses (all benchmark datasets). Machine: 8 logical cores.
usaddress 0.5.16 (python-crfsuite), usaddr wheel 0.1.0 (Rust, same model).

| Configuration | Addresses/sec | Multiplier vs baseline |
|---|---|---|
| usaddress, single core (baseline) | 9,476 | 1.0x |
| **usaddr wheel, single core (like-for-like)** | 50,865 | **5.4x** |
| native Rust, single core | 54,132 | 5.7x |
| usaddress, 8 processes (multiprocessing) | 29,069 | 3.1x |
| native Rust, 8 threads | 192,019 | 20.3x |

Multi-core like-for-like (native 8-thread vs usaddress 8-process): 6.6x

Go/no-go vs the >=10x single-core bar: **FAIL** (5.4x)

Both parsers ran the identical compat workload: `tag()` over every row, catching
RepeatedLabelError. Reproduce: `python benchmark/run_speed.py`.
