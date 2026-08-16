"""Regenerate the README's confidence-vs-error numbers from committed artifacts.

For every human-adjudicated gold record whose approved label sequence is on
file (judged_labels, rounds 5+), run the default model's confidence path and
ask: did the parse match the human-approved labels, and how confident was its
weakest token? Reports mean weakest-token confidence for correct vs wrong
parses, the AUC of weakest-token confidence as a wrong-parse detector, and
the >0.99 precision tradeoff quoted in the README.

Usage: python benchmark/confidence_error_auc.py
"""

import json
from pathlib import Path

import fastaddress

ROOT = Path(__file__).parent.parent


def main():
    verd = json.loads((ROOT / "eval" / "gold" / "verdicts-merged.json").read_text(encoding="utf-8"))
    rows = []
    for raw, v in verd.items():
        judged = v.get("judged_labels")
        if not judged:
            continue
        triples = fastaddress.parse_with_confidence(raw)
        labels = [l for _, l, _ in triples]
        if len(labels) != len(judged):
            # A token-count mismatch is definitionally a wrong parse; counting it
            # any other way would bias the separation upward.
            rows.append((False, min((c for _, _, c in triples), default=0.0)))
            continue
        weakest = min(c for _, _, c in triples)
        rows.append((labels == judged, weakest))

    correct = [w for ok, w in rows if ok]
    wrong = [w for ok, w in rows if not ok]
    n_c, n_w = len(correct), len(wrong)
    if not n_c or not n_w:
        raise SystemExit(f"not enough data: {n_c} correct / {n_w} wrong")

    # AUC by pairwise comparison (exact, small n).
    wins = sum((c > w) + 0.5 * (c == w) for c in correct for w in wrong)
    auc = wins / (n_c * n_w)

    hi_c = sum(1 for c in correct if c > 0.99)
    hi_w = sum(1 for w in wrong if w > 0.99)
    print(f"records with approved labels: {len(rows)}  ({n_c} judged-correct parses, {n_w} judged-wrong)")
    print(f"mean weakest-token confidence  correct {sum(correct)/n_c:.3f}   wrong {sum(wrong)/n_w:.3f}")
    print(f"AUC (weakest token predicts wrong parse): {auc:.3f}")
    print(f"parses above 0.99 weakest-token: correct {hi_c} ({hi_c/n_c*100:.0f}%)   wrong {hi_w}")


if __name__ == "__main__":
    main()
