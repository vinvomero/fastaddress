# Vendored: crfs 0.4.1

Vendored unmodified from [messense/crfs-rs](https://github.com/messense/crfs-rs) (crates.io
`crfs` 0.4.1, MIT — see LICENSE in this directory) on 2026-08-09, then extended for this
project's inference-speed requirements. Local changes (each a candidate for an upstream PR):

- Pre-decoded feature/label tables at `Model::new` (removes per-access buffer parsing in the
  scoring loop)
- `tag_ids` API with reusable scratch buffers (removes per-call allocations and per-attribute
  cqdb string lookups for callers that cache attribute ids)
- 26-label arm in the unrolled Viterbi match (the usaddress model's label count previously fell
  to the generic path)
- Forward-backward marginals: `MarginalState`, `Context::forward_backward`, `Context::score`, and
  the `Tagger::tag_ids_with_marginals` entry point. Upstream crfs never ported CRFsuite's
  `crf1dc_alpha_score` / `crf1dc_beta_score`, so the `MARGINALS` flag and its context fields were
  inert. Scaled (not log-space) forward-backward, matching CRFsuite, with one deviation: the
  per-position state-score maximum is subtracted before `exp` and added back into `log_norm`.
  Marginals are exactly invariant under that shift, and it keeps `exp` away from overflow.
  Strictly additive — `tag`, `tag_ids` and their buffers are untouched.

All changes preserve arithmetic order; correctness is enforced by this repo's four-layer oracle
parity gate and the full-corpus ID-vs-string equivalence test. The marginals are additionally
checked against brute-force enumeration of all label sequences on the bundled 2-label toy model
(`tagger::tests::marginals_match_brute_force_enumeration`) and against `pycrfsuite.Tagger`
(`benchmark/compare_marginals.py`).
