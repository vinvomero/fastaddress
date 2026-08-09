# Contributing

The one rule: **parity is the product.** Every change must leave the four-layer differential
suite at zero divergences (`python benchmark/run_parity.py`), and performance changes must not
buy speed with correctness (`benchmark/run_speed.py` reports both).

- Bug in parsing? If usaddress produces the same output, it's a model behavior, not a bug here —
  file it as a native-mode improvement proposal instead.
- New feature? Native mode is where improvements live; compat mode is frozen to usaddress 0.5.16
  semantics.
- Run `cargo test --workspace` and the parity suite before opening a PR.
