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

`usaddr_v2.crfsuite` (320,360 bytes, sha256 prefix `89d99e84607fa34e`) is candidate **v28**,
trained by this project on 2026-08-15. Exact recipe in
`training/MANIFEST-usaddr_v28.json`; corpus builders and the full evaluation protocol are in
`training/` and `eval/PROTOCOL.md`. Five earlier candidates (v23-v27) cleared subsets of the
checks and failed others; their artifacts, manifests, and failure analyses are retained in the
repo and findings report.

- Training sources: upstream usaddress MIT training XMLs, distant supervision from county open
  data, shape-preserving augmentation, v1 distillation, and adjudication-derived error-class
  data (`training/synth_error_classes.py` — every generator cites the human ruling or Census
  evidence behind it).
- Gates cleared (pre-registered, human-adjudicated): gold margin +4.80pp against a +3.0pp bar,
  95% CI [+3.74, +5.94], floor +4.67 with all unadjudicated records counted against; clean set
  159/159, exactly equal to the original; 16-state national scan 81.9% right vs 12.0% wrong on
  divergent records, no state worse than 3:1.
- Known loss, adjudicated: `Anchor Point, AK`.
- Disclosure: training targeted error classes surfaced by the gold set itself; see PROTOCOL.md.
  Public phrasing is "measurably better on identified, evidence-backed error classes".
- The pinned original model above is untouched; compat mode still uses it exclusively, and the
  four-layer parity guarantee applies to that path only.
