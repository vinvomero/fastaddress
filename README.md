# usaddr (working name)

A drop-in replacement for [usaddress](https://github.com/datamade/usaddress) — the standard
US address parser — running the **same trained CRF model** in a Rust engine.

- **10x faster** single-core, like-for-like (36,000+ addresses/sec vs ~3,500; measured, reproducible)
- **Exact output parity**: same model, same features, same predictions — verified at four layers
  (tokens, features, serialized attributes, tagged output) across 20,738 real county tax-roll
  addresses with **zero divergences**
- **Never crashes in native mode**: inputs that raise `RepeatedLabelError` in usaddress (e.g.,
  saint-name streets like "ST JAMES PLACE") parse gracefully via `tag_native()` — compat mode
  reproduces the error exactly for drop-in fidelity
- **Tiny install**: prebuilt wheels with the 134KB model embedded; no C toolchain, no gigabyte
  model downloads; ~265ms import

```python
import usaddr  # instead of: import usaddress

usaddr.tag("123 N Main St Apt 4B Springfield IL 62704")
# ({'AddressNumber': '123', 'StreetNamePreDirectional': 'N', ...}, 'Street Address')
```

`parse()`, `tag()` (including `tag_mapping`), and `RepeatedLabelError` behave identically to
usaddress 0.5.16. Multi-thread batch processing reaches 140k+ addresses/sec on 8 cores.

## Why this exists

usaddress is quietly enormous infrastructure — millions of monthly downloads, government and
open-data dependents — built on a CRF architecture whose Python implementation tops out around a
few thousand addresses per second. County tax rolls, assessor records, and national datasets run
to the millions of rows. Same model, compiled engine: the accuracy people rely on, at batch speed.

## Trust, not claims

- `benchmark/run_parity.py` — the four-layer differential suite against Python usaddress
  ([current report](benchmark/results/parity_report.md))
- `benchmark/run_speed.py` — the three-way benchmark, interleaved best-of-three
  ([current report](benchmark/results/speed_report.md))
- `benchmark/fetch_data.py` — reproducible public-data fetch (NYC, Cook County IL, Allegheny
  County PA open-data portals)

## Credit

This project exists because of [DataMade's usaddress](https://github.com/datamade/usaddress) —
the model this engine runs is their trained model, redistributed unmodified under MIT (see
[model/PROVENANCE.md](model/PROVENANCE.md)). Prior Rust explorations
[usaddress-rs](https://github.com/boydjohnson/usaddress-rs) and
[us-addrs](https://github.com/raphaellaude/us-addrs) proved the model-loading approach and
supplied hard test cases; their work is gratefully acknowledged. This is stewardship of an
ecosystem, not a replacement-by-attack: the benchmark suite is offered upstream to usaddress.

## Layout

- `crates/core` — Rust engine (tokenizer, feature extraction, CRF inference via
  [crfs](https://github.com/messense/crfs-rs), compat + native APIs)
- `crates/python` — PyO3 bindings and the pip package
- `benchmark/` — reproducible data fetch, parity suite, speed suite
- `model/` — the vendored usaddress model + provenance

## Development

```bash
cargo test --workspace
pip install -r benchmark/requirements.txt
python benchmark/fetch_data.py && python benchmark/dump_oracle.py
cargo build --release && python benchmark/run_parity.py
```

Maintenance: issue triage is committed for at least 12 months post-launch (owner to be finalized
at release). The engine is maintenance-light by design — no retraining pipeline or external data
dependency.
