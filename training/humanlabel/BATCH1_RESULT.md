# Batch 1 result: 840 human labels, v19 + humanlabel weight grid on gold-2c

Baselines: v1 = 38/47 suffix-present; v19 = +2 overall, 42/47 suffix-present, 36 adjudicated fails.

| cell | gold-2c net | 95% CI | suffix-present | recipient | clean | adjudicated fails |
|---|---|---|---|---|---|---|
| v19 (no labels) | +2 | (wide) | 42/47 | 18/27 | 159/159 | 36 |
| v53 + humanlabel x10 | +0 | [-7.14, +7.14] | 39/47 | 18/27 | 158/159 | 35 |
| **v53 + humanlabel x25** | **+3** | [-4.76, +10.32] | 40/47 | 19/27 | 157/159 | 35 |
| v53 + humanlabel x50 | +0 | [-7.94, +7.94] | 39/47 | 17/27 | 157/159 | 35 |

## Findings

1. **Real labels do NOT cause the suffix-present collapse.** Every synthetic-error-class model
   crashed suffix-present to 25/47; the human labels hold it at 39-40. Confirms the core
   diagnosis: real data does not poison the model, mined synthetic classes do.
2. **The movement is inside the noise.** Best cell is +3 on gold-2c with a CI including zero.
   Not an established improvement, only an absence of harm. 840 labels is too few to clear the bar.
3. **Weight 25 is the sweet spot; 50 overshoots** (recipient regresses -2 -> -4).
4. **The adjudicated failures are untouched** (still 35): batch 1 sampled low-confidence real-mail
   cases, which do not cover the S-BARRINGTON abbreviated-city class.

## Consequence

Batch 1 is a valid first increment that behaves exactly as the theory predicted, but it is not
enough to claim a fix or spend the gold-2b attempt. The path forward is batch 2 (2,380
class-targeted labels aimed at the failing buckets and the GitHub-issue classes), stacked on
batch 1, then re-measure per class.
