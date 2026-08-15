# fastaddress

A drop-in replacement for [usaddress](https://github.com/datamade/usaddress), the standard US
address parser. Same trained model, new Rust engine.

```python
import fastaddress  # instead of: import usaddress

fastaddress.tag("123 N Main St Apt 4B Springfield IL 62704")
# ({'AddressNumber': '123', 'StreetNamePreDirectional': 'N', ...}, 'Street Address')
```

What you get:

- **10.5x faster single-core**, like for like: 110,119 addresses/sec against usaddress's 10,493.
  On 8 threads, 212,916/sec. A million-row tax roll in under five seconds. Measured 2026-08-09,
  interleaved runs on a quiet machine; method and current numbers in
  [benchmark/results/speed_report.md](benchmark/results/speed_report.md).
- **The same answers.** Not similar. Identical, checked at four layers (tokens, features,
  serialized attributes, tagged output) across 20,738 real county addresses, zero divergences
  ([parity report](benchmark/results/parity_report.md)).
- **No crashes in native mode.** Addresses that raise `RepeatedLabelError` in usaddress
  (saint-name streets like "ST JAMES PLACE" have been crashing it since 2017) parse fine through
  `tag_native()`. Compat mode still reproduces the error exactly, because drop-in means drop-in.
- **A 0.8MB wheel with the model inside.** No C toolchain, no model download, works on Lambda.
  Imports in about a quarter second.
- **Confidence scores**, the thing [usaddress#337](https://github.com/datamade/usaddress/issues/337)
  has been asking for. Details below.
- **An optional retrained model (v2)** that fixes documented error classes while the default
  stays bit-identical to usaddress. It cleared a pre-registered, human-adjudicated accuracy gate
  (+4.80 points on a 1,500-address gold set, bar was +3.0) and a 16-state national regression
  check. Getting there took six candidates; the failures are published alongside the pass in
  [the accuracy record](#the-accuracy-record).

`parse()`, `tag()` (including `tag_mapping`), and `RepeatedLabelError` behave identically to
usaddress 0.5.16 on the ASCII-dominant inputs real property data consists of. Known Python/Rust
Unicode-casing differences are documented as out of parity scope.

## Confidence scores

Every parse can tell you how sure the model is, per token and for the whole sequence. It's the
CRF's marginal probabilities, computed by forward-backward over the same weights Viterbi already
uses. Opt-in; the plain functions never pay for it.

```python
fastaddress.parse_with_confidence("123 N Main St Springfield IL 62704")
# [('123', 'AddressNumber', 0.99995), ('N', 'StreetNamePreDirectional', 0.99452), ...]

tagged, address_type, confidence, sequence_confidence = fastaddress.tag_with_confidence(addr)
# tagged/address_type are byte-identical to tag(); confidence is keyed the same way
```

When a component spans several tokens, its confidence is the minimum across them. The weakest
link, so a component is never reported as more confident than any token inside it.

Two facts worth knowing before you trust these numbers.

First, they're correct: verified against `pycrfsuite.Tagger.marginal()` running the same model
over the same addresses, max absolute difference 1.665e-15 across 34,028 token positions, zero
Viterbi disagreements. Reproduce with `python benchmark/compare_marginals.py --rows 5000`.

Second, they actually predict errors. Scored against our human-adjudicated records
([eval/gold](eval/gold)), parses judged correct average 0.762 on their weakest token; parses
judged wrong average 0.514 (AUC 0.833). None of the 47 known-wrong parses scored above 0.99,
while 19% of known-correct ones did. Read that as a precision tradeoff: above 0.99 nothing in
this sample was wrong, but only a fifth of correct parses get there. It's a filter for routing
doubtful records to review, not permission to skip reviewing. And those first two numbers come
from contested records, the hardest addresses in the set. On a general mix, easy addresses sit
at 0.999+ and separate more cleanly.

## The accuracy record

This section is the project's transparency contract. Every claim links to the artifact that
produced it, and it gets updated whenever a model or evaluation changes. A number here that you
can't regenerate from the repo is a bug; file an issue.

### The two models

| | Default (compat) | v2 (opt-in) |
|---|---|---|
| What it is | DataMade's trained model, [redistributed unmodified](model/PROVENANCE.md) | Retrained by this project ([recipe manifest](training/MANIFEST-usaddr_v28.json)) |
| Output | Bit-identical to usaddress 0.5.16 | Differs on purpose, on documented error classes |
| Status | Shipping | Shipping, opt-in. Candidate v28, the sixth attempt; see below for what the first five broke. |

### How v2 was evaluated

The rules were set before any training happened and are committed at
[eval/PROTOCOL.md](eval/PROTOCOL.md): what the gates are, how records get labeled, who has to
review them, what gets disclosed. The gates don't move once results exist. Two earlier
candidates missed them, and those misses are published in the
[findings report](benchmark/results/model-v2-findings.md) with the same prominence as the pass.

| Gate | Bar | v2 (candidate v28) |
|---|---|---|
| Gold-set margin | at least +3.0pp, 95% CI excluding zero | +4.80pp, CI [+3.74, +5.94]. Pass, and the floor is +4.67 even if every unadjudicated record went against it. |
| Clean set (upstream's own held-out files) | within 1.0pp of the original | 159/159, exactly equal. Pass. |
| National scan, net improvement | more right than wrong on its changes | 81.9% right vs 12.0%. Pass. |
| National scan, per-state | no state worse than 3:1 against it | All 16 states. Pass. |

The deciding gold records were judged by a human: five review rounds, models blinded as A/B,
Census records attached as evidence, verdicts and blind keys committed in
[eval/gold/](eval/gold/). v28 wins 73 and loses 1: `Anchor Point, AK`, which stays lost until
some future candidate fixes it. (An earlier candidate also lost `1305 Lake Shore Dr N`; v28
fixed it.)

One disclosure has to travel with any of these numbers: v2's training data targets error classes
we found by studying gold-set failures. That biases the gold margin upward. The honest claim is
"measurably better on identified, evidence-backed error classes," never a bare accuracy
percentage. The clean set is the control that was never studied, and it caught one candidate
(v21) memorizing instead of generalizing, at 155/159.

### What the gold set is, and is not

1,500 real free-text addresses: 900 Cook County owner-mailing records (878 of them Illinois),
225 from NYC, and 375 hard cases spread thin across all 51 states and DC. So roughly 75% of the
set is two states, and the win margin inherits that. 34 of v23's 73 wins are one Illinois
pattern (abbreviated city prefixes like `S BARRINGTON`); 31 are New York saint-name streets.

This set proves the identified classes are fixed. It is not evidence of nationwide accuracy, and
we don't claim otherwise. A state-stratified free-text gold set is the next evaluation
milestone, and it will be pre-registered the same way this one was.

### National behavior, or: the check that caught our own model

Because the gold set leans regional, every candidate also runs a
[16-state behavioral scan](benchmark/national_scan.py): about 108k addresses built from Census
TIGER data, scoring every record where the candidate changes the original's answer against the
Census's own component labels.

The first candidate to pass the gold gates (v23) failed this scan badly: 54.9% of its changes
were wrong nationally. It had learned its counterweights from an invented city list, and the
side effects showed up in states the gold set barely touches: it read `New Orleans` as a state,
`South Fulton` as a directional, `Box Elder` as a PO box. It did not ship.

Five iterations followed, each against two ship rules committed to git before any results
existed: net national improvement on the scan, and no state left worse than 3:1 against it.
v24 fixed Louisiana and broke grid cities in Kansas. v25 fixed Kansas. v26 fixed the clean set
and made Georgia worse, which exposed self-contradicting training data (the corpus taught
`Rd S Fulton` as both a city and a direction-plus-city, because Fulton alone is also a city).
v27 falsified that hypothesis: filtering the contradictions changed nothing. The real defect
was exposure: 1,549 confusable city names sampled so thinly each one appeared about 1.5 times
per pattern. v28 gives every confusable city guaranteed coverage, and passes everything:
81.9% of its changes right against 12.0% wrong, every state clean, gold and clean gates intact.
The whole chain is in the git history, each hypothesis committed before its test ran. Composed
text never enters gate arithmetic; the scan is a tripwire for regional overfitting, not an
accuracy claim.

### Training data, all of it

| Source | Role | License/status |
|---|---|---|
| usaddress `labeled.xml` + Iowa OpenAddresses XML | base corpus | MIT, upstream repo |
| County parcel rolls (Cook IL, Allegheny PA) | distant supervision, capped | public open data |
| v1 distillation + shape-preserving augmentation | stability | derived |
| Error-class synthetics ([generator](training/synth_error_classes.py)) | targeted fixes; every generator cites the human ruling or Census evidence behind it | generated |
| Census PLACE national city vocabulary | national counterweight | public domain |
| Census TIGER/FEATNAMES street splits | experiment only, not in any shipping recipe: it proved the old heuristic corpus 9.11% wrong, but the model trained on it regressed | public domain |

No gold or clean evaluation address appears in any training corpus. The builders enforce this
with normalized-identity dedupe.

## Why this exists

usaddress is quietly enormous infrastructure:
[5.2M monthly downloads](https://pepy.tech/project/usaddress) (pepy.tech, Aug 2026),
[1,145 dependent repos](https://github.com/datamade/usaddress/network/dependents) including
government and open-data projects. And it's built on a Python CRF implementation that tops out
around a few thousand addresses a second, while county tax rolls and national datasets run to
millions of rows. Same model, compiled engine: the accuracy people already rely on, at batch
speed.

## Trust, not claims

- `benchmark/run_parity.py`: the four-layer differential suite against Python usaddress
  ([current report](benchmark/results/parity_report.md))
- `benchmark/run_speed.py`: the three-way benchmark, interleaved best-of-three
  ([current report](benchmark/results/speed_report.md))
- `benchmark/fetch_data.py`: reproducible public-data fetch (NYC, Cook County IL, Allegheny
  County PA open-data portals)

Run them yourself before you believe any of this.

## Credit

This project exists because of [DataMade's usaddress](https://github.com/datamade/usaddress).
The default model is their trained model, redistributed unmodified under MIT (see
[model/PROVENANCE.md](model/PROVENANCE.md)). Two earlier Rust ports,
[usaddress-rs](https://github.com/boydjohnson/usaddress-rs) and
[us-addrs](https://github.com/raphaellaude/us-addrs), proved the model-loading approach and
supplied hard test cases; their work is gratefully acknowledged. This is stewardship of an
ecosystem, not a replacement-by-attack. The benchmark suite is offered upstream to usaddress.

## Layout

- `crates/core`: the Rust engine (tokenizer, feature extraction, CRF inference via a vendored
  [crfs](https://github.com/messense/crfs-rs) fork, compat + native APIs)
- `crates/python`: PyO3 bindings and the pip package
- `benchmark/`: reproducible data fetch, parity suite, speed suite, national scan
- `training/` and `eval/`: the v2 corpus builders, evaluation protocol, and adjudicated records
- `model/`: both models plus provenance

## Development

```bash
cargo test --workspace
pip install -r benchmark/requirements.txt
python benchmark/fetch_data.py && python benchmark/dump_oracle.py
cargo build --release && python benchmark/run_parity.py
```

Issue triage is committed for at least 12 months post-launch (owner to be finalized at release).
The engine is maintenance-light by design: no retraining pipeline, no external data dependency.
