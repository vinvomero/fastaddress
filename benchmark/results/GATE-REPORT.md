# Pre-Build Gate Report — usaddress baseline

Date: 2026-08-09 · Machine: single core, Python 3.13, usaddress 0.5.16
Data: 20,000 addresses from three public county sources (fetched via `benchmark/fetch_data.py`; reproducible)

## Measurements

| Dataset | n | Throughput (addr/sec, 1 core) | Hard parse failures | Structural anomalies* |
|---|---|---|---|---|
| Allegheny County PA (property) | 5,000 | ~9,300 | 0.00% | 0.04% |
| Cook County IL (property) | 5,000 | ~3,900 | 0.00% | 0.24% |
| Cook County IL (owner mailing — messy free-text) | 5,000 | ~4,600 | 0.06% | 1.46% |
| NYC (PLUTO) | 5,000 | ~6,200 | 0.66% | 0.22% |

*Structural anomalies = no street name tagged, or house number present but not tagged. Includes
legitimate non-street addresses (PO boxes, landmarks), so this over-counts true errors.

Observed real error classes: saint-name streets ("ST JAMES PLACE") crash with RepeatedLabelError;
directional-as-street-name confusion ("720 SOUTH ST"); landmark/no-number addresses (plazas, "7 WORLD
TRADE CENTER"); range house numbers ("115 -119 FORBES AVE") unassessed without gold labels.

## Verdict

- **Accuracy-led narrative: NOT supported.** Measured error headroom on tax-roll-shaped data is
  roughly 0.2–1.5%, and part of that is heuristic noise. usaddress is much better on this data than
  its reputation suggests. A gold-label eval (R11) could still surface label-level errors these
  heuristics can't see, but the burden was to find large headroom — it wasn't found.
- **Speed-led narrative (the launch-carrying story per the re-tiered requirements): supported.**
  Single-core baseline is ~4–10k addresses/sec. A compiled rewrite at 250k–1M/sec would support a
  credible 25–100x like-for-like headline with exact clean-data parity as the trust mechanism.
- **Caveats carried forward:** speed may not be a *felt* pain for all usaddress users (adversarial
  residual); the crash class (saint-names) and range-number handling are genuine quality wins a
  rewrite can bank even without claiming broad accuracy superiority — "never crashes on valid
  addresses" is itself a story element.

## Recommendation

Proceed to planning the parser build with the speed + parity + robustness framing. Do not lead with
accuracy claims; treat the R11 gold-label eval as the stretch-goal gate the requirements already
define. The known crash/error classes above become named test cases.
