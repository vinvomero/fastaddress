# Roadmap

Grounded in an analysis of the [upstream usaddress issue tracker](https://github.com/datamade/usaddress/issues)
(fetched 2026-08-12 via the GitHub API: 170 open issues reviewed; 37 addressed by this project's
v1, 7 cheaply addressable, 112 model-level, 14 out of scope). Performance and parity figures below
are this repo's measurements: [benchmark/results/speed_report.md](../benchmark/results/speed_report.md)
and [benchmark/results/parity_report.md](../benchmark/results/parity_report.md). The rule from CONTRIBUTING.md governs everything here: parity is the product; compat-mode
behavior is frozen to usaddress 0.5.16, and improvements live in native mode or opt-in layers.

## v1.0 (built, unreleased)

- Rust engine running the usaddress-trained CRF model with four-layer verified output parity
  (20,738-address corpus (including 738 us-addrs regression cases), zero divergences)
- 11.3x single-core like-for-like; 360k/sec multi-threaded (native engine)
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

## Model v2 (NOT in this release — both claim-tier attempts spent)

The retrained model does not ship. The final candidate, **v43**, is green on every internal
surface (clean 159/159, 74-0 on adjudicated hard cases, both national scans, +2.4pp on the
held-out real-text set) and still could not statistically prove its edge on the national
free-text exam: gold-2 attempt 2 of 2 came in at +0.789pp with a CI including zero. Under the
pre-registered rules ([findings](../benchmark/results/model-v2-findings.md),
[PROTOCOL2](../eval/gold2/PROTOCOL2.md)), that is a fail, both scoring attempts are spent, and
any future claim requires the already-built gold-2b set. The v43 artifact and full recipe stay
in the repo as documented candidates. An earlier candidate (v23) cleared the first-generation
gates and then failed the national scans — that history is in the findings report.

Public claims must carry the PROTOCOL.md disclosure: training targeted error classes surfaced by
the gold set itself, so the phrasing is "measurably better on identified, evidence-backed error
classes" — never a bare accuracy percentage. The improvement classes: abbreviated city prefixes
(S BARRINGTON), grid pre-directionals (295 South 250 East), saint-name streets, bare street names
(BROADWAY), abbreviated unit designators, milepost routes, truncated street types.

Still model-level, unaddressed: the 8 adjudicated both-wrong records, and the remaining upstream
mislabeling issues outside these classes. Post-launch candidates:

- A geographically representative second gold set (the current one is Midwest/Northeast-heavy and
  nearly blind to Western grid addressing — measured, 36 grid records of 1,500).
- Census TIGER/FEATNAMES corpus at national scale, with mixed spelled-out state names (the v20
  experiment documents both its promise — 9.11% heuristic error corrected — and its trap).
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
