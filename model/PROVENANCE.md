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
