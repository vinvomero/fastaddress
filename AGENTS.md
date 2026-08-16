# Agent guide: fastaddress

Instructions for AI coding agents (and humans in a hurry). This repo is a Python package
with a Rust engine. Everything you need to install, verify, and work on it is below.

## Install

Fastest path, no Rust toolchain needed — grab a wheel from the latest GitHub release:

```bash
pip install https://github.com/vinvomero/fastaddress/releases/latest/download/WHEEL_NAME.whl
```

(Pick the wheel matching the OS/Python from the release assets list.)

Build from source — requires a Rust toolchain (https://rustup.rs), everything else is
handled by pip's build isolation:

```bash
pip install git+https://github.com/vinvomero/fastaddress
```

The root `pyproject.toml` points maturin at `crates/python/Cargo.toml`, so the plain
git+ URL works with no subdirectory tricks. Release-profile compile takes a few minutes.

## Verify the install

```bash
python -c "import fastaddress; print(fastaddress.tag('123 N Main St Springfield IL 62704'))"
```

Expected: a (dict, 'Street Address') pair whose contents equal `usaddress.tag`'s output
(fastaddress returns a plain insertion-ordered dict, not OrderedDict). For the full drop-in check (needs `pip install usaddress` too):

```bash
python crates/python/tests/test_dropin.py
```

## What this package is

- `fastaddress.parse / tag / tag_mapping semantics / RepeatedLabelError` — byte-identical
  to `usaddress` 0.5.16 on ASCII-dominant input, 11.3x faster single-core. Same model, redistributed
  unmodified (`model/PROVENANCE.md`).
- `parse_with_confidence / tag_with_confidence` — per-token CRF marginal probabilities.
- `tag_native` — no-crash variant for inputs that raise `RepeatedLabelError` upstream.
- `model=` keyword on all six functions selects a built-in model by id (`"v1"` default;
  `"v2"` only in feature-enabled builds -- it raises ValueError in the shipping wheel).

## Repo layout

| Path | What |
|---|---|
| `crates/core` | Tokenizer, feature extraction, tagging pipeline (Rust) |
| `crates/crf` | Vendored CRF engine: model reader, Viterbi, marginals (Rust) |
| `crates/python` | PyO3 bindings -> the `fastaddress` wheel |
| `model/` | Shipping model + provenance |
| `benchmark/` | Speed + parity + accuracy evaluation harnesses |
| `training/` | Corpus builders and training pipeline for candidate models |
| `eval/` | Gold evaluation sets, protocols, human verdicts |
| `docs/plans/` | Engineering plans (decision artifacts) |

## Rules that protect the project's credibility

The evaluation system runs on pre-registration: gates are committed to git BEFORE
results exist, and spent evaluation surfaces are never re-scored. If you are an agent
working in this repo:

- Never edit `eval/PROTOCOL.md` / `eval/gold2/PROTOCOL2.md` status logs except to append.
- Never score a candidate against `eval/gold2b/` — its two scoring attempts are budgeted
  and human-gated (see PROTOCOL2). The dev-tier surfaces in `benchmark/` are the
  iterate-freely ones; `benchmark/gauntlet.py --candidate <model>` runs them all.
- Every number in README.md must be regenerable from committed artifacts. If you change
  a model or an eval, update the README accuracy record in the same change.
- Training corpora under `training/corpus/` are gitignored on purpose (size); the
  builders + manifests are the committed source of truth.

## Build notes

- Workspace builds: `cargo build --release` at root. The Python wheel: `maturin build
  --release -m crates/python/Cargo.toml`.
- CI (`.github/workflows/wheels.yml`) runs a four-layer parity gate + drop-in tests and
  builds wheels for Linux/Windows/macOS on every `v*` tag.
