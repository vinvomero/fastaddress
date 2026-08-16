# Benchmark suite

Reproduce end-to-end: fetch_data.py (public county APIs) -> dump_oracle.py (Python usaddress ground truth, pinned 0.5.16) -> run_parity.py (four-layer differential, CI gate) -> run_speed.py (three-way interleaved best-of-3). Reports land in results/.

## Two kinds of scripts live here

**The public reproduction path** (documented in the README, runs on a fresh clone after
`cargo build --release`): `fetch_data.py`, `dump_oracle.py`, `run_parity.py`, `run_speed.py`,
`compare_marginals.py`, `confidence_error_auc.py`.

**Internal evaluation machinery** (the model-v2 campaign's gates and tooling; several depend
on local caches or spent evaluation surfaces and are kept for auditability, not re-running):
`gauntlet.py` and its six checks (`full_check`, `full_set_margin`, `national_scan`,
`holdout_scan`, `final_validation`, `realtext_dev`), the gold-set fetchers
(`fetch_gold2*.py`, `topup_gold2b.py`), `score_gold2.py`, and the one-off analysis scripts.
The protocols in `eval/` say which surfaces are spent; nothing here may re-score them.
