# fastaddress

A drop-in replacement for [usaddress](https://github.com/datamade/usaddress). Same trained
model, new Rust engine.

```python
import fastaddress  # instead of: import usaddress

fastaddress.tag("123 N Main St Apt 4B Springfield IL 62704")
# ({'AddressNumber': '123', 'StreetNamePreDirectional': 'N', ...}, 'Street Address')
```

11.3x faster on one core. Same answers.

## Why this exists

usaddress is quietly enormous infrastructure: about
[5.2M monthly downloads](https://pepy.tech/project/usaddress) as of August 2026 and
[1,145 dependent repositories](https://github.com/datamade/usaddress/network/dependents),
including government and open-data projects.

The model is good. The runtime is the bottleneck.

On our benchmark machine, usaddress parses about 8,000 addresses/sec. That's fine for small
files. County tax rolls and national property datasets run into millions of rows, so people
compensate with multiprocessing, sampling, and overnight jobs.

fastaddress keeps DataMade's trained model unchanged and runs it in a compiled Rust CRF engine.

No accuracy tradeoff. No new model hiding behind a compatible API. Just faster inference.

## What you get

- **11.3x faster single-core.** 89,653 addresses/sec vs. 7,941 for usaddress, same machine and
  same run. Native Rust reaches 360,035/sec on 8 threads.
  [Speed report](benchmark/results/speed_report.md).
- **The same answers.** We compare tokens, features, serialized CRF attributes, and final tagged
  output across 20,738 real county addresses. Zero divergences.
  [Parity report](benchmark/results/parity_report.md).
- **Native mode without `RepeatedLabelError`.** Addresses such as `ST JAMES PLACE` parse normally
  through `tag_native()`. Compatibility mode reproduces the original exception exactly.
- **A ~0.8 MB wheel with the model inside.** No C toolchain, model download, or external service.
  Works on Lambda and imports in roughly a quarter second.
- **Confidence scores.** Token-level and full-parse CRF probabilities, addressing the
  long-standing [usaddress#337](https://github.com/datamade/usaddress/issues/337) request.
- **An experimental model we refused to ship.** Our best retrained candidate wins 74-0 on
  adjudicated hard cases and improves held-out real-mail text by +2.4 points. It still failed our
  preregistered national significance gate, so the original model remains the default.
  [Full accuracy record](#about-the-experimental-model).

## Install

Not on PyPI yet. Until it is, this repository and its releases are the only official sources.

**Prebuilt wheel.** Download the wheel matching your OS and Python version from
[Releases](https://github.com/vinvomero/fastaddress/releases):

```bash
pip install <downloaded-wheel>.whl
```

No Rust required.

**From source.** Requires a Rust toolchain from [rustup.rs](https://rustup.rs):

```bash
pip install git+https://github.com/vinvomero/fastaddress
```

Verify:

```bash
python -c "import fastaddress; print(fastaddress.tag('123 N Main St Springfield IL 62704'))"
```

AI coding agents: see [AGENTS.md](AGENTS.md).

## Compatibility

`parse()`, `tag()`, `tag_mapping`, parameter names, and `RepeatedLabelError` match usaddress
0.5.16 on the ASCII-dominant inputs typical of U.S. property data.

Two known differences:

1. `tag()` returns a normal insertion-ordered dict, not an `OrderedDict`. They're equal with
   `==`, but distinguishable with `isinstance()`.
2. Unicode casing and digit classification can differ on some non-ASCII characters.

For strict compatibility, use the normal API. For the faster native behavior around cases such
as repeated labels, use `tag_native()`.

## Confidence scores

Confidence is opt-in, so normal `parse()` and `tag()` calls don't pay for it.

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

Or:

```python
tagged, address_type, confidence, sequence_confidence = (
    fastaddress.tag_with_confidence(addr)
)
```

Multi-token components use the minimum token confidence: the weakest link.

The probabilities were checked against `pycrfsuite.Tagger.marginal()` across 34,028 token
positions:

- maximum absolute difference: 1.665e-15
- Viterbi disagreements: 0

Reproduce it:

```bash
python benchmark/compare_marginals.py --rows 5000
```

Confidence is useful for routing questionable parses to review. It is not a calibrated guarantee
that a parse is correct. On our 40 hardest adjudicated records, weakest-token confidence
separates right parses from wrong ones with an AUC of 0.703: a real signal, and a modest one
(`python benchmark/confidence_error_auc.py`).

## About the experimental model

The shipping model is DataMade's original model, redistributed unmodified. The retrained
candidate does not ship, and the reason is worse than "it didn't clear the bar."

We built a retrained model to fix specific, human-verified error classes, with release gates
set before training and never moved afterward. It passed a lot of them: 74-0 on adjudicated
hard cases, 159/159 on the upstream clean set, both national scans, a one-shot 20-county
evaluation, +2.400pp on held-out real mailing text. It then failed the deciding national test
three times running.

| Exam | Candidate | Result | 95% CI |
|---|---|---|---|
| Gold-2 attempt 1 | v36 | +0.215pp | [-0.861, +1.291] |
| Gold-2 attempt 2 | v43 | +0.789pp | [-0.287, +1.865] |
| Gold-2b attempt 1 | v50 | **-0.275pp** | [-0.927, +0.343] |

The third one is net negative. That prompted a question we should have asked earlier: were the
surfaces saying "better" actually measuring anything independent?

They weren't. Every validation surface we had shared a generative process with the training
data. So we built one that didn't -- **gold-2c**: 600 addresses from 25 datasets disjoint from
every exam and every training corpus, with 126 records carrying *absolute* human-approved label
sequences rather than pairwise verdicts. Then we scored the whole historical line on it.

| Model | vs. original | Streets with the suffix present |
|---|---|---|
| v19 (before the error-class work) | +2 | 42/47 |
| v28 | -9 | 34/47 |
| v36 | -3 | 36/47 |
| v43 | -13 | 25/47 |
| v50 | -13 | 25/47 |

Every candidate from v28 onward is **worse than the original** on independent human-labeled
free text, and the gap widens as the campaign progressed. The damage concentrates in one place:
ordinary streets that carry their suffix, the commonest shape in American mail. The original
gets 38 of 47; our best recent candidates get 25.

What happened is a textbook result, and we published the textbook: the training data targeted
error classes discovered by studying our own gold set's failures, so the model learned to
distrust the patterns those failures came from. The gold set said we improved. The clean set,
the scans, and the dev holdouts all agreed. They were wrong together, because they were built
from the same material. The one model that beats the original here, v19, predates all of that
targeted work -- though its +2 has a confidence interval including zero, so it isn't a win
either, just an absence of self-inflicted damage.

Gold-2b has one scoring attempt left. It stays unspent: no candidate from this line may be
proposed for it, and any future one has to beat the original on suffix-present addresses first.

One disclosure travels with every number above, required by
[eval/PROTOCOL.md](eval/PROTOCOL.md): the candidate's training targeted error classes found by
studying Gold-1 failures, which biases that set's margin upward. That disclosure has been in
this README since the beginning. It turned out to be understating the problem rather than
overstating it.

Full chain: [model findings](benchmark/results/model-v2-findings.md),
[evaluation protocol](eval/gold2/PROTOCOL2.md), and the gold-2c
[approved labels](eval/gold2c/approved_labels.json) that produced the table above
(`python benchmark/gold2c_dev.py --candidate <model>`).

## Training data

The experimental model uses:

| Source | Role |
|---|---|
| usaddress labeled data | Base corpus |
| Cook County + Allegheny County parcel rolls | Distant supervision |
| v1 distillation and shape-preserving augmentation | Stability |
| Error-class synthetics | Targeted fixes |
| Census PLACE | National city vocabulary |
| Census TIGER / FEATNAMES | Alignment reference |
| 162,879 aligned owner-mail lines from 30 states | Real-text training |

No Gold or clean-set evaluation address appears in a training corpus. Builders enforce this with
normalized-identity deduplication.

Full manifests live in [training/](training/).

Every address in this repository comes from public county and state assessor rolls. Owner names
appear only where an assessor put them in a mailing-address field and the parser has to handle
them. Nothing here goes beyond what the source already published. If your name is here and you'd
rather it weren't, open an issue.

## Reproduce the claims

The benchmark scripts are part of the repository:

```text
benchmark/run_parity.py
benchmark/run_speed.py
benchmark/compare_marginals.py
benchmark/confidence_error_auc.py
benchmark/fetch_data.py
```

Run them before you trust the README.

If the artifacts and this page disagree, the README is wrong.

## Credit

fastaddress exists because [DataMade's usaddress](https://github.com/datamade/usaddress) exists.

The default model is their trained model, redistributed unmodified under MIT. See
[model/PROVENANCE.md](model/PROVENANCE.md).

Earlier Rust ports, [usaddress-rs](https://github.com/boydjohnson/usaddress-rs) and
[us-addrs](https://github.com/raphaellaude/us-addrs), demonstrated the model-loading approach and
supplied useful hard cases.

This project isn't an argument that usaddress is bad software. Its model was good enough to
become infrastructure.

fastaddress replaces the slow part.

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
crates/core      Rust engine
crates/python    PyO3 bindings and Python package
benchmark/       Parity, speed, confidence, and national tests
training/        Experimental model training
eval/            Evaluation protocols and adjudicated records
model/           Models and provenance
```

Issue triage is committed for at least 12 months after launch by
[@vinvomero](https://github.com/vinvomero).
