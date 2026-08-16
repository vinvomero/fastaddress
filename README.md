# fastaddress

A drop-in replacement for [usaddress](https://github.com/datamade/usaddress), the standard US
address parser. Same trained model, new Rust engine.

```python
import fastaddress  # instead of: import usaddress

fastaddress.tag("123 N Main St Apt 4B Springfield IL 62704")
# ({'AddressNumber': '123', 'StreetNamePreDirectional': 'N', ...}, 'Street Address')
```

## Why this exists

usaddress is quietly enormous infrastructure:
[5.2M monthly downloads](https://pepy.tech/project/usaddress) (pepy.tech, Aug 2026) and
[1,145 dependent repos](https://github.com/datamade/usaddress/network/dependents), including
government and open-data projects. It is also built on a Python CRF implementation that tops
out around eight thousand addresses a second, while county tax rolls and national datasets run
to millions of rows. People work around that with sampling, overnight jobs, and multiprocessing
pools.

There's no accuracy tradeoff on offer here. The model is good. The runtime is the bottleneck.
So: DataMade's model, redistributed unmodified, running in a compiled engine.

## Install

Not on PyPI yet -- until it is, this repo and its release page are the only official
sources. Two ways in:

```bash
# Prebuilt wheel, no Rust needed: grab the one matching your OS/Python from
# https://github.com/vinvomero/fastaddress/releases  then
pip install <downloaded-wheel>.whl

# Or build from source (needs a Rust toolchain from https://rustup.rs; takes a few minutes)
pip install git+https://github.com/vinvomero/fastaddress
```

Verify: `python -c "import fastaddress; print(fastaddress.tag('123 N Main St Springfield IL 62704'))"`.
Agents get their own runbook in [AGENTS.md](AGENTS.md).

What you get:

- **11.3x faster single-core**, like for like: 89,653 addresses/sec against usaddress's 7,941,
  same machine, same run. The native Rust engine hits 360,035/sec on 8 threads. A million-row
  tax roll in seconds. ([speed report](benchmark/results/speed_report.md), rerun it with
  `python benchmark/run_speed.py`)
- **The same answers.** Not similar -- identical, checked at four layers (tokens, features,
  serialized attributes, tagged output) across 20,738 real county addresses, zero divergences
  ([parity report](benchmark/results/parity_report.md)).
- **No crashes in native mode.** Saint-name streets like "ST JAMES PLACE" have raised
  `RepeatedLabelError` in usaddress since 2017; they parse fine through `tag_native()`. Compat
  mode still reproduces the error exactly, because drop-in means drop-in.
- **A 0.8MB wheel with the model inside.** No C toolchain, no model download, works on Lambda,
  imports in about a quarter second.
- **Confidence scores** per token and per parse -- the long-standing
  [usaddress#337](https://github.com/datamade/usaddress/issues/337) request.
- **A retrained model that doesn't ship, and the full reason why.** Our best candidate wins 74-0
  on human-adjudicated hard cases and beats the original by +2.4 points on held-out real mail
  text -- but on the national free-text exam its edge (+0.789 points) has a confidence interval
  that includes zero. Under rules set before any results existed, it stays out. Both scoring
  attempts are spent. The chain, failures included, is in
  [the accuracy record](#the-accuracy-record).

`parse()`, `tag()` (with `tag_mapping` and usaddress's parameter names), and
`RepeatedLabelError` (same attributes, same message) behave identically to usaddress 0.5.16 on
the ASCII-dominant inputs property data consists of. Two documented differences: `tag()` returns
a plain insertion-ordered dict rather than an OrderedDict (equal by `==`, distinguishable by
`isinstance`), and Unicode casing/digit classification can diverge on non-ASCII digits.

## Confidence scores

Every parse can report how sure the model is, per token and for the whole sequence -- the CRF's
marginal probabilities, computed by forward-backward over the same weights Viterbi already uses.
Opt-in; the plain functions never pay for it. This is [usaddress#337](https://github.com/datamade/usaddress/issues/337).

```python
fastaddress.parse_with_confidence("123 N Main St Springfield IL 62704")
# [('123', 'AddressNumber', 0.99995), ('N', 'StreetNamePreDirectional', 0.99452), ...]

tagged, address_type, confidence, sequence_confidence = fastaddress.tag_with_confidence(addr)
# tagged/address_type are byte-identical to tag(); confidence is keyed the same way
```

A multi-token component reports the minimum across its tokens -- the weakest link.

The numbers are correct: verified against `pycrfsuite.Tagger.marginal()` on the same model and
addresses, max absolute difference 1.665e-15 across 34,028 token positions, zero Viterbi
disagreements (`python benchmark/compare_marginals.py --rows 5000`).

How well they predict errors is a smaller claim. On our 40 hardest adjudicated records,
weakest-token confidence separates right from wrong parses with an AUC of 0.703 (means 0.935 vs
0.891) -- and only 5 of those 40 are judged-correct, so read it as directional. An earlier draft
quoted stronger figures from an analysis we could no longer regenerate, so they were withdrawn.
Regenerate today's with `python benchmark/confidence_error_auc.py`. On a general mix, easy
addresses sit at 0.999+ and separate cleanly. Treat confidence as a filter for routing doubtful
records to review, never as permission to skip it.

## The accuracy record

Every claim here links to the artifact that produced it, and this section gets updated whenever
a model or evaluation changes. If you can't regenerate a number from this repo, that's a bug.
File an issue.

### The two models

| | Default (compat) | v2 (opt-in) |
|---|---|---|
| What it is | DataMade's trained model, [redistributed unmodified](model/PROVENANCE.md) | Retrained by this project (current candidate: [recipe manifest](training/MANIFEST-v43.json)) |
| Output | Bit-identical to usaddress 0.5.16 | Differs on purpose, on documented error classes |
| Status | Shipping | **Not in this release.** It wins everywhere we built the test ourselves and ties on real mail text. Ships when that changes, or never. |

### How v2 was evaluated

Rules first, training second. [eval/PROTOCOL.md](eval/PROTOCOL.md) fixed the gates, the labeling
method, who reviews, and what gets disclosed, all before a model existed. Gates don't move once
results arrive. Candidates that missed them are published in the
[findings report](benchmark/results/model-v2-findings.md) as loudly as the ones that passed.

| Gate | Bar | Current candidate (v43) |
|---|---|---|
| Gold-set margin (composed-era set) | at least +3.0pp, 95% CI excluding zero | 74 wins, 0 losses on adjudicated disagreements (14 new ones pending review); passes the bar at the floor. Pass. |
| Clean set (upstream's own held-out files) | within 1.0pp of the original | 159/159, exactly equal. Pass. |
| National scans (16-state, then a 32-state holdout) | net improvement; no state worse than 3:1 | Both pass. |
| 20-county split (spent by v36's one-shot binding run: 70.5% right vs 17.3%) | same two rules | Pass. |
| Real-text dev holdout (2,000 held-out real mail lines) | beat the original, CI excluding zero | +2.400pp, CI [+1.750, +3.100]. Pass. |
| **Gold-2: real free-text, 40 states + DC (two attempts, both spent)** | net margin positive, CI excluding zero; no census division net-negative | Attempt 1 (v36): +0.215pp, CI [-0.861, +1.291] -- fail. **Attempt 2 (v43): +0.789pp, CI [-0.287, +1.865] -- fail.** |

Every deciding record was judged by a human: seven blinded review rounds, Census evidence
attached, verdicts and keys committed in [eval/gold/](eval/gold/) and [eval/gold2/](eval/gold2/).
Only human verdicts count -- the LLM suggestion files in those folders were prelabeling triage,
committed for transparency and excluded from every margin. The candidate's 14 newest gold-1
divergences are unreviewed and count for nothing, which is why that row says "at the floor."

One disclosure travels with these numbers: v2's training targets error classes found by studying
gold-set failures, which biases the gold margin upward. The honest claim is "measurably better on
identified, evidence-backed error classes," never a bare accuracy percentage. The clean set is the
control nobody studied, and it caught one candidate (v21) memorizing instead of generalizing.

### What the gold set is, and is not

Gold-1 is 1,500 real free-text addresses, and three quarters of it is two states: 900 Cook
County records, 225 from NYC. The margin inherits that skew, badly. Thirty-four of one
candidate's 73 wins were a single Illinois pattern. So the set proves the identified classes got
fixed and proves nothing about nationwide accuracy. We never claimed otherwise, and that gap is
the whole reason gold-2 exists.

### The checks that caught our own models

Four surfaces, each added because the last one turned out to be too easy. Each caught something.
Full blow-by-blow in the [findings report](benchmark/results/model-v2-findings.md).

First, a 16-state scan over 108k Census TIGER addresses. It failed the first candidate that
cleared the gold gates, and not narrowly: 54.9% of v23's changes were wrong nationally. It had
started reading `New Orleans` as a state and `Box Elder` as a PO box. Five iterations fixed
that, each against rules committed before the run.

Then a 32-state holdout of places no decision had ever touched. It failed the candidate that had
just passed everything it was iterated against: 41.1% right, 45.2% wrong. Three more iterations
got it green. But those three rounds meant the holdout had steered the fixes, so it wasn't
independent anymore either.

Which is the trap this whole section is about. A test you iterate against stops being a test.

So the third surface was one-shot: fresh counties drawn by committed seed, a single run, outcome
final. The first attempt failed on two counties and the model got pulled from the release. The
second passed decisively, 70.5% of changes right against 17.3%, all 20 counties clean.

That earned the real exam. Gold-2 is 1,394 owner-mailing addresses from 40 states and DC, every
census division, as assessors actually typed them, with two scoring attempts allowed for the
lifetime of the set. Attempt 1 (v36): 30 wins, 27 losses, +0.215pp, interval includes zero.
Attempt 2 (v43): 35 wins, 24 losses, +0.789pp, interval includes zero. Both fail.

Between those attempts we did the thing that should have been done first, which was train on
real text. 299,832 owner-mail lines from 30 states, labeled by alignment against Census records,
every line that didn't match exactly thrown away rather than guessed at. 55% survived. (The last
corpus this project built with heuristics measured 9.11% wrong. Alignment or nothing.)

It worked, mostly. v43 came out the first candidate ever green on every internal surface at
once, and the free-text margin nearly quadrupled. It still didn't clear the bar, because a
64-disagreement exam can't certify an effect under about 1.1 points. Right direction, not enough
resolution to prove it.

Gold-2 is spent now, both attempts disclosed. The replacement is already built and untouched:
gold-2b, 2,912 records across 32 states, drawn only from datasets that neither gold-2 nor any
training corpus ever saw, pre-registered before a single record was fetched. One source failed
its provenance check mid-build and got dropped. Nothing has been scored against it.

### Training data, all of it

| Source | Role | License/status |
|---|---|---|
| usaddress `labeled.xml` + Iowa OpenAddresses XML | base corpus | MIT, upstream repo |
| County parcel rolls (Cook IL, Allegheny PA) | distant supervision, capped | public open data |
| v1 distillation + shape-preserving augmentation | stability | derived |
| Error-class synthetics ([generator](training/synth_error_classes.py)) | targeted fixes; every generator cites the human ruling or Census evidence behind it | generated |
| Census PLACE national city vocabulary | national counterweight | public domain |
| Census TIGER/FEATNAMES street splits | alignment reference: proved the old heuristic corpus 9.11% wrong; now labels the real-text corpus | public domain |
| Real owner-mail lines, aligned ([builder](training/build_realtext_corpus.py), [manifest](training/REALTEXT_MANIFEST.json)) | 164,879 rows, 30 states; feeds v37+ candidates only, no shipping model | public open data + public domain |

No gold or clean evaluation address appears in any training corpus. The builders enforce this
with normalized-identity dedupe.

### The data and the people in it

Every address here comes from public county and state assessor rolls -- records governments
publish so property information can be checked. Owner names appear only where the assessor put
them in the mailing-address field and the parser has to handle them (`Recipient` is a real
parsing class). Nothing goes beyond what the source already made public: no SSNs, no non-public
fields, nothing behind authentication. If your name is here and you'd rather it weren't, open an
issue -- name tokens can be masked in place without disturbing any locked cohort.

## Trust, not claims

Every number above regenerates from this repo: `benchmark/run_parity.py` (four-layer differential
suite), `run_speed.py` (three-way interleaved benchmark), `confidence_error_auc.py`,
`compare_marginals.py`, and `fetch_data.py` for the public-data fetch. Run them before you
believe any of it.

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

Issue triage is committed for at least 12 months post-launch, by the repo owner (@vinvomero).
The engine is maintenance-light by design: no retraining pipeline, no external data dependency.
