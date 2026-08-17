"""Minimal corpus: the abbreviated-city frame alone (V19-U3).

v19 beats the original on gold-2c's suffix-present class -- the commonest
shape in American mail -- and fails 36 human-adjudicated records, most of
them one class: cities written with an abbreviated leading word ("S
BARRINGTON", "LK ZURICH"). This emits that frame and nothing else.

The point is surgical. The full national corpus carries ~30 frames whose
combined effect measurably damaged suffix-present accuracy; this takes the
one frame that fixes a real, human-verified defect and leaves the rest out.
Whether it costs suffix-present accuracy is now checkable on gold-2c before
anything is trusted.

Usage: python training/build_minimal_abbrev.py
"""
import json, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import usaddress
from synth_error_classes import gen_abbrev_city, gen_true_post_directional

SEED = 20260823
OUT = Path(__file__).parent / "corpus" / "minimal_abbrev.jsonl"

def main():
    rng = random.Random(SEED)
    rows = []
    # The defect class itself.
    for r in gen_abbrev_city(rng, 24000):
        rows.append(dict(r, origin="min-abbrev_city"))
    # Its counterweight, at the ratio the adjudicated record set settled on
    # (v41-v43): without it the model over-applies the city reading to real
    # post-directionals, which is a different adjudicated class.
    for r in gen_true_post_directional(rng, 4500):
        rows.append(dict(r, origin="min-true_post_directional"))
    kept = 0
    with open(OUT, "w", encoding="utf-8") as f:
        for r in rows:
            if usaddress.tokenize(" ".join(r["tokens"])) != r["tokens"]:
                continue
            f.write(json.dumps(r) + "\n")
            kept += 1
    print(f"wrote {kept} rows -> {OUT}")

if __name__ == "__main__":
    main()
