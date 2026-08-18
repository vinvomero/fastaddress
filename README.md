# fastaddress

Fast US address parsing in Python, backed by Rust.
Compatible with the `usaddress` API and its trained model.

```python
import fastaddress

fastaddress.tag("123 N Main St Apt 4B Springfield IL 62704")
# ({'AddressNumber': '123', 'StreetNamePreDirectional': 'N', ...}, 'Street Address')
```

## Why this exists

`usaddress` is widely used, but its Python CRF runtime is slow on large datasets. On our
benchmark machine it parses about 8,000 addresses per second, which becomes noticeable on county
tax rolls and national property datasets.

`fastaddress` runs the same trained model in Rust.

```text
usaddress                7,941 addresses/sec
fastaddress             89,653 addresses/sec
fastaddress, 8 threads  360,035 addresses/sec
```

Single-core throughput is 11.3x higher.

The compatibility suite checks 20,738 real county addresses at the token, feature, serialized
attribute, and tagged-output levels. It found zero divergences.

[Speed report](benchmark/results/speed_report.md)
[Parity report](benchmark/results/parity_report.md)

## Install

Not on PyPI yet.
Download a prebuilt wheel from [Releases](https://github.com/vinvomero/fastaddress/releases):

```bash
pip install <downloaded-wheel>.whl
```

Or build from source with Rust installed:

```bash
pip install git+https://github.com/vinvomero/fastaddress
```

Verify:

```bash
python -c "import fastaddress; print(fastaddress.tag('123 N Main St Springfield IL 62704'))"
```

See [AGENTS.md](AGENTS.md) for the agent runbook.

## What you get

- 89,653 addresses/sec on one core. 360,035/sec on 8 threads.
- Drop-in API compatibility. `parse()`, `tag()`, `tag_mapping`, and `RepeatedLabelError`.
- Zero output divergences across 20,738 real addresses in the parity suite.
- Native mode. `tag_native()` handles cases such as `ST JAMES PLACE` without raising `RepeatedLabelError`.
- Confidence scores. Token, component, and sequence probabilities from the CRF.
- Small wheels. Roughly 0.8 MB with the model included. No model download or external service.
- Reproducible benchmarks. The scripts and source data are in the repo.

## API

The normal API follows `usaddress 0.5.16` behavior:

```python
fastaddress.parse(address)
fastaddress.tag(address)
```

Native parsing is also available:

```python
fastaddress.tag_native(address)
```

There are two known compatibility differences:

- `tag()` returns an insertion-ordered `dict`, not `OrderedDict`.
- Unicode casing and digit classification may differ for non-ASCII inputs.

For typical US property data, both implementations produce the same tagged output.

## Confidence scores

```python
fastaddress.parse_with_confidence(
    "123 N Main St Springfield IL 62704"
)
# [
#   ('123', 'AddressNumber', 0.99995),
#   ('N', 'StreetNamePreDirectional', 0.99452),
#   ...
# ]
```

Tagged output:

```python
tagged, address_type, confidence, sequence_confidence = (
    fastaddress.tag_with_confidence(addr)
)
```

For components spanning multiple tokens, confidence is the minimum token probability.

The implementation was compared against `pycrfsuite.Tagger.marginal()` over 34,028 token
positions:

```text
max absolute difference  1.665e-15
Viterbi disagreements    0
```

Reproduce it:

```bash
python benchmark/compare_marginals.py --rows 5000
```

Confidence is useful for deciding which records to review. It is not a calibrated probability
that the full address is correct.

## Experimental model

The shipping model is unchanged. The repo also contains an experimental retrained model that
targeted known parsing errors. It does not ship because accuracy did not improve.

The retraining passed every internal gate — 74 wins / 0 losses on adjudicated hard cases,
+2.400pp on a held-out real-text set, both national scans — and then failed the deciding
national exam three times running:

```text
Gold-2   attempt 1   v36   +0.215pp   95% CI [-0.861, +1.291]
Gold-2   attempt 2   v43   +0.789pp   95% CI [-0.287, +1.865]
Gold-2b  attempt 1   v50   -0.275pp   95% CI [-0.927, +0.343]
```

The third is net negative. That prompted building an evaluation set from sources disjoint from
every exam and every training corpus, labeled by hand (Gold-2c). Scored on it, every retrained
candidate is worse than the original on ordinary streets that carry their suffix — the commonest
shape in US mail:

```text
original                    38 / 47 suffix-present correct
best retrained candidate    25 / 47
```

The result is that the retraining traded real-world accuracy for wins on self-selected cases. The default model — DataMade's,
redistributed unmodified — is what ships.

The full protocol, training history, failed candidates, and adjudications are here:

- [Evaluation protocol](eval/PROTOCOL.md)
- [Model findings](benchmark/results/model-v2-findings.md)
- [Training manifest](training/MANIFEST-v43.json)
- [Gold evaluations](eval/)

## Training data

The experimental model uses upstream labeled data, public county parcel records, Census data,
generated error cases, and 162,879 aligned owner-mailing records from 30 states.

No Gold or clean-set evaluation address appears in a training corpus. The builders enforce this
with normalized-identity deduplication.

See `training/` for manifests and builders.

## Reproduce it

```bash
python benchmark/run_speed.py
python benchmark/run_parity.py
python benchmark/compare_marginals.py
python benchmark/confidence_error_auc.py
```

If a number in this README disagrees with the benchmark output, the benchmark wins.

## Development

```bash
cargo test --workspace

pip install -r benchmark/requirements.txt
python benchmark/fetch_data.py
python benchmark/dump_oracle.py

cargo build --release
python benchmark/run_parity.py
```

Repository layout:

```text
crates/core      Rust parser and CRF engine
crates/python    PyO3 bindings
benchmark/       Benchmarks and parity tests
training/        Experimental model training
eval/            Evaluation data and protocol
model/           Models and provenance
```

## Credit

The default model comes from [DataMade/usaddress](https://github.com/datamade/usaddress) and is
redistributed unmodified under the MIT license. See [model/PROVENANCE.md](model/PROVENANCE.md).

[usaddress-rs](https://github.com/boydjohnson/usaddress-rs) and
[us-addrs](https://github.com/raphaellaude/us-addrs) also informed the Rust model-loading work
and supplied useful test cases.

Issue triage is committed for at least 12 months after launch by
[@vinvomero](https://github.com/vinvomero).
