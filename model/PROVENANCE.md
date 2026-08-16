# Model Provenance

`usaddr.crfsuite` (133,768 bytes) is the trained conditional random field model shipped with
[usaddress](https://github.com/datamade/usaddress) v0.5.16 by DataMade, copied unmodified from the
released PyPI package (`usaddress/usaddr.crfsuite`).

- Upstream license: MIT (permits redistribution with attribution; see upstream repo LICENSE)
- This project redistributes the model unmodified so that the Rust engine produces the same
  predictions as usaddress — parity by construction.
- To refresh: `pip install usaddress==<version>` and copy
  `site-packages/usaddress/usaddr.crfsuite` here; update the version and byte size in this file.
  The parity oracle (benchmark) must be regenerated against the same version.

## usaddr_v2.crfsuite (the v2 model, opt-in, feature-gated)

`usaddr_v2.crfsuite` (371,744 bytes, sha256 prefix `c5cbb26b5fe8586c`) is candidate **v43**,
the final and best candidate of the retraining campaign, trained 2026-08-16. Exact recipe in
`training/MANIFEST-v43.json`; corpus builders and both evaluation protocols are in
`training/`, `eval/PROTOCOL.md`, and `eval/gold2/PROTOCOL2.md`.

Its full record, stated plainly:

- Green on every internal surface simultaneously (the only candidate ever to manage it):
  clean set 159/159; every human-adjudicated gold-1 verdict matched (74 wins, 0 losses);
  both national scans; the spent 20-county binding split; real-text dev holdout +2.400pp,
  95% CI [+1.750, +3.100].
- **Failed the national free-text claim gate** (gold-2 scoring attempt 2 of 2: +0.789pp,
  95% CI [-0.287, +1.865] -- includes zero). Both pre-registered attempts are spent.
- Consequence: this model ships **feature-gated and default-off**, carries no claim of
  national superiority, and the feature stays off in released wheels. It is provided so the
  documented record is testable, not because it cleared the bar. Earlier candidates
  (v23-v42, including v28 which briefly occupied this file) and their failure analyses are
  retained in the repo, manifests, and `benchmark/results/model-v2-findings.md`.
  Public phrasing is "measurably better on identified, evidence-backed error classes".
- The pinned original model above is untouched; compat mode still uses it exclusively, and the
  four-layer parity guarantee applies to that path only.
