# Gold-Standard Evaluation Protocol

Pre-registered before any v2 training run (see git history for the commit date). These gates do
not move after results exist.

## The two gates (pre-registered)

1. **Gold-set gate.** v2 ships only if its full-address exact-match rate on the adjudicated gold
   set exceeds the original model's by **at least +3.0 percentage points**, with a bootstrap 95%
   confidence interval on the difference that excludes zero.
2. **Clean-set gate.** v2's exact-match rate on the clean set may not fall more than
   **1.0 percentage point** below the original model's. The clean set is upstream usaddress's
   held-out labeled data (`measure_performance/test_data`, fetched at pinned version 0.5.16),
   which is excluded from all training corpora by normalized-identity dedupe.

Both gates are applied mechanically in the go/no-go unit. A miss shelves the model (the selection
path is reverted/disabled) and the findings are published with the same prominence a ship would
have received.

## Gold set construction

- **Target size:** 1,500 addresses. At plausible base rates (75–90% exact match) this detects a
  3pp difference with a paired-comparison bootstrap comfortably; confidence intervals are
  reported regardless.
- **Sources (true free-text only; composed/distant-supervised text is never eligible):**
  ~60% county owner-mailing addresses (the messiest real source in hand), ~25% the us-addrs
  hard-case corpus, ~15% crash-class and issue-derived hard cases (addresses where the original
  parser errors or is documented to mislabel).
- **Labels:** the 26-label usaddress schema, one label per token, tokens exactly as
  `usaddress.tokenize` produces them.

## Labeling method (disclosed)

1. **Machine prelabel:** each candidate is prelabeled by the original model (usaddress 0.5.16).
   Records where it crashes get no prelabel and require labeling from scratch.
2. **LLM-assisted review:** an LLM pass reviews prelabels against the adjudication rules,
   correcting and flagging; every change is logged.
3. **Human adjudication:** a human reviews every record before it counts. Records carry a
   `status` field — `prelabeled`, `llm_reviewed`, or `adjudicated` — and **only `adjudicated`
   records enter gate arithmetic.**
4. **Agreement:** 10% of records are independently double-labeled; the agreement rate is
   published with the results.

**Known bias, disclosed:** prelabeling with the original model biases uncorrected errors in the
original's favor. This is the conservative direction — it can only understate v2's improvement —
and is accepted deliberately.

## Adjudication rules

- Follow the usaddress label definitions (US Thoroughfare/Postal Address Data Standard mapping)
  as documented upstream; where genuinely ambiguous, prefer the reading a USPS carrier would.
- Two-word place names label every token `PlaceName`; directional words that are part of the
  street's proper name (e.g., "NORTH SHORE DR") label per the standard, not per the vocabulary.
- Unresolvably ambiguous tokens (annotator cannot decide with the rules) are marked and excluded
  from the set; the exclusion count is published.
- `RepeatedLabelError`-class addresses are labeled like any other — the schema permits repeated
  labels; only the original's `tag()` grouping cannot express them.

## Separation guarantees

- No gold or clean address may appear in any training corpus. Identity = uppercased
  alphanumeric-only collapse of the raw string. The corpus builder enforces this and the check is
  part of its test suite.
- Gold records are drawn only from sources that never feed distant supervision (owner-mailing
  free text, us-addrs cases, issue-derived cases). Property-address composed pairs are
  training-only.

## Reporting

`benchmark/run_accuracy.py` produces, for each model on each set: full-address exact match,
per-label precision/recall/F1, and the paired difference with bootstrap CI, split by gold source
type. All public accuracy claims must cite this protocol and the published gold set.
