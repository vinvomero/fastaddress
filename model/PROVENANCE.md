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

## usaddr_v2.crfsuite (the v2 model, opt-in)

`usaddr_v2.crfsuite` (285,396 bytes, sha256 prefix `aa0309cc8a44099f`) is candidate **v23**,
trained by this project on 2026-08-15. Exact recipe in
`training/MANIFEST-usaddr_v23.json`; corpus builders and the full evaluation protocol are in
`training/` and `eval/PROTOCOL.md`.

- Training sources: upstream usaddress MIT training XMLs, distant supervision from county open
  data, shape-preserving augmentation, v1 distillation, and adjudication-derived error-class
  data (`training/synth_error_classes.py` — every generator cites the human ruling or Census
  evidence behind it).
- Gates cleared (pre-registered, human-adjudicated): gold margin +4.73pp against a +3.0pp bar,
  95% CI [+3.67, +5.87]; clean set 159/159, exactly equal to the original.
- Known losses, adjudicated: `1305 Lake Shore Dr N` (genuine post-directional read as a city
  prefix) and `Anchor Point, AK`.
- Disclosure: training targeted error classes surfaced by the gold set itself; see PROTOCOL.md.
  Public phrasing is "measurably better on identified, evidence-backed error classes".
- The pinned original model above is untouched; compat mode still uses it exclusively, and the
  four-layer parity guarantee applies to that path only.
