# usaddr (working name)

A drop-in replacement for [usaddress](https://github.com/datamade/usaddress) — the standard
US address parser — running the **same trained CRF model** in a Rust engine.

- **10x faster** single-core, like-for-like (110,000+ addresses/sec vs ~10,500), and
  **210,000+ addresses/sec** multi-threaded — a million-row tax roll in under 5 seconds
  (measured; methodology and current numbers in [benchmark/results/speed_report.md](benchmark/results/speed_report.md))
- **Exact output parity**: same model, same features, same predictions — verified at four layers
  (tokens, features, serialized attributes, tagged output) across 20,738 real county tax-roll
  addresses with **zero divergences** (current run: [benchmark/results/parity_report.md](benchmark/results/parity_report.md))
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
usaddress 0.5.16 on the ASCII-dominant inputs real property data consists of; known Python/Rust
Unicode-casing differences are documented as out of parity scope.

### Confidence scores

CRF marginal probabilities, the thing upstream
[usaddress#337](https://github.com/datamade/usaddress/issues/337) asks for, computed by
forward-backward over the same weights Viterbi uses. Opt-in: the functions above never run it.

```python
usaddr.parse_with_confidence("123 N Main St Springfield IL 62704")
# [('123', 'AddressNumber', 0.99995), ('N', 'StreetNamePreDirectional', 0.99452), ...]

tagged, address_type, confidence, sequence_confidence = usaddr.tag_with_confidence(addr)
# tagged/address_type are byte-identical to tag(); confidence is keyed the same way
```

`confidence[label]` is the marginal probability of that component's label. When a component spans
several tokens the value is the **minimum** across its tokens — the weakest link, so a component
is never reported as more confident than any token inside it. `sequence_confidence` is the joint
probability of the whole predicted labelling.

Verified against `pycrfsuite.Tagger.marginal()` running the same model over the same addresses —
**max absolute difference 1.665e-15** across 34,028 token positions, with zero Viterbi
disagreements. Reproduce it with:

```bash
python benchmark/compare_marginals.py --rows 5000
```

## Why this exists

usaddress is quietly enormous infrastructure — [5.2M monthly downloads](https://pepy.tech/project/usaddress)
(pepy.tech, Aug 2026), [1,145 dependent repos](https://github.com/datamade/usaddress/network/dependents) including government and
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
