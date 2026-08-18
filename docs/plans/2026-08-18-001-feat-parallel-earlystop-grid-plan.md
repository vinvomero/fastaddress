---
title: "feat: Parallel + early-stop grid runner for candidate training"
type: feat
status: active
date: 2026-08-18
origin: humanlabel campaign iteration-speed request
---

# feat: Parallel + early-stop grid runner

## Summary

Candidate grids currently run as bash loops that train one cell, score it, then train the
next. At v19 scale (~300k sequences per cell) each cell is ~25 minutes, so a three-cell grid is
~75 minutes of mostly-idle CPU on an 8-core machine. Two independent speedups apply, and they
compose: run the cells concurrently (the cells fit in memory now; the sequential habit is a
leftover from the 720k-sequence v43 era), and stop each LBFGS run when its loss plateaus instead
of always burning all 200 iterations. Together they take a three-cell grid from ~75 minutes to
roughly 15-20, with no change to the evaluation method.

The hard constraint: **neither speedup may change the model in a way that shifts the gold-2c
numbers.** The whole campaign rests on an apples-to-apples comparison against v19 and v1, so
early-stop is validated against a full-iteration run before it is trusted, and parallelism is
verified to produce byte-identical models to sequential.

## Problem Frame

- Sequential grids waste ~6 of 8 cores. Cells at ~300k sequences use ~1.5-2 GB each; the OOM
  that forced sequential training happened at 720k (v43 scale), which no longer applies.
- LBFGS is capped at `max_iterations=200` with the CRFsuite default stopping `delta=1e-5`.
  Near-converged runs spend their last several dozen iterations moving the loss by less than
  that threshold would demand if it were checked more aggressively.
- Training time is not the campaign's true bottleneck (human labeling is), so this is a
  quality-of-life speedup, not a critical path. It must not cost correctness to buy speed.

## Requirements

- **R-A**: A grid runner that trains N cells concurrently, capped by a memory-and-core budget,
  scores each survivor on gold-2c (per class), the clean set, and adjudicated records, and
  prints one combined table. Same numbers a sequential run would produce.
- **R-B**: An opt-in early-stop lever on `train.py` (a tunable LBFGS `delta`), off by default so
  existing reproducible runs are unchanged.
- **R-C**: Early-stop is validated before use: a cell trained with it must match the same cell
  trained to full convergence on gold-2c within noise (identical, ideally), and the check is
  recorded. If it shifts the numbers, it is not adopted.
- **R-D**: Parallelism produces the same model as sequential for the same cell (byte-identical
  artifact, since training is deterministic given fixed inputs and single-threaded per process).
- **R-E**: A hard concurrency cap so a grid can never OOM the machine; the cap is computed from
  available memory and cores, not hardcoded.

## Key Technical Decisions

1. **Python orchestrator, not a bash loop.** A small `benchmark/grid.py` owns cell definitions,
   the concurrency pool, memory-aware scheduling, result collection, and the combined report.
   Bash cannot cap concurrency by live memory or collect structured results cleanly.
2. **One process per cell, single-threaded each.** pycrfsuite/CRFsuite LBFGS is effectively
   single-threaded, so parallelism is across cells (process-level), not within a train. This
   keeps each model byte-identical to a sequential run (determinism preserved) and makes the
   memory math simple: concurrency = min(cores - 2, floor(free_mem / per_cell_budget), n_cells).
3. **Early-stop via CRFsuite's own `delta`/`period`, not a custom loop.** Expose `--delta` on
   train.py (default keeps today's behavior). Raising delta makes LBFGS stop when the relative
   loss improvement over `period` iterations falls below it. This is a built-in, documented
   CRFsuite stopping criterion, not a hack, so it stays reproducible.
4. **Validate early-stop empirically before trusting it.** Train one representative cell at the
   default delta and at the aggressive delta; compare gold-2c overall and per class, clean set,
   and adjudicated count. Adopt the aggressive delta only if the numbers are identical or move
   strictly within the bootstrap CI. Record the comparison in the plan's verification.
5. **Scoring stays exact.** The runner calls the existing `gold2c_dev.py`, `full_check.py`, and
   (optionally) the other surfaces unchanged. No new evaluation logic, so no new way to be wrong.

## Implementation Units

### GRID-U1. Early-stop lever on train.py

**Goal:** `--delta` flag on `train.py`; default reproduces current models exactly.
**Requirements:** R-B.
**Files:** `training/train.py`.
**Approach:** Add `--delta` (float, default `None`). When set, pass `"delta": args.delta` into
the pycrfsuite `set_params` dict (LBFGS reads it alongside `period`, default 10). Record the
value in the manifest. Default `None` omits the key, so training is byte-identical to today.
**Test scenarios:** with `--delta` unset, a trained artifact's sha256 matches a pre-change build
of the same cell (determinism/no-op proof); with `--delta 1e-4`, training completes in fewer
iterations (train_seconds drops) and the artifact still loads and tags.
**Verification:** manifest shows the delta; no-op proof holds.

### GRID-U2. Early-stop validation

**Goal:** Evidence that the aggressive delta does not move the evaluation.
**Requirements:** R-C. **Dependencies:** U1.
**Files:** none new (uses existing scorers); result recorded in this plan and a short note in
`training/humanlabel/` or PROTOCOL-adjacent doc.
**Approach:** Pick one representative cell (v19 recipe + humanlabel at the current best weight).
Train it twice: default delta (full convergence) and `--delta 1e-4`. Score both on gold-2c
(overall + per class), clean set, adjudicated count. Compare.
**Test scenarios:** gold-2c overall net identical or within CI; per-class counts unchanged;
clean set unchanged; adjudicated count unchanged; train_seconds materially lower for the
early-stop run.
**Verification:** the comparison table is recorded; adopt-or-reject decision is written down.

### GRID-U3. Parallel grid runner

**Goal:** `benchmark/grid.py` trains cells concurrently under a memory cap and prints a combined
scored table.
**Requirements:** R-A, R-D, R-E. **Dependencies:** U1 (so cells can opt into early-stop).
**Files:** `benchmark/grid.py` (new).
**Approach:** Accept a cell spec (a small list of dicts, or CLI: base flags + a list of
`--humanlabel` weights, plus optional shared `--delta`). Compute the concurrency cap from
`os.cpu_count()` and available memory (via `psutil` if present, else a conservative fixed cap),
using a measured/estimated per-cell budget (~2 GB). Launch cells with
`concurrent.futures.ProcessPoolExecutor` or bounded `subprocess.Popen` slots, each invoking
`train.py` with `--out model/candidates/<name>.crfsuite`. As each finishes, run the scorers.
Collect and print one table: cell, train_seconds, gold-2c net + per-class, clean, adjudicated.
Never exceed the cap; log the chosen concurrency and the reason.
**Test scenarios:** a 3-cell grid with cap 3 runs all three concurrently and the three artifacts
are byte-identical to the same cells trained sequentially (determinism proof); with a cap of 1
it degrades to sequential and still produces the same models; a cell that dies (OOM/kill) is
reported as failed without taking down the others; the combined table matches hand-run scores.
**Verification:** determinism proof (parallel == sequential artifacts); wall-clock materially
below the sequential baseline; no OOM at the chosen cap.

## Scope Boundaries

**In scope:** cell-level parallelism, the built-in LBFGS early-stop lever, a memory-aware
runner, and validation that neither changes the numbers.
**Out of scope, deliberately:** minfreq feature pruning and switching LBFGS to l2sgd -- both are
faster but change the model, which would break the v19/v1 comparison the gold-2c method depends
on. Not adopted, by design. Also out: within-train multithreading (CRFsuite does not support it
meaningfully) and GPU (wrong algorithm class).
**Non-negotiable:** the default `train.py` invocation stays byte-identical to today; speed is
never bought with a silent model change.

## Risks & Mitigations

- **Early-stop shifts results.** Caught by U2's explicit before/after comparison; if it moves
  anything outside noise, the aggressive delta is rejected and only parallelism is kept.
- **Parallel runs OOM.** The concurrency cap is computed from live free memory with a per-cell
  budget and a safety margin; a cell that still dies is isolated and reported, not fatal to the
  grid.
- **Non-determinism from parallelism.** Each cell is its own single-threaded process with fixed
  inputs, so artifacts are byte-identical to sequential; the determinism proof in U3 is the
  guard, and if it ever fails the runner falls back to sequential.
- **psutil not installed.** The runner degrades to a conservative fixed cap (e.g., 3) rather
  than failing, so it works on a bare environment.
