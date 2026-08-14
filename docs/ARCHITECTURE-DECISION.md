# Why a CRF, and not a transformer

Researched 2026-08-14, when the parser already ran ~96,000 addresses/sec single-core on a
257KB model. The question was whether a different model class would be better.

## The constraints that decide it

Any replacement has to ship inside a pip wheel (no runtime download, no GPU), run offline,
produce deterministic output (the parity guarantee depends on it), and sustain tens of thousands
of addresses per second on one CPU core. Those are not preferences; they are what the project's
speed claim and its reproducibility claim are made of.

## What the evidence says

**Transformers are more accurate on messy input, and it is not close.** The one true
apples-to-apples benchmark ([arXiv 2404.05632](https://arxiv.org/html/2404.05632v1), 2024)
compared parsers on address data of increasing noise:

| Model | F1, clean | F1, noisy | F1, production noise |
|---|---|---|---|
| libpostal (CRF) | **0.992** | 0.781 | 0.675 |
| deepparse (BiLSTM) | — | 0.709 | — |
| DistilBERT | 0.885 | 0.859 | 0.765 |
| XLM-RoBERTa-Large | — | **0.924** | **0.801** |

**But note the first column.** On clean, structured addresses the CRF *wins* — 0.992 vs 0.885 for
DistilBERT. The neural advantage appears only under noise and domain shift. Addresses are short,
highly structured sequences, which is the regime where CRFs have always held up; the transformer
edge is real but specific to mess.

**The speed gap is three to four orders of magnitude.** DistilBERT-class token classifiers run
~8-10 sequences/sec on a single CPU core; Intel's specialized runtime work claims ~4x over ONNX
Runtime, which still lands in the tens per second. GLiNER2 (a 2024-2026 CPU-targeted NER model)
measures 130-208ms per sample, roughly 5-8/sec. Flair manages ~45 sentences/sec. spaCy's
non-transformer CNN pipeline is the fastest neural option at ~10,000 words/sec and still an order
of magnitude short. Nothing in the surveyed field occupies the "neural but CPU-fast" middle.

**Size fails too.** An int8-quantized DistilBERT is ~66MB before the runtime and tokenizer,
against a 257KB CRF in a 0.8MB wheel.

## The lever that does work

Senzing retrained libpostal in May 2025 on 1.2B addresses — **same CRF architecture, no model
change** — and gained +4% accuracy on average, up to +87 percentage points in weak locales. The
accuracy lever compatible with these constraints is training data, not model class. That is
precisely what this project's synthetic-pattern work does, and the round-by-round results in
`model-v2-findings.md` are the local version of the same finding.

## Decision

Keep the CRF. Revisit only if a constraint changes:

- If offline/wheel-size constraints were dropped (a server-side service rather than a library),
  a fine-tuned transformer would be the accuracy play, at ~1000x the compute per address.
- If someone ships a genuinely CPU-fast neural tagger for short sequences, re-run the benchmark.
- An LLM-based parser ([arXiv 2601.18014](https://arxiv.org/html/2601.18014) reports 99.8%
  exact-row accuracy with Claude 3.5 Sonnet) is the accuracy ceiling and is disqualified here on
  latency, cost, offline operation, and determinism — but it is the right tool for reconciling a
  few thousand hard addresses, not for parsing millions.

## Honest gap in this research

No published benchmark gives single-core, ~10-token-sequence throughput for a quantized small
transformer. The order-of-magnitude conclusion is safe (10-100x short at best), but the precise
number is an extrapolation, not a measurement.

---

## Measured: gradient-boosted trees (XGBoost)

Tested directly rather than argued, using the *same* features the CRF sees (including the
previous:/next: context features), so the comparison isolates architecture from feature
engineering. 415,610 labeled tokens, 11,193 feature dimensions, 29 classes.

| | CRF (v19) | XGBoost |
|---|---|---|
| Clean-set exact match | **100.00%** (159/159) | **64.15%** (102/159) |
| Throughput | ~96,000/sec | 95/sec (Python) |
| Model size | 257 KB | 8.2 MB + 11k-entry vocabulary |

The accuracy collapse is structural, not a tuning problem. XGBoost classifies each token
**independently**; the CRF labels the whole sequence jointly via Viterbi. Sequence constraints —
a street type follows a street name, a ZIP follows a state, a building phrase cannot start
mid-street — are exactly what a per-token classifier cannot represent, and exactly what address
parsing depends on. Neighbor features help but do not substitute for joint decoding: a
full-address exact match requires every token right, so independent per-token errors compound.

Reproduce: `python training/experiment_xgboost.py`

## Summary of the option space

| Approach | Accuracy vs CRF | Single-core throughput | Ships in a wheel |
|---|---|---|---|
| **CRF (current)** | baseline | ~96,000/sec | yes, 257 KB |
| XGBoost | **much worse** (measured 64%) | 95/sec | 8 MB |
| BiLSTM (deepparse) | par on clean, worse on noisy | needs PyTorch | no |
| DistilBERT | worse on clean, better on noisy | ~10/sec | ~66 MB, marginal |
| XLM-RoBERTa-Large | better on noisy (0.924 vs 0.781 F1) | far below 10/sec | no |
| LLM prompting | best measured (99.8% exact-row) | API-bound | no (not offline) |

Nothing beats the CRF within the constraints. The accuracy lever that fits is better training
data — see the NAD/TIGER note in the roadmap.
