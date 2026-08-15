# fastaddress

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
import fastaddress  # instead of: import usaddress

fastaddress.tag("123 N Main St Apt 4B Springfield IL 62704")
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
fastaddress.parse_with_confidence("123 N Main St Springfield IL 62704")
# [('123', 'AddressNumber', 0.99995), ('N', 'StreetNamePreDirectional', 0.99452), ...]

tagged, address_type, confidence, sequence_confidence = fastaddress.tag_with_confidence(addr)
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

**Does a low score actually mean a wrong parse?** Measured against the adjudicated records in
[eval/gold](eval/gold), scoring each parse by its least-confident token:

| | |
|---|---|
| Parses judged **correct** (contested records) | mean 0.762 |
| Parses judged **wrong** (contested records) | mean 0.514 |
| Separation (AUC) | **0.833** — 0.5 would mean the score tells you nothing |
| Known-wrong parses scoring above 0.99 | **0 of 47** |
| Clean-set parses (all correct) scoring above 0.99 | 19% |

Read that as a precision/recall tradeoff, not a guarantee: above 0.99 nothing in this sample was
wrong, but only about a fifth of correct parses get there, so it is a high-precision filter for
routing records to review — not a way to keep most of your data unexamined. The first two rows are
measured on contested records only (the hardest addresses in the set), which is the conservative
place to measure: on a general mix, easy addresses score 0.999+ and separate more cleanly.

## Accuracy, evaluation, and data — the full record

This section is the project's transparency contract: every claim links to the artifact that
produced it, and it is updated whenever a model or evaluation changes. If a number here can't be
regenerated from the repo, that's a bug — file an issue.

### The two models

| | Default (compat) | v2 (opt-in) |
|---|---|---|
| What it is | DataMade's trained model, [redistributed unmodified](model/PROVENANCE.md) | Retrained by this project ([recipe manifest](training/MANIFEST-usaddr_v23.json)) |
| Output guarantee | **Bit-identical to usaddress 0.5.16** — four-layer parity, zero divergences on 20,738 addresses ([report](benchmark/results/parity_report.md)) | Differs deliberately on identified error classes |
| Status | Shipping | **In revision — see "National behavior" below. It does not ship until every check passes.** |

### How v2 was evaluated (pre-registered, human-adjudicated)

The evaluation protocol — gates, adjudication rules, and disclosures — was written **before any
training run** and is committed at [eval/PROTOCOL.md](eval/PROTOCOL.md). The gates do not move
after results exist; two earlier candidates (v19, v20) missed them and the misses are published in
the [findings report](benchmark/results/model-v2-findings.md) with the same prominence as the pass.

| Gate | Bar | v23 result |
|---|---|---|
| Gold-set margin | ≥ +3.0pp, 95% CI excluding zero | **+4.73pp**, CI [+3.67, +5.87] — PASS |
| Clean set (upstream's own held-out files) | within 1.0pp of original | **159/159, exactly equal** — PASS |

Every one of the 82 gold records where v23 differs from the original carries a **human verdict**
(5 review rounds, blinded A/B, Census evidence attached; verdicts and blind keys in
[eval/gold/](eval/gold/)). v23 wins 73, **loses 2** — `1305 Lake Shore Dr N` and
`Anchor Point, AK` — both adjudicated and permanent until a future candidate fixes them.

**Disclosure (required with any accuracy number):** v2's training targets error classes that were
found by inspecting gold-set failures, which biases the gold margin upward. The honest claim is
*"measurably better on identified, evidence-backed error classes"* — never a bare accuracy
percentage. The clean set is the uninspected control; it caught one candidate (v21) memorizing
rather than generalizing, at 155/159.

### What the gold set is — and is not

1,500 real free-text addresses: 900 Cook County owner-mailing (878 of them Illinois), 225 NYC,
375 hard cases spanning all 51 states/DC (~7–12 each). **~75% of the set is two states**, and the
win margin inherits that: 34 of v23's 73 wins are one Illinois pattern (abbreviated city prefixes,
`S BARRINGTON`), 31 are New York saint-name streets. This set proves the identified classes are
fixed; it is **not** evidence of nationwide accuracy. A state-stratified free-text gold set is the
next evaluation milestone and will be pre-registered the same way.

### National behavior (the tripwire that caught v23)

Because the gold set is regionally skewed, every candidate also runs a
[16-state behavioral scan](benchmark/national_scan.py): ~108k addresses composed from Census
TIGER data, scoring every record where the candidate changes the original's answer against the
Census's own component labels. **v23 failed it** — 54.9% of its changes were wrong nationally
(it read `New Orleans` as a state, `South Fulton` as a directional, `Box Elder` as a PO box), a
consequence of counterweight training data built from an invented city list. The successor
candidate trains on the real national inventory of confusable place names
([builder](training/build_city_vocab.py)) and must pass two ship rules committed before its
results existed: net national improvement, and no state worse than 3:1 against it. Composed
text never enters gate arithmetic — this scan is a regression tripwire, not an accuracy claim.

### Training data (all sources, all licenses)

| Source | Role | License/status |
|---|---|---|
| usaddress `labeled.xml` + Iowa OpenAddresses XML | base corpus | MIT, upstream repo |
| County parcel rolls (Cook IL, Allegheny PA) | distant supervision, capped | public open data |
| v1-distillation + shape-preserving augmentation | stability | derived |
| Error-class synthetics ([generator](training/synth_error_classes.py)) | targeted fixes | every generator cites the human ruling or Census evidence behind it |
| Census PLACE national city vocabulary | national counterweight | public domain |
| Census TIGER/FEATNAMES street splits | **experiment — not in the shipping recipe**: measured the heuristic corpus 9.11% wrong but its model (v20) regressed | public domain |

No gold or clean evaluation address appears in any training corpus (normalized-identity dedupe,
enforced by the builders). Confidence scores are verified against `pycrfsuite` to 1.665e-15 and
their error-prediction power (AUC 0.833) is measured in the section above.

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
