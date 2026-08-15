# Gold-Standard Evaluation Protocol

Pre-registered before any v2 training run (see git history for the commit date). These gates do
not move after results exist.

## The two gates (pre-registered)

1. **Gold-set gate.** v2 ships only if its full-address exact-match rate on the adjudicated gold
   set exceeds the original model's by **at least +3.0 percentage points**, with a bootstrap 95%
   confidence interval on the difference that excludes zero.
2. **Clean-set gate.** v2's exact-match rate on the clean set may not fall more than
   **1.0 percentage point** below the original model's. The clean set is upstream usaddress's
   `measure_performance/test_data` files that follow the model's own labeling convention
   (`labeled.xml`, `multi_word_state_addresses.xml`, `simple_address_patterns.xml`), excluded
   from all training corpora by normalized-identity dedupe.

   *Changelog (pre-training revision, disclosed):* `us50_test_tagged.xml` was originally
   included, then excluded before any training run when baseline scoring revealed it uses a
   coarser labeling convention than the model's schema (whole street phrases tagged
   `StreetName`, e.g. "Road," — the original model scores ~10% exact match on it purely from
   convention mismatch). It is unusable as an accuracy gate for either model.

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

## Disclosure: training data derived from gold-set error analysis (added 2026-08-15)

From candidate v21 onward, part of the training corpus
(`training/synth_error_classes.py`) targets error classes that were **found by
inspecting failures on the gold set**. That is ordinary error-driven
development, and it is also a form of looking at the test set. It must be
disclosed with any number it produces, because it biases the gold margin
upward: the model was pointed at these classes on purpose.

What the bias does and does not cover:

- **Biased.** The gold-set margin. It measures improvement on classes chosen
  because the gold set exposed them, so it overstates what a fresh sample of
  county addresses would show.
- **Not biased, and this is the control.** The clean set — upstream's own
  held-out files — was never inspected for error classes and no generator was
  written against it. It is scored every run, and a candidate that memorised
  the gold set rather than learning a general pattern would show up as a clean
  regression. v21 did exactly that (155/159) and was rejected for it.
- **Independent grounding.** The classes are not invented from the gold labels.
  Each generator cites either a human adjudication or Census geocoder evidence,
  and the largest class (an abbreviated directional belonging to the city name,
  as in `S BARRINGTON`) is confirmed by the Census geocoder returning
  `city = "S BARRINGTON"` on a per-record basis — evidence that exists
  independently of this evaluation.

Any public claim built on the gold margin must carry this disclosure. The
honest phrasing is that the model was improved on identified, evidence-backed
error classes, and that the gold set measures that improvement rather than a
blind estimate of national accuracy.

## How the gold gate is computed (method note, added 2026-08-14 — the gate itself is unchanged)

The gold gate is a **margin** over the full 1,500-record set. Adjudicating all 1,500 was never
necessary to compute it, and this note records why, because the shortcut is only valid under a
premise that must be checked rather than assumed.

A record where both models emit the *same* parse is either right for both or wrong for both. It
adds the same amount to both sides of `correct(candidate) − correct(incumbent)` and therefore
contributes **exactly zero** to the margin. The margin is fully determined by the records where
the two models differ — which are precisely the records sent to adjudication.

**The premise:** this holds only if *every* differing record carries a verdict. If one does not,
the margin has an unmeasured term and is not exact. `benchmark/full_set_margin.py` recomputes the
differing set from scratch on every run and reports any differing record lacking a verdict, rather
than trusting a stored list. Two earlier "no regressions" claims in this project were wrong
because the check could not see records it never enumerated; this one names its own blind spot.

Consistent with the labeling method above, only human-reviewed verdicts enter the arithmetic.
`--human-only` reports that figure; the unrestricted figure is diagnostic only and is not a gate
result.

## Reporting

`benchmark/run_accuracy.py` produces, for each model on each set: full-address exact match,
per-label precision/recall/F1, and the paired difference with bootstrap CI, split by gold source
type. All public accuracy claims must cite this protocol and the published gold set.
