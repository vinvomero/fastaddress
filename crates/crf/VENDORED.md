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

All changes preserve arithmetic order; correctness is enforced by this repo's four-layer oracle
parity gate and the full-corpus ID-vs-string equivalence test.
