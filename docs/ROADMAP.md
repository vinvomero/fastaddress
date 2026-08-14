# Roadmap

Grounded in an analysis of the [upstream usaddress issue tracker](https://github.com/datamade/usaddress/issues)
(fetched 2026-08-12 via the GitHub API: 170 open issues reviewed; 37 addressed by this project's
v1, 7 cheaply addressable, 112 model-level, 14 out of scope). Performance and parity figures below
are this repo's measurements: [benchmark/results/speed_report.md](../benchmark/results/speed_report.md)
and [benchmark/results/parity_report.md](../benchmark/results/parity_report.md). The rule from CONTRIBUTING.md governs everything here: parity is the product; compat-mode
behavior is frozen to usaddress 0.5.16, and improvements live in native mode or opt-in layers.

## v1.0 (built, unreleased)

- Rust engine running the usaddress-trained CRF model with four-layer verified output parity
  (20,738-address corpus + 738 us-addrs regression cases, zero divergences)
- 10x single-core like-for-like; 210k+/sec multi-threaded
- Drop-in Python wheel (tag/parse/tag_mapping/RepeatedLabelError), 0.8MB, no build toolchain —
  resolves upstream's crash class (26 reports since 2017, incl. #180) and install class (#229, #347)
- Native mode: never raises on valid input (also covers upstream #160, multiple occupancies)

- **Confidence scores** (upstream #337): CRF marginal probabilities per tag and per parse. No
  retraining; parity untouched; answers "should I trust this parse?" The highest
  demand-per-effort item in the upstream tracker, so it ships with v1.0 rather than after it.

## v1.1

- **Exception fidelity**: `original_string` / `parsed_string` attributes on the Python
  `RepeatedLabelError` (drop-in gap).
- **`bytes` input** accepted like usaddress's tokenize does (drop-in gap).

## v1.2

- **USPS normalization layer** (upstream #331, #226): opt-in post-processing — abbreviation
  expansion (St→Street), Pub-28-style casing. Rules only; no model change; clearly separated from
  compat output.
- Free-threaded (abi3t) wheels when audience demand appears.

## Model accuracy (gated — see origin requirements R11; in progress, not yet cleared)

Targets the upstream tracker's 112 mislabeling issues (two-word places, directionals, highways).
Gated on an independently auditable gold-standard label set with published methodology
([eval/PROTOCOL.md](../eval/PROTOCOL.md)). **No accuracy claims without it, and the gate has not
been cleared.**

- Candidate v19 never regresses but **misses the pre-registered +3.0pp gold gate** — margin
  +2.60pp all-verdicts, and arithmetically capped at +2.80pp even if every outstanding record is
  adjudicated in its favour. It fixes 39 of 1,500; the bar needs 45.
  ([findings](../benchmark/results/model-v2-findings.md))
- **Census TIGER/Line training corpus** — moved ahead of the other model work because it is the
  only lever that raises the *count* of records fixed. The prior corpus split street phrases with
  a heuristic that mislabels 9.11% of them against TIGER ground truth; 71% of those errors are
  trailing directionals in grid addresses, the largest remaining class.
  ([builder](../training/build_tiger_corpus.py))
- Outstanding: human adjudication of the differing records the protocol requires before any
  margin counts ([worklist generator](../tools/make_confirmation_doc.py)).
- Constrained decoding for partially-structured input (upstream #94, the tracker's oldest issue).

## Ongoing

- Goodwill PRs upstream: benchmark suite to datamade/usaddress; inference optimizations
  (pre-decoded tables, id API, 26-label Viterbi arm) to messense/crfs-rs.
- Issue triage per the 12-month commitment in the README.
- Oracle re-pin if usaddress ships a new release (benchmark/requirements.txt governs).

## Non-goals

- Multinational parsing (libpostal's scope)
- LLM-based parsing
- Any accuracy claim not backed by the gated eval set
