# fastaddress

A drop-in replacement for [usaddress](https://github.com/datamade/usaddress), the standard US
address parser. Same trained model, new Rust engine.

```python
import fastaddress  # instead of: import usaddress

fastaddress.tag("123 N Main St Apt 4B Springfield IL 62704")
# ({'AddressNumber': '123', 'StreetNamePreDirectional': 'N', ...}, 'Street Address')
```

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

- **11.3x faster single-core**, like for like: 89,653 addresses/sec against usaddress's 7,941
  on the same machine, same run. The native Rust engine reaches 360,035/sec on 8 threads (the
  Python API itself is single-threaded per call). A million-row tax roll in seconds. Measured
  2026-08-16 on the release build; method and current numbers in
  [benchmark/results/speed_report.md](benchmark/results/speed_report.md) -- rerun it yourself
  with `python benchmark/run_speed.py`.
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
- **A retrained model that doesn't ship, and we'll tell you exactly why.** Our best candidate
  wins 74-0 on human-adjudicated hard cases. It beats the original by +2.4 points on held-out
  real mail text. And on the 1,394-record national free-text exam, its edge came out to
  +0.789 points with a confidence interval that includes zero -- so under rules we set before
  seeing any results, it stays out. Both allowed scoring attempts are spent. The whole chain,
  failures included, is in [the accuracy record](#the-accuracy-record).

`parse()`, `tag()` (including `tag_mapping` and usaddress's parameter names), and
`RepeatedLabelError` (same attributes, same message text) behave identically to usaddress
0.5.16 on the ASCII-dominant inputs real property data consists of. Known Python/Rust Unicode
differences in casing and digit classification (fullwidth or Arabic-Indic digits can take a
different label) are out of parity scope; standalone `½` tokens are preserved and parity-tested.

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

Second, what they can and can't tell you about errors. On the hardest slice we have -- the 40
human-adjudicated records that carry approved label sequences, almost all of them cases where
the default model gets something wrong -- weakest-token confidence separates right from wrong
parses with an AUC of 0.703 (means 0.935 vs 0.891). That's a modest signal on contested
records, and we say so: an earlier draft quoted stronger numbers from an analysis we can no
longer regenerate, so out they went. Regenerate today's with
`python benchmark/confidence_error_auc.py`. On a general mix, easy addresses sit at 0.999+
and separate cleanly; treat confidence as a filter for routing doubtful records to human
review, never as permission to skip it.

## The accuracy record

This section is the project's transparency contract. Every claim links to the artifact that
produced it, and it gets updated whenever a model or evaluation changes. A number here that you
can't regenerate from the repo is a bug; file an issue.

### The two models

| | Default (compat) | v2 (opt-in) |
|---|---|---|
| What it is | DataMade's trained model, [redistributed unmodified](model/PROVENANCE.md) | Retrained by this project (current candidate: [recipe manifest](training/MANIFEST-v43.json)) |
| Output | Bit-identical to usaddress 0.5.16 | Differs on purpose, on documented error classes |
| Status | Shipping | **Not in this release.** Wins on every composed surface; statistically indistinguishable from the default on real free-text. Details below. Ships when that changes, or not at all. |

### How v2 was evaluated

The rules were set before any training happened and are committed at
[eval/PROTOCOL.md](eval/PROTOCOL.md): what the gates are, how records get labeled, who has to
review them, what gets disclosed. The gates don't move once results exist. Two earlier
candidates missed them, and those misses are published in the
[findings report](benchmark/results/model-v2-findings.md) with the same prominence as the pass.

| Gate | Bar | Current candidate (v43) |
|---|---|---|
| Gold-set margin (composed-era set) | at least +3.0pp, 95% CI excluding zero | 74 wins, 0 losses on adjudicated disagreements (14 new ones pending review); passes the bar at the floor. Pass. |
| Clean set (upstream's own held-out files) | within 1.0pp of the original | 159/159, exactly equal. Pass. |
| National scans (16-state, then a 32-state holdout) | net improvement; no state worse than 3:1 | Both pass. |
| 20-county split (spent by v36's one-shot binding run: 70.5% right vs 17.3%) | same two rules | Pass. |
| Real-text dev holdout (2,000 held-out real mail lines) | beat the original, CI excluding zero | +2.400pp, CI [+1.750, +3.100]. Pass. |
| **Gold-2: real free-text, 40 states + DC (two attempts, both spent)** | net margin positive, CI excluding zero; no census division net-negative | Attempt 1 (v36): +0.215pp, CI [-0.861, +1.291] -- fail. **Attempt 2 (v43): +0.789pp, CI [-0.287, +1.865] -- fail.** |

The deciding gold records were judged by a human: seven review rounds so far, models blinded
as A/B, Census records attached as evidence, verdicts and blind keys committed in
[eval/gold/](eval/gold/) and [eval/gold2/](eval/gold2/). Margins here are computed from human verdicts only -- every counted disagreement carries
one. The current candidate's 14 newest divergences are still unreviewed and count for
nothing, which is why its gold-1 row says "passes at the floor" rather than an exact figure. (You'll
find LLM-generated suggestion files in the eval folders too -- those were prelabeling triage,
committed for transparency. The protocol counts human verdicts and nothing else;
[eval/PROTOCOL.md](eval/PROTOCOL.md) is explicit about it.)

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
we don't claim otherwise. The promised state-stratified free-text set now exists
([eval/gold2/](eval/gold2/)); how that exam went is two sections down.

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
per pattern. v28 gave every confusable city guaranteed coverage and passed everything it had been iterated
against -- so we ran a 32-state geographic holdout of states no decision had ever touched, and
it failed there (41.1% right, 45.2% wrong). Three more iterations (v29-v31) fixed the diagnosed
classes and eventually passed the holdout too. But by then the holdout had steered three rounds
of fixes, so it was no longer independent either.

The final check was a third split: 20 fresh counties, never used by anything, one run, rules
committed to git before the result, outcome binding. v31 passed the net rule decisively (47.9%
of its changes right against 17.3%, better in 18 of 20 counties) and **failed the per-state
rule in two counties** (Tucson AZ, 5:41 against; Cobb GA, 4:33). Per the pre-committed rule,
that is the end of the question for this release: **the retrained model does not ship.** The
default model -- bit-identical to usaddress -- is unaffected by any of this, which is exactly
why it is the default.

### The free-text exam, where the winning streak stopped

After v31, the failure classes got a systematic rebuild: type-word and city vocabularies
inventoried from all 3,235 counties' TIGER data, a corpus that guarantees every confusable name
a minimum number of exposures, and a fresh generation of candidates. The survivor, v36, passed
everything the previous generation had failed -- including a second one-shot binding split
(20 fresh counties drawn by a committed seed): 70.5% of its changes right, 17.3% wrong, all 20
counties clean.

Then it took the exam all of that was practice for. Gold-2 is the promised free-text set:
1,394 owner-mailing addresses from 40 states + DC, all nine census divisions, fetched from
county and state open-data portals as assessors actually wrote them, gates pre-registered in
[eval/gold2/PROTOCOL2.md](eval/gold2/PROTOCOL2.md) with a lifetime budget of two scoring
attempts. On attempt 1 the two models disagreed on 62 records; a human adjudicated every one,
blinded. Result: 30 for v36, 27 for the original, 5 neither. That is +0.215pp with a CI of
[-0.861, +1.291] -- statistically nothing -- and the Mountain division net-negative. Fail, on
both gates.

The pattern deserves plain words: a model trained on composed text dominates composed exams and
ties on real text. The one time real adjudicated examples entered training (the gold-1 error
classes), the improvement transferred and held. Synthetic coverage did not transfer.

### The real-text generation, and the final attempt

The response was to train on real text for the first time. 299,832 real owner-mail lines
were fetched from 30 states' open-data portals and labeled by alignment: city/state/zip
taken from the source's own fields, street interiors matched exactly against Census TIGER
records, and every line that didn't match dropped rather than guessed -- 164,879 survived
(55.0%), with per-source yields and drop reasons in
[training/REALTEXT_MANIFEST.json](training/REALTEXT_MANIFEST.json). (The last
heuristically-labeled corpus this project built measured 9.11% wrong. Alignment or nothing.)
A 2,000-row holdout was carved out before any new model existed
([eval/realtext_dev.jsonl](eval/realtext_dev.jsonl)), and the spend rule for the final
gold-2 attempt was frozen first: beat the original on that holdout with a CI excluding
zero, stay green on every earlier surface, and materially exceed v36's +0.900 anchor.

Five candidates later (two more were untrainable in available memory -- documented, not
hidden), v43 met all of it: +2.400pp on the holdout with every one of 48 divergents going
its way, zero regressions on any adjudicated verdict, every composed surface green. It was
the first candidate in the project's history clean everywhere at once. It earned the final
attempt.

Attempt 2, adjudicated blind by a human across all 64 disagreements: 35 for v43, 24 for
the original, 5 neither. Net +0.789pp, CI [-0.287, +1.865]. The interval includes zero.
**Fail.** The division gate passed this time -- attempt 1's Mountain-division failure is
fixed -- and the margin nearly quadrupled (+3 records to +11). But a 64-disagreement exam
cannot certify an effect smaller than about 1.1 points, and +0.789 is under that line. The
rules were set before the results; the result is the result.

So: gold-2 is spent, both attempts disclosed, and the retrained model stays opt-in and
unheadlined. What real-text training measurably did -- the 4x margin move, the fixed
regional failure, the 74-0 hard-case record -- ships as documentation, not as a claim of
national superiority.

The next exam already exists. Gold-2b was fetched and locked before launch: 2,912 records
in its strict cohort across 32 states, drawn only from datasets that neither gold-2 nor any
training corpus ever touched, with the sampling rules and analysis structure committed to
[PROTOCOL2](eval/gold2/PROTOCOL2.md) before a single record was fetched. One source failed
its provenance check during the build (a city layer quietly mixing in excluded-lineage
parcels) and was dropped -- the process working as designed. No candidate has been scored
against it. Two attempts, ever, same as before.

Every candidate, every failed gate, and every hypothesis is in the git history, committed
before its test ran.

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

Every address in this repo comes from public county and state assessor rolls -- records
governments publish precisely so property information can be checked. Where an owner's name
appears in an evaluation file, it is because the assessor published it in the mailing-address
field and the parser has to handle it (a `Recipient` line is a real parsing class). We commit
no data beyond what the source already made public: no SSNs, no non-public fields, nothing
fetched from behind authentication. If your name appears here and you want it replaced with a
placeholder, open an issue -- the eval sets can substitute a record without weakening anything.

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

Issue triage is committed for at least 12 months post-launch, by the repo owner (@vinvomero).
The engine is maintenance-light by design: no retraining pipeline, no external data dependency.
