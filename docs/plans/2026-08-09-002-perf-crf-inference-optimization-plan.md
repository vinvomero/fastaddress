---
title: "perf: CRF inference optimization to clear the 10x single-core bar"
type: perf
status: completed
date: 2026-08-09
origin: C:/Users/vvome/docs/brainstorms/2026-08-09-us-address-parser-requirements.md
---

# perf: CRF inference optimization to clear the 10x single-core bar

## Summary

Vendor the MIT-licensed `crfs` crate into the workspace and eliminate its per-call inference costs — string lookups, allocations, and buffer re-parsing — to move the wheel from 5.4x to a target ≥10x single-core like-for-like, with parity guarantees unchanged.

## Problem Frame

Honest quiet-machine measurement: wheel 50.9k/sec vs usaddress 9.5k/sec single-core (5.4x). Stage decomposition puts tokenize+features at ~6µs/call and CRF inference at ~12.5µs. Reading `crfs` 0.4.1 source (`tagger.rs`), each `tag()` call: (1) resolves every attribute name through a cqdb string lookup (~190/call), (2) allocates a fresh `Instance` and `ViterbiState`, (3) re-parses feature records from the raw model buffer through `io::Result`-checked accessors inside the scoring inner loop (`state_score` → `model.feature(fid)?` per feature per attribute), and (4) resolves label ids to strings per call. None of this changes the math; all of it is per-call overhead a fork can remove. Target arithmetic, with the moved cost budgeted honestly: attribute-ID resolution doesn't vanish — it shifts into the feature stage as cache lookups. With bounded families precomputed and only `word:*` memoized (~30 fast-hash lookups/call), the budget is ~6–7µs features+lookups + 2–4µs inference ≈ 90–125k/sec → 9.5–13x. The 26-label Viterbi unroll (U2) protects the low end.

---

## Requirements

- R1. Single-core like-for-like throughput ≥10x usaddress under the existing fair methodology (interleaved best-of-3, full corpus, quiet machine); if the result lands in 8–10x, stop and surface the decision (advances origin R2).
- R2. The four-layer oracle parity gate stays at zero divergences on the string path.
- R3. A new in-process equivalence test proves the optimized ID path produces labels identical to the string path across all 20,738 corpus addresses plus the us-addrs cases.
- R4. The vendored crate keeps its MIT license and attribution (origin R8); changes are documented for a potential upstream PR, consistent with the credit-and-continuation framing (origin R6).
- R5. Public API, wheel surface, and benchmark methodology are unchanged.

## Key Technical Decisions

- **Vendor `crfs` 0.4.1 into `crates/crf`** rather than wait on upstream. MIT permits it; attribution preserved; upstream PR offered afterward as goodwill (confirmed at synthesis).
- **Pre-decode the model at load time.** Materialize per-attribute feature lists into flat `(target, weight)` arrays and the label table into owned strings once, at `Model::new`. The 134KB model expands to a few MB at most; the scoring loop becomes branchless array walks instead of `Result`-checked buffer parsing. Expected largest single win.
- **ID-level tagging API.** Expose `tag_ids(&mut self, &[Vec<(u32, f64)>]) -> Vec<u32>` with reusable internal scratch. The core's thread-local changes from `OnceCell<Tagger>` to `RefCell<Option<Tagger>>` (`borrow_mut` per call; per-thread, no contention) to permit the mutable receiver. String `tag()` keeps `&self` with internally allocated scratch — it only serves the dump/oracle path where per-call cost is irrelevant.
- **Attribute-ID cache in the feature extractor.** Fixed attribute names (booleans, `digits:*`, flags, context prefixes) resolve to ids once at startup. Bounded families are precomputed into tables at init, not memoized: `length:{d,w}:N` (N capped by observed token lengths), `endsinpunc:<char>` (ASCII punctuation), `trailing.zeros:<run>` (bounded digit runs). Only `word:*` is genuinely memoized, in a per-thread fast-hash map (FxHash-class, not SipHash) — ~30 lookups/call, not ~120. Misses (including words unknown to the model) are negative-cached; the map is capped (~2x the model's attribute count), past which lookups fall back to cqdb so adversarial input degrades in speed, never in memory. Cache misses produce behavior identical to today — the string path via cqdb.
- **Scoring order preserved.** Attributes are fed in the same order as today so f64 accumulation order is unchanged — label equality (R3) is then exact, not approximate.
- **String path retained** for the dump binary and oracle diffs; production (API/wheel) uses the ID path. R3's equivalence test is what extends the parity guarantee across the two paths.

---

## Implementation Units

### U1. Vendor crfs into the workspace

- Goal: `crates/crf` contains crfs 0.4.1 verbatim (license, attribution note, source URL); workspace and `usaddr-core` build against it; all existing tests and the parity gate pass unchanged.
- Requirements: R4, R2
- Dependencies: none
- Files: `crates/crf/*` (vendored), `Cargo.toml`, `crates/core/Cargo.toml`, `crates/crf/VENDORED.md`
- Test scenarios: full `cargo test --workspace` green; oracle parity run zero divergences; wheel builds.
- Verification: byte-identical behavior — this unit changes provenance only.

### U2. Pre-decoded tables and ID-level API

- Goal: model load materializes feature/label tables; `tag_ids` with scratch reuse exists; `tag()` reimplemented over it with identical results.
- Requirements: R2, R3 (foundation)
- Dependencies: U1
- Files: `crates/crf/src/model.rs`, `crates/crf/src/tagger.rs`, `crates/crf/src/context.rs` (scratch reuse + 26-label arm), `crates/core/src/model.rs` (thread-local becomes `RefCell<Option<Tagger>>`), `crates/crf/tests/id_api.rs`
- Approach: decode once in `Model::new`; `Tagger` owns reusable `Instance`/`ViterbiState` buffers (clear, don't reallocate); label table pre-resolved to `String`s returned as `&str`. Add a `26 =>` arm to the unrolled-Viterbi match in `context.rs` — the vendored crate specializes only up to 16 labels, so the usaddress model's 26 labels currently fall to the generic scalar loop; the arm uses the existing unrolled path with identical arithmetic order (covered by R3).
- Test scenarios: `tag()` on the U1 fixture unchanged; `tag_ids` with ids resolved via cqdb equals `tag()` on the same input; empty sequence returns empty; repeated calls on one tagger reuse buffers without state bleed (tag A, tag B, tag A again — results stable).
- Verification: oracle parity still zero; microbench shows `tag()` per-call time reduced.

### U3. Attribute-ID cache in feature extraction

- Goal: production path emits `(id, weight)` directly — fixed names resolved at init, open-ended names memoized per thread — with the string path preserved for dump/oracle.
- Requirements: R3, R5
- Dependencies: U2
- Files: `crates/core/src/features.rs`, `crates/core/src/attr_cache.rs`, `crates/core/src/api.rs`, `crates/core/tests/id_equivalence.rs`
- Approach: `token_attr_ids()` mirrors `token_attrs()` structurally (same emission order); context-prefixed variants (`previous:`/`next:`) get their own cached ids; unknown-to-model attributes are dropped exactly as `to_attr_id` misses are today.
- Execution note: keep both paths generated from shared per-feature logic where practical so they cannot drift silently; the equivalence test is the enforcement.
- Test scenarios: R3's full-corpus equivalence test (ID-path labels == string-path labels for every row of every dataset, in-process); cache-miss fallback exercised (synthetic unseen word); negative-cache behavior (repeated unknown word resolves once); cap overflow (fill past the cap with distinct garbage words, correctness preserved, map stops growing); per-thread cache isolation under `std::thread` parallelism.
- Verification: equivalence test green corpus-wide; parity gate zero.

### U4. Re-benchmark and go/no-go

- Goal: definitive numbers under the unchanged fair methodology; reports and README updated; verdict against R1.
- Requirements: R1
- Dependencies: U3
- Files: `benchmark/results/speed_report.md` (regenerated), `README.md` (numbers only), `crates/crf/VENDORED.md` (upstream-PR notes)
- Test scenarios: none — measurement unit. `Test expectation: none — measurement and docs only.`
- Verification: quiet-machine run; if ≥10x, update README headline; if 8–10x, stop and present the decision; below 8x, stop and reassess the approach.

---

## Scope Boundaries

Origin scope boundaries stand unchanged (multinational, accuracy stretch, CAMA space all still out). **Deferred to Follow-Up Work — new deferrals specific to this optimization phase:** upstream PR to messense/crfs-rs offering the pre-decode + ID API + 26-label arm (after numbers land); true SIMD Viterbi (only if U4 misses); free-threaded wheels, naming, release home (already tracked).

## Risks & Dependencies

- **f64 accumulation-order drift** would break exact label equality — mitigated by preserving attribute emission order (KTD); the R3 test catches any slip corpus-wide.
- **Two-path drift over time** (string vs ID) — mitigated by shared emission logic and the equivalence test running in CI with the parity gate.
- **Diminishing returns**: if pre-decode + caching lands under 8x, remaining cost is in Viterbi/feature-extraction fundamentals; U4's stop rule prevents sunk-cost creep.

## Sources & Research

- `crfs` 0.4.1 source read this session: `tagger.rs` (`tag`, `state_score`, per-call `Instance`/`ViterbiState`), model accessor patterns — local registry copy
- Stage decomposition measurements: `benchmark/results/speed_report.md`, BENCH_STAGE runs (features ~6µs, inference ~12.5µs of 18.5µs/call)
- Origin requirements and completed v1 plan: `docs/plans/2026-08-09-001-feat-rust-address-parser-plan.md`
